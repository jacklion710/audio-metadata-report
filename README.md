# Audio Metadata Report Generator

Scans a directory of audio files and generates a technical report focusing on DJ equipment compatibility. The report includes information about file types, sample rates, bit depths, and channel configurations, with specific checks for CDJ compatibility.

## Features

- Scans for common audio formats (MP3, WAV, FLAC, AIF/AIFF, M4A, OGG)
- Reports technical specifications relevant for DJ equipment
- Generates summary statistics and detailed file information
- Checks CDJ compatibility requirements:
  - WAV: 44.1kHz/48kHz, 16/24-bit, stereo
  - MP3: 44.1kHz, 32-320kbps, stereo
  - AIFF: 44.1kHz/48kHz, 16/24-bit, stereo
  - FLAC: 44.1kHz/48kHz, 16/24-bit, stereo
  - M4A: 44.1kHz/48kHz, 256kbps or higher, stereo
- Provides detailed compatibility issues for each file
- Generates overall compatibility statistics
- Handles various audio formats and metadata structures
- Robust error handling and reporting
- Automatic conversion of incompatible files to CDJ-compatible formats
- Stores converted files in a separate directory
- Maintains original format when possible while adjusting technical specifications

## Installation

1. Clone the repository to your workspace:
```bash
git clone https://github.com/jacklion710/audio-metadata-report
cd audio-metadata-report
```

2. Install the required dependencies:
```bash
pip install mutagen
```

3. Install ffmpeg (required for audio conversion):
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt-get install ffmpeg`
- Windows: Download from https://ffmpeg.org/download.html

## Usage

1. Open `scan.py` and update the `AUDIO_DIR` variable with your audio directory path:
```python
AUDIO_DIR = 'path/to/your/audio/directory'  # Change this line to your specific path
```

2. Run the scan script to generate a report:
```bash
python scan.py
```

3. View the generated report:
```bash
cat audio_metadata_report.txt
```

4. Run the conversion script to convert incompatible files:
```bash
python convert.py
```

The conversion script will:
- Convert incompatible files to CDJ-compatible formats in a `converted` directory
- Maintain the original format when possible while adjusting technical specifications
- Log all conversion operations and any errors

## Directory Structure

```
audio-metadata-report/
├── scan.py                 # Script to scan audio files and generate report
├── convert.py             # Script to convert incompatible files
├── audio_metadata_report.txt  # Generated report file
├── converted/             # Directory containing converted files
└── README.md             # This file
```

## Report Contents

The generated report includes:

### CDJ Compatibility Summary
- Number of compatible files
- Number of incompatible files
- Overall compatibility rate

### Summary Statistics
- Distribution of file types
- Distribution of sample rates
- Distribution of bit depths
- Distribution of channel configurations

### Detailed File Information
For each audio file:
- File name and type
- Format details
- File size
- Technical specifications:
  - Sample rate
  - Bit depth
  - Channel configuration
  - Bitrate (for lossy formats)
- CDJ compatibility status
- Specific compatibility issues (if any)

### Error Report
- List of files that couldn't be processed
- Error messages and details

## Requirements

- Python 3.x
- mutagen library
- ffmpeg (for audio conversion)

## Supported CDJ Models

The compatibility requirements are based on the following CDJ models:
- Pioneer CDJ-3000
- Pioneer CDJ-2000NXS2
- Pioneer CDJ-2000NXS

## Notes

- The script checks for compatibility with the most common CDJ requirements
- Some older CDJ models may have different requirements
- Always verify compatibility with your specific CDJ model
- For best results, use WAV or AIFF formats at 44.1kHz/16-bit
- Converted files are placed in a separate `converted` directory
- The conversion process maintains the highest possible quality while ensuring compatibility
- Original files remain unchanged in their source directory

