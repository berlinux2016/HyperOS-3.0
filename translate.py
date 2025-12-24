import os
import re
import shutil
import time
import sys
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator

# --- CONFIGURATION -----------------------------------------------------------

# Path to your translation repository (Target Language)
# Example: "/home/user/GitHub/HyperOS-3.0/German/main"
PATH_TARGET = "./path/to/your/repo/German/main"

# Path to the original English source files (Source Language)
# Example: "/home/user/MIUI/orig"
PATH_ORIGIN = "./path/to/original/English/source"

# Target Language Code for Google Translate (de, es, it, fr, etc.)
TARGET_LANG = 'de'

# Tuning
BATCH_SIZE = 20
WAIT_TIME = 0.5

# --- SECURITY FILTERS (DO NOT CHANGE) ----------------------------------------

# 1. Keys: If the XML key contains these, it will NOT be translated (Technical)
FORBIDDEN_KEY_PARTIALS = (
    "config_", "m3_", "abc_", "font_", "typeface", "coordinate", 
    "path", "vector", "data", "geometry", "anim", "interpolator", 
    "transition", "layout", "dimen", "color", "style", "attr", 
    "id", "action_", "key_", "value_", "provider", "package", 
    "passport", "weixin", "wechat"
)

# 2. Content: If the text contains these, it will NOT be translated (Crash Risk)
FORBIDDEN_CONTENT_TERMS = (
    "sans-serif", "serif", "monospace", "cubic-bezier", "path(", 
    "@string/", "@color/", "@dimen/", "@drawable/", "@style/", "@id/",
    "http://", "https://", "www.", ".com", ".xml", ".png", ".jpg",
    "remix", "roto", "lato", "misans", "arial", "miui-",
    "true", "false", "visible", "gone", "invisible", "fill_parent", "match_parent"
)

# 3. Ignore List: Words that are usually identical in English and Target Language
IGNORE_TERMS = {
    "ok", "cancel", "yes", "no", "on", "off", "auto", "xiaomi", "redmi", "poco",
    "miui", "mi", "android", "google", "bluetooth", "wifi", "wi-fi", "wlan",
    "gps", "nfc", "usb", "vpn", "sim", "esim", "sd", "hd", "fhd", "4k", "8k",
    "lte", "5g", "4g", "3g", "2g", "sos", "cpu", "gpu", "ram", "rom", "led",
    "oled", "amoled", "lcd", "imei", "pin", "puk", "apn", "hz", "mah", "gb", 
    "mb", "kb", "app", "apps", "backup", "cloud", "service", "services", 
    "pro", "ultra", "lite", "max", "min", "plus", "none", "null", "default",
    "music", "video", "camera", "update", "download", "install", "error",
    "am", "pm" 
}

def load_xml_dict(path):
    """Safely loads XML content into a dictionary."""
    data = {}
    if not os.path.exists(path): return data
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        for s in root.findall('string'):
            name = s.get('name')
            text = s.text
            if name: 
                data[name] = text if text else ""
    except: pass
    return data

def is_safe_to_translate(key, text):
    """Strict security check. Returns True if safe to translate."""
    if not text: return False
    
    clean_text = text.strip()
    clean_key = key.lower()
    clean_val_lower = clean_text.lower()

    # 1. Check technical keys
    for bad_key in FORBIDDEN_KEY_PARTIALS:
        if bad_key in clean_key: return False
    
    # 2. Check technical content
    for term in FORBIDDEN_CONTENT_TERMS:
        if term in clean_val_lower: return False

    # 3. Check for SVG Paths (e.g. M 3,5 L 20,20)
    if re.match(r'^[MmLlHhVvCcSsQqTtAaZz]\s*[\d\.\,\-]', clean_text): return False
    
    # 4. Check for pure numbers/coordinates
    allowed_chars = set("0123456789., -:[](){}")
    if set(clean_text).issubset(allowed_chars): return False

    # 5. Check for snake_case IDs
    if "_" in clean_text and " " not in clean_text: return False

    # 6. Check ignore list
    if clean_val_lower in IGNORE_TERMS: return False
    
    # 7. Check AM/PM
    if clean_text in ["AM", "PM"]: return False

    return True

def get_needed_fix(key, original_en, current_target):
    """Detects and fixes common translation errors (BIN instead of AM, etc.)"""
    stripped_en = original_en.strip()
    stripped_target = current_target.strip()

    # FIX 1: AM/PM -> BIN/PN (Common Google Translate Error)
    if stripped_en == "AM" and stripped_target != "AM": return "AM"
    if stripped_en == "PM" and stripped_target != "PM": return "PM"

    # FIX 2: Restore capitalization for technical IDs (e.g. passport_weixin)
    if "_" in stripped_en and " " not in stripped_en:
        if stripped_target != stripped_en: return stripped_en

    # FIX 3: Restore broken percentage formatting (%d -> %D causes crash)
    if "%d" in original_en and "%D" in current_target: return original_en

    # FIX 4: Replace German quotes with standard quotes (Target language specific)
    if TARGET_LANG == 'de':
        if "„" in current_target or "“" in current_target:
            return current_target.replace("„", '"').replace("“", '"')

    return None

