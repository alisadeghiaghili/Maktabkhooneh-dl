# Changelog

All notable changes to this project will be documented in this file.

## [2.0] - 2026-06-28

### Changed
- Migrated from Selenium + geckodriver to **Playwright** (Chromium)
- Rewrote entire script: cleaner structure, single file, no package dependency
- Moved `input()` and all settings inside `main()` — no more module-level side effects
- Added `None` guard on `lesson_href` to prevent crash on missing links
- Added `try/except` around `wait_for_selector` for download button — skips lesson instead of crashing
- Added `[SKIP]` and `[INFO]` log messages for better visibility
- Removed hardcoded `COURSE_URL` at module level

### Removed
- Removed v1 Selenium-based package (`maktabkhooneh/` directory)
- Removed geckodriver dependency
- Removed duplicate `requirements.txt`, `README.md`, `changelog.txt`

### Renamed
- `maktabkhooneh-dl-v2.py` → `maktabkhooneh_dl.py`
- `requirements-v2.txt` → `requirements.txt`
- `README-v2.md` → `README.md`
- `changelog.txt` → `CHANGELOG.md`

---

## [1.0] - 2025-09-12

### Added
- Introduced `dataclass` structures for course and downloader configuration

### Changed
- Enhanced table rendering with live streaming display for real-time row updates

---

## [0.9] - 2025-08-26

### Changed
- Unified downloader into a single script with user-selectable options for wget, curl, axel, and aria2c

## [0.8] - 2025-08-26

### Added
- Introduced separate downloader scripts for wget, curl, and axel

## [0.7] - 2025-08-25

### Changed
- Improved progress bar for smoother and clearer updates

## [0.6] - 2025-08-25

### Fixed
- Compatibility issues with the latest Maktabkhooneh website update
