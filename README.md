# audio-automation-utils

Small Python utilities for audio workflow organization and repetitive task automation.

Built for people who work with large collections of audio files, measurement exports, and project folders — and spend too much time doing things manually.

## Features

- **Folder inventory export** — scan any directory and export a CSV listing of all files (name, size, extension, modified date)
- **Batch file rename** — apply prefix, suffix, or sequential numbering to files matching a pattern; includes dry-run mode so nothing changes until you're sure

## Why this exists

Managing measurement sessions, project exports, and archive folders means constantly renaming files and building inventories by hand. These two commands cover the most repetitive parts.

## Requirements

Python 3.8+. No external dependencies — standard library only.

## Quick start

```bash
git clone https://github.com/niccolocervellati-cyber/audio-automation-utils.git
cd audio-automation-utils
python src/audio_automation_utils.py --help
```

## Usage

### Export folder inventory to CSV

```bash
python src/audio_automation_utils.py inventory /path/to/folder --output inventory.csv
```

### Batch rename with dry-run

```bash
# Preview changes (nothing is modified)
python src/audio_automation_utils.py rename /path/to/folder --prefix "session01_" --ext .wav --dry-run

# Apply
python src/audio_automation_utils.py rename /path/to/folder --prefix "session01_" --ext .wav
```

### Sequential numbering

```bash
python src/audio_automation_utils.py rename /path/to/folder --number --ext .txt --dry-run
```

## License

MIT