def validate_translation(original, translated):
    """Post-translation safety check."""
    if not translated: return False
    # Check if variables like %s, %1$d are preserved
    patterns = re.findall(r'%(\d+\$)?([sdcxbgofe%])', original)
    for pat in patterns:
        token = f"%{pat[0]}{pat[1]}"
        # Allow slight spacing variations during check, fixed in clean_translation
        if token not in translated and token.replace("$", " $ ") not in translated:
            return False
    return True

def clean_translation(text):
    """Cleans up translation artifacts."""
    t = text
    if TARGET_LANG == 'de':
        t = t.replace("„", '"').replace("“", '"')
    t = t.replace("&", "&amp;").replace("<", "&lt;")
    # Fix spaces inside variables introduced by translator (% 1 $ s -> %1$s)
    t = re.sub(r'%\s+(\d+)\s+\$\s+([sd])', r'%\1$\2', t)
    t = re.sub(r'%\s+([sd])', r'%\1', t)
    t = t.replace("... ", "...")
    return t

def main():
    print("--- HYPEROS TRANSLATION MASTER SCRIPT ---")
    print(f"Target: {PATH_TARGET}")
    print(f"Language: {TARGET_LANG}")
    print("-" * 40)

    translator = GoogleTranslator(source='auto', target=TARGET_LANG)
    files_modified = 0
    total_fixes = 0
    total_translations = 0

    for apk_folder in sorted(os.listdir(PATH_TARGET)):
        # Determine target values folder (e.g., values-de, values-es)
        values_dir = f"values-{TARGET_LANG}" if TARGET_LANG != "en" else "values"
        
        target_xml_path = os.path.join(PATH_TARGET, apk_folder, f"res/{values_dir}/strings.xml")
        origin_xml_path = os.path.join(PATH_ORIGIN, apk_folder, "res/values/strings.xml")

        if os.path.exists(target_xml_path) and os.path.exists(origin_xml_path):
            target_data = load_xml_dict(target_xml_path)
            origin_data = load_xml_dict(origin_xml_path)
            
            updates_map = {}
            to_translate_map = {}

            for key, val_target in target_data.items():
                if key in origin_data:
                    val_origin = origin_data[key]
                    
                    # 1. Check for needed repairs
                    fix = get_needed_fix(key, val_origin, val_target)
                    if fix:
                        updates_map[key] = clean_translation(fix)
                    
                    # 2. Check for missing translations (if target == origin)
                    elif val_target == val_origin:
                        if is_safe_to_translate(key, val_origin):
                            to_translate_map[key] = val_origin

            if updates_map or to_translate_map:
                print(f"[{apk_folder}] Fixes: {len(updates_map)} | Translate: {len(to_translate_map)}")

            # Execute Translations (Batch)
            if to_translate_map:
                keys_list = list(to_translate_map.keys())
                texts_list = list(to_translate_map.values())
                
                for i in range(0, len(keys_list), BATCH_SIZE):
                    batch_keys = keys_list[i:i+BATCH_SIZE]
                    batch_texts = texts_list[i:i+BATCH_SIZE]
                    try:
                        results = translator.translate_batch(batch_texts)
                        for k, res in enumerate(results):
                            orig = batch_texts[k]
                            trans = res
                            key_name = batch_keys[k]
                            if trans and trans != orig:
                                cleaned_trans = clean_translation(trans)
                                if validate_translation(orig, cleaned_trans):
                                    updates_map[key_name] = cleaned_trans
                                    total_translations += 1
                        time.sleep(WAIT_TIME)
                        sys.stdout.write(f"\r  -> Progress: {i+len(batch_texts)}/{len(keys_list)}")
                        sys.stdout.flush()
                    except Exception as e:
                        print(f"\n  [WARNING] API Error: {e}")
                        time.sleep(5)
                print("")

            # Write changes to file
            if updates_map:
                try:
                    # Create Backup
                    if not os.path.exists(target_xml_path + ".bak"):
                        shutil.copy2(target_xml_path, target_xml_path + ".bak")
                    
                    with open(target_xml_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    def replace_func(match):
                        full_tag = match.group(1)
                        key = match.group(2)
                        end_tag = match.group(4)
                        if key in updates_map:
                            return f'{full_tag}{updates_map[key]}{end_tag}'
                        return match.group(0)

                    new_content = re.sub(
                        r'(<string\s+name=["\'](.*?)["\'].*?>)(.*?)(</string>)', 
                        replace_func, content, flags=re.DOTALL
                    )

                    with open(target_xml_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    
                    files_modified += 1
                    total_fixes += len(updates_map)

                except Exception as e:
                    print(f"  [ERROR] {e}")

    print("-" * 40)
    print(f"DONE! Files modified: {files_modified}, Total changes: {total_fixes}")

if __name__ == "__main__":
    main()