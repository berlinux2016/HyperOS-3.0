# ![logo](HyperOS.png)

## ⚠️ Archivierungshinweis / Archive Notice

**Dieses Repository wird nicht mehr aktiv entwickelt und wird archiviert.**

**This repository is no longer actively maintained and will be archived.**

---

# Xiaomi HyperOS 3.0 - German Translation on Xiaomi.eu

[![GitHub issues](https://img.shields.io/github/issues-raw/berlinux2016/MIUI15.svg)](https://github.com/berlinux2016/HyperOS-3.0/issues "GitHub issues")

## Introduction

This repository contains the German translation of the Xiaomi HyperOS 3.0 Beta/Stable ROM releases from [xiaomi.eu](https://xiaomi.eu/community/forums/miui-rom-releases.103/) and possibly other HyperOS custom ROMs.

All strings were translated by the community - special thanks go to:

Sorted by [activity](https://github.com/berlinux2016/HyperOS-3.0/graphs/contributors)

MeiGuddet, Henry2o1o, WorXeN, ingbrzy, berlinux2016, ScratchBuild, malchik-solnce, pareh, lynx7, cp82, energY8989, BodoTh, aaf-caliban, EdlerProgrammierer, ReeCorDs, Syrrr, FireEmerald, he-leon, danielchc, vivanco-vivanco, darosto


🛠 Automated Translation & Repair Tool

I have developed a robust Python script to assist with translating new XML files and fixing common syntax errors that cause bootloops.

Features of the Master Script:

Anti-Bootloop Protection: Automatically blocks translation of technical strings (e.g., SVG paths, m3_ tokens, cubic-bezier animations).

Format Repair: Fixes broken format specifiers (e.g., %D instead of %d or BIN instead of AM).

Safe Translation: Only translates missing strings that are identical to the English original, preserving existing manual translations.

Automatic Backups: Creates backups before modifying any file.

Prerequisites

You need Python 3 installed. Install the required dependency:

pip install deep-translator


🌍 How to adapt for other languages (Spanish, Italian, etc.)

This script is configured for German (de) by default. If you want to use it for another language (e.g., Spanish or Italian), simply edit the configuration section at the top of the script:

PATH_DE: Point this to your repository folder (e.g., ./Spanish/main).

PATH_EN: Point this to the unzipped English original APK sources.

TARGET_LANG: Change 'de' to your target language code (e.g., 'es', 'it', 'fr', 'pl').

IGNORE_TERMS: Add or remove words that should remain in English for your specific language.

Download from this Repo the translate.py Script.


## Reporting issues

Use the [Github Issue tracker](https://github.com/berlinux2016/HyperOS-3.0/issues) to report a bug or the following [forum thread](https://xiaomi.eu/community/forums/german-translation.8/).


## Submitting fixes

Fixes are submitted as pull request via Github.

- Fork the repository.
- Make the fix.
- Submit a pull request to the project owner.

Check [Contributing to a project](https://guides.github.com/activities/forking) for further informations.
