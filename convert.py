import os
import subprocess
from pathlib import Path
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_ffmpeg():
    """Check if ffmpeg is installed and accessible"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("ffmpeg is not installed or not accessible in your system PATH.")
        logger.error("Please install ffmpeg to use this script:")
        logger.error("- macOS: brew install ffmpeg")
        logger.error("- Ubuntu/Debian: sudo apt-get install ffmpeg")
        logger.error("- Windows: Download from https://ffmpeg.org/download.html")
        return False

# Default directory path for audio files
# AUDIO_DIR = 'path/to/your/audio/directory'  # Change this line to your specific path
AUDIO_DIR = '/Users/jacobleone/Documents/Music/Block Party'  # Change this line to your specific path

# CDJ Compatibility Requirements
CDJ_REQUIREMENTS = {
    'wav': {
        'sample_rates': [44100, 48000],
        'bit_depths': [16, 24],
        'channels': [2],  # Stereo
        'bitrate': None  # Not applicable for WAV
    },
    'mp3': {
        'sample_rates': [44100],
        'bit_depths': None,  # Not applicable for MP3
        'channels': [2],  # Stereo
        'bitrate': (32, 320)  # Min and max kbps
    },
    'aiff': {
        'sample_rates': [44100, 48000],
        'bit_depths': [16, 24],
        'channels': [2],  # Stereo
        'bitrate': None  # Not applicable for AIFF
    },
    'flac': {
        'sample_rates': [44100, 48000],
        'bit_depths': [16, 24],
        'channels': [2],  # Stereo
        'bitrate': None  # Not applicable for FLAC
    },
    'm4a': {
        'sample_rates': [44100, 48000],
        'bit_depths': None,  # Not applicable for M4A
        'channels': [2],  # Stereo
        'bitrate': (256, None)  # Min kbps, no max
    }
}

def get_conversion_params(metadata):
    """
    Determine the conversion parameters needed for CDJ compatibility
    Returns a tuple of (output_format, ffmpeg_params)
    """
    file_type = metadata['file_type'].lstrip('.')
    params = []
    
    # Map file types to their CDJ requirement keys
    format_map = {
        'aif': 'aiff',  # Map 'aif' to 'aiff' for CDJ requirements
        'wav': 'wav',
        'mp3': 'mp3',
        'flac': 'flac',
        'm4a': 'm4a'
    }
    
    # Get the CDJ requirement key for this file type
    cdj_key = format_map.get(file_type, 'wav')  # Default to 'wav' for unsupported formats
    
    # Determine target format based on current format
    if file_type in ['wav', 'aif', 'aiff']:
        # For WAV/AIFF, keep the same format but adjust bit depth
        target_format = 'wav' if file_type == 'wav' else 'aiff'  # Convert 'aif' to 'aiff'
        if metadata['bit_depth'] not in CDJ_REQUIREMENTS[cdj_key]['bit_depths']:
            params.extend(['-acodec', 'pcm_s24le'])  # Convert to 24-bit
    elif file_type == 'flac':
        # For FLAC, keep FLAC but adjust bit depth
        target_format = 'flac'
        if metadata['bit_depth'] not in CDJ_REQUIREMENTS[cdj_key]['bit_depths']:
            params.extend(['-acodec', 'flac'])
    elif file_type == 'mp3':
        # For MP3, keep MP3 but adjust bitrate
        target_format = 'mp3'
        if metadata['bitrate'] and metadata['bitrate'] < 320:
            params.extend(['-acodec', 'libmp3lame', '-b:a', '320k'])
    elif file_type == 'm4a':
        # For M4A, keep M4A but adjust bitrate
        target_format = 'm4a'
        if metadata['bitrate'] and metadata['bitrate'] < 256:
            params.extend(['-acodec', 'aac', '-b:a', '256k'])
    else:
        # For unsupported formats, convert to WAV
        target_format = 'wav'
        params.extend(['-acodec', 'pcm_s24le'])
    
    # Adjust sample rate if needed
    if metadata['sample_rate'] not in CDJ_REQUIREMENTS[cdj_key]['sample_rates']:
        params.extend(['-ar', '44100'])  # Convert to 44.1kHz
    
    # Ensure stereo output
    if metadata['channels'] != 2:
        params.extend(['-ac', '2'])
    
    return target_format, params

def convert_file(input_path, output_path, ffmpeg_params):
    """
    Convert an audio file using ffmpeg
    Returns True if successful, False otherwise
    """
    try:
        cmd = ['ffmpeg', '-i', str(input_path), '-y'] + ffmpeg_params + [str(output_path)]
        logger.info(f"Running ffmpeg command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Successfully converted: {input_path.name}")
            return True
        else:
            logger.error(f"Error converting {input_path.name}: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error converting {input_path.name}: {str(e)}")
        return False

def process_directory(directory_path):
    """
    Process all audio files in the directory and convert incompatible ones
    """
    if not check_ffmpeg():
        return
    
    # Create converted files directory in the root of the repository
    converted_dir = Path.cwd() / 'converted'
    converted_dir.mkdir(exist_ok=True)
    logger.info(f"Created/verified converted directory at: {converted_dir}")
    
    # Load metadata from the report
    try:
        with open('audio_metadata_report.txt', 'r') as f:
            report_content = f.read()
    except FileNotFoundError:
        logger.error("audio_metadata_report.txt not found. Please run scan.py first.")
        return
    
    # Process each file
    audio_files = []
    current_file = None
    current_metadata = {}
    
    for line in report_content.split('\n'):
        if line.startswith('File: '):
            if current_metadata:
                audio_files.append(current_metadata)
            current_file = line[6:].strip()
            current_metadata = {'filename': current_file}
        elif line.startswith('  Type: '):
            current_metadata['file_type'] = line[8:].strip()
        elif line.startswith('  Sample Rate: '):
            try:
                current_metadata['sample_rate'] = int(line[14:].split()[0])
            except (ValueError, IndexError):
                current_metadata['sample_rate'] = None
        elif line.startswith('  Bit Depth: '):
            try:
                value = line[12:].split()[0]
                current_metadata['bit_depth'] = None if value == 'None' else int(value)
            except (ValueError, IndexError):
                current_metadata['bit_depth'] = None
        elif line.startswith('  Channels: '):
            try:
                current_metadata['channels'] = int(line[11:].strip())
            except (ValueError, IndexError):
                current_metadata['channels'] = None
        elif line.startswith('  Bitrate: '):
            try:
                value = line[10:].split()[0]
                current_metadata['bitrate'] = None if value == 'None' else float(value)
            except (ValueError, IndexError):
                current_metadata['bitrate'] = None
        elif line.startswith('  CDJ Compatible: '):
            current_metadata['is_compatible'] = line[17:].strip() == 'Yes'
    
    if current_metadata:
        audio_files.append(current_metadata)
    
    # Process incompatible files
    incompatible_files = [f for f in audio_files if not f.get('is_compatible', True)]
    
    if not incompatible_files:
        logger.info("No incompatible files found. All files are CDJ-compatible.")
        return
    
    logger.info(f"Found {len(incompatible_files)} incompatible files to convert.")
    
    for metadata in incompatible_files:
        input_path = Path(directory_path) / metadata['filename']
        if not input_path.exists():
            logger.warning(f"File not found: {metadata['filename']}")
            continue
        
        # Determine conversion parameters
        target_format, ffmpeg_params = get_conversion_params(metadata)
        
        # Create output path
        output_filename = input_path.stem + '.' + target_format
        output_path = converted_dir / output_filename
        
        logger.info(f"Converting {input_path} to {output_path}")
        
        # Convert file
        if convert_file(input_path, output_path, ffmpeg_params):
            logger.info(f"Successfully converted {metadata['filename']} to {output_filename}")
            # Verify the file was created
            if output_path.exists():
                logger.info(f"Verified converted file exists at: {output_path}")
            else:
                logger.error(f"Converted file not found at: {output_path}")
        else:
            logger.error(f"Failed to convert {metadata['filename']}")

def main():
    # Check if the default directory exists
    if not os.path.exists(AUDIO_DIR):
        logger.error(f"Error: Directory '{AUDIO_DIR}' does not exist.")
        logger.error("Please update the AUDIO_DIR variable in convert.py with your audio directory path.")
        return
    
    logger.info(f"Processing directory: {AUDIO_DIR}")
    process_directory(AUDIO_DIR)
    logger.info("Conversion process completed.")

if __name__ == "__main__":
    main() 