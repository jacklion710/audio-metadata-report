# Audio Metadata Report Generator

Scans a directory of audio files and generates a technical report focusing on DJ equipment compatibility. The report includes information about file types, sample rates, bit depths, and channel configurations.

## Features

- Scans for common audio formats (MP3, WAV, FLAC, AIF/AIFF, M4A, OGG)
- Reports technical specifications relevant for DJ equipment
- Generates summary statistics and detailed file information
- Focuses on format compatibility with CDJs and other DJ equipment

## Installation

1. Clone the repository to your workspace:
```bash
git clone https://github.com/jacklion710/audio-metadata-report
cd audio-metadata-report
```

2. Install the required dependency:
```bash
pip install mutagen
```

## Usage

1. Open `scan.py` and update the `AUDIO_DIR` variable with your audio directory path:
```python
AUDIO_DIR = 'path/to/your/audio/directory'  # Change this line to your specific path
```

2. Run the script:
```bash
python scan.py
```

3. View the generated report:
```bash
cat audio_metadata_report.txt
```

## Report Contents

The generated report includes:
- Summary statistics for file types, sample rates, bit depths, and channel configurations
- Detailed technical information for each audio file
- File size and format specifications
- Compatibility-relevant metadata

## Requirements

- Python 3.x
- mutagen library

