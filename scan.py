#!/usr/bin/env python3
import os
from pathlib import Path
from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.flac import FLAC
from mutagen.aiff import AIFF
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
from collections import defaultdict
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Default directory path for audio files
# AUDIO_DIR = 'path/to/your/audio/directory'  # Change this line to your specific path
AUDIO_DIR = '/Users/jacobleone/Documents/Music/Block Party'  # Change this line to your specific path

def get_format_specific_info(audio, file_type):
    """
    Extract format-specific metadata from audio file
    """
    try:
        if file_type == '.mp3':
            if isinstance(audio, MP3):
                return {
                    'bitrate': round(audio.info.bitrate / 1000, 2) if hasattr(audio.info, 'bitrate') else None,
                    'format': 'MP3'
                }
        elif file_type in ['.wav', '.wave']:
            if isinstance(audio, WAVE):
                return {
                    'bitrate': None,  # WAV doesn't have bitrate
                    'format': 'WAV'
                }
        elif file_type == '.flac':
            if isinstance(audio, FLAC):
                return {
                    'bitrate': None,  # FLAC is lossless
                    'format': 'FLAC'
                }
        elif file_type in ['.aif', '.aiff']:
            if isinstance(audio, AIFF):
                return {
                    'bitrate': None,  # AIFF doesn't have bitrate
                    'format': 'AIFF'
                }
        elif file_type == '.m4a':
            if isinstance(audio, MP4):
                return {
                    'bitrate': round(audio.info.bitrate / 1000, 2) if hasattr(audio.info, 'bitrate') else None,
                    'format': 'M4A'
                }
        elif file_type == '.ogg':
            if isinstance(audio, OggVorbis):
                return {
                    'bitrate': round(audio.info.bitrate / 1000, 2) if hasattr(audio.info, 'bitrate') else None,
                    'format': 'OGG'
                }
    except Exception as e:
        logger.warning(f"Error getting format-specific info: {str(e)}")
    return {'bitrate': None, 'format': None}

def get_audio_metadata(file_path):
    """
    Extract technical metadata from an audio file
    Returns a dictionary with relevant metadata for DJ equipment compatibility
    """
    try:
        # Try to load the file with mutagen
        audio = MutagenFile(file_path)
        if audio is None:
            logger.warning(f"Could not read file: {file_path}")
            return None

        file_type = file_path.suffix.lower()
        format_info = get_format_specific_info(audio, file_type)

        metadata = {
            'filename': file_path.name,
            'file_type': file_type,
            'file_size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2),
            'sample_rate': None,
            'bit_depth': None,
            'channels': None,
            'bitrate': format_info['bitrate'],
            'format': format_info['format']
        }

        # Extract basic audio properties
        if hasattr(audio, 'info'):
            if hasattr(audio.info, 'sample_rate'):
                metadata['sample_rate'] = audio.info.sample_rate
            if hasattr(audio.info, 'bits_per_sample'):
                metadata['bit_depth'] = audio.info.bits_per_sample
            elif hasattr(audio.info, 'bitdepth'):  # Some formats use different attribute names
                metadata['bit_depth'] = audio.info.bitdepth
            if hasattr(audio.info, 'channels'):
                metadata['channels'] = audio.info.channels
            elif hasattr(audio.info, 'nchannels'):  # Some formats use different attribute names
                metadata['channels'] = audio.info.nchannels

        return metadata
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
        return None

def generate_report(directory_path):
    """
    Generate a technical report of audio files in the directory
    """
    audio_files = []
    format_stats = defaultdict(int)
    sample_rate_stats = defaultdict(int)
    bit_depth_stats = defaultdict(int)
    channel_stats = defaultdict(int)
    error_files = []
    
    # Scan directory for audio files
    audio_extensions = {'.mp3', '.wav', '.wave', '.flac', '.aif', '.aiff', '.m4a', '.ogg'}
    for file_path in Path(directory_path).rglob('*'):
        if file_path.suffix.lower() in audio_extensions:
            try:
                metadata = get_audio_metadata(file_path)
                if metadata:
                    audio_files.append(metadata)
                    format_stats[metadata['file_type']] += 1
                    if metadata['sample_rate']:
                        sample_rate_stats[str(metadata['sample_rate'])] += 1
                    if metadata['bit_depth']:
                        bit_depth_stats[str(metadata['bit_depth'])] += 1
                    if metadata['channels']:
                        channel_stats[str(metadata['channels'])] += 1
                else:
                    error_files.append(str(file_path))
            except Exception as e:
                error_files.append(f"{file_path} (Error: {str(e)})")

    # Generate report
    report = []
    report.append("=== Audio Files Technical Report ===\n")
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Directory scanned: {directory_path}")
    report.append(f"Total audio files found: {len(audio_files)}")
    if error_files:
        report.append(f"Files with errors: {len(error_files)}\n")
    else:
        report.append("All files processed successfully.\n")

    # Summary Statistics
    report.append("=== Summary Statistics ===\n")
    report.append("File Types:")
    for fmt, count in format_stats.items():
        report.append(f"  {fmt}: {count} files")
    
    report.append("\nSample Rates:")
    for rate, count in sample_rate_stats.items():
        report.append(f"  {rate} Hz: {count} files")
    
    report.append("\nBit Depths:")
    for depth, count in bit_depth_stats.items():
        report.append(f"  {depth} bits: {count} files")
    
    report.append("\nChannel Configurations:")
    for channels, count in channel_stats.items():
        report.append(f"  {channels} channels: {count} files")

    # Detailed File Information
    report.append("\n=== Detailed File Information ===\n")
    for metadata in audio_files:
        report.append(f"File: {metadata['filename']}")
        report.append(f"  Type: {metadata['file_type']}")
        report.append(f"  Format: {metadata['format'] or 'N/A'}")
        report.append(f"  Size: {metadata['file_size_mb']} MB")
        report.append(f"  Sample Rate: {metadata['sample_rate']} Hz")
        report.append(f"  Bit Depth: {metadata['bit_depth']} bits")
        report.append(f"  Channels: {metadata['channels']}")
        if metadata['bitrate']:
            report.append(f"  Bitrate: {metadata['bitrate']} kbps")
        report.append("")

    # Error Report
    if error_files:
        report.append("\n=== Files with Errors ===\n")
        for error_file in error_files:
            report.append(f"- {error_file}")

    return "\n".join(report)

def main():
    # Check if the default directory exists
    if not os.path.exists(AUDIO_DIR):
        logger.error(f"Error: Directory '{AUDIO_DIR}' does not exist.")
        logger.error("Please update the AUDIO_DIR variable in scan.py with your audio directory path.")
        return

    logger.info(f"Scanning directory: {AUDIO_DIR}")
    report = generate_report(AUDIO_DIR)
    
    output_file = 'audio_metadata_report.txt'
    with open(output_file, 'w') as f:
        f.write(report)
    
    logger.info(f"Report generated successfully: {output_file}")

if __name__ == "__main__":
    main()
