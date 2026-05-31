# DuplicateFinder

A lightweight Windows desktop application for detecting and managing duplicate files using PyQt6.

## Features

### Core Functionality

- **Duplicate Detection**: SHA-256 hash, filename, hash + filename, hash OR filename, or content OR filename
- **Multi-folder Scanning**: Select one or multiple directories with optional recursion
- **Duplicate Grouping**: View duplicates grouped by detection method with file metadata (size, date, path)
- **Manual Selection**: Select which duplicates to action on
- **File Operations**:
  - Delete to recycle bin (send2trash)
  - Rename
  - Move
  - Open file location (File Explorer)
  - Copy path to clipboard
- **Search & Filtering**: Real-time filter by filename or path
- **Column Sorting**: Click headers to sort results
- **Export**: CSV export of results
- **Storage Recovery**: Display recoverable disk space in status bar
- **Dark/Light Theme**: Toggle with persistent storage
- **Preferences**: Auto-save theme, last scanned folders, scan mode, recursion setting, window geometry

## Requirements

- Windows 10+
- Python 3.10+

## Installation

### From Source

```bash
pip install -r requirements.txt
python duplicate_finder/main.py
```

### As Executable

```bash
cd duplicate_finder
pyinstaller --onedir --windowed --icon=resources/app_icon.png --splash=resources/app_icon.png --name=DuplicateFinder --add-data="resources:resources" main.py
```

Executable will be in `dist/DuplicateFinder/`.

## Architecture

```
duplicate_finder/
├── main.py                 # Application entry point
├── config.py               # Configuration constants
├── models/                 # Data models
│   ├── scanner.py         # File scanning logic
│   ├── file_entry.py      # File data structure
│   └── preferences.py     # Settings persistence
├── views/                 # UI components
│   ├── main_window.py     # Main window container
│   ├── topbar.py          # Top toolbar
│   ├── sidebar.py         # Left sidebar (folder selection)
│   ├── statusbar.py       # Bottom status bar
│   ├── scan_view.py       # Scan controls
│   └── results_view.py    # Results table
├── controllers/           # Business logic
│   ├── scan_controller.py # Scan orchestration
│   └── file_controller.py # File operations
├── resources/             # Assets
│   ├── styles.qss        # Qt stylesheets
│   └── app_icon.png      # Application icon
└── utils/
    └── helpers.py        # Utility functions
```

## Technology Stack

- **Framework**: PyQt6
- **UI Style**: Fusion + QSS (flat design, no rounded corners)
- **Storage**: preferences.json (ephemeral analysis, no database)
- **Windows Integration**: send2trash, pathlib
