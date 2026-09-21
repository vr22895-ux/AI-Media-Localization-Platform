import os
import subprocess
import logging
from typing import Optional

# 1. Setup Logging
# We use Python's built-in logging instead of 'print' statements.
# This ensures every event has a timestamp, which is crucial for tracking how long 
# each module takes (you'll need these timings for your research paper!).
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AudioExtractor:
    """
    Extracts audio from video files and converts it to a standard format
    (16kHz, 16-bit PCM, mono) optimized for speech recognition and diarization models.
    """
    
    def __init__(self, target_sample_rate: int = 16000, target_channels: int = 1):
        # We store the required audio specs as class properties.
        # 16000 Hz and 1 channel (mono) are the exact formats Whisper and Pyannote expect.
        self.target_sample_rate = target_sample_rate
        self.target_channels = target_channels
        
        # As soon as this class is initialized, check if FFmpeg actually exists on the system.
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Verify that ffmpeg is installed and accessible in the system PATH."""
        try:
            # We run 'ffmpeg -version' in the background silently (DEVNULL hides the output).
            # 'check=True' forces Python to throw an error if the command fails.
            subprocess.run(
                ["ffmpeg", "-version"], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL, 
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # If FFmpeg isn't installed or configured, stop the entire program immediately.
            raise RuntimeError("FFmpeg is not installed or not found in the system PATH. Please install FFmpeg.")

    def extract(self, video_path: str, output_audio_path: str) -> Optional[str]:
        """
        Extract audio from the given video file.
        
        Args:
            video_path (str): Path to the source video file (e.g., 'data/input.mp4').
            output_audio_path (str): Path where the extracted .wav file should be saved.
            
        Returns:
            str: Path to the extracted audio file, or None if extraction failed.
        """
        
        # 1. Validation: Check if the video file actually exists before we try to process it
        if not os.path.exists(video_path):
            logger.error(f"Source video not found: {video_path}")
            return None

        # 2. Preparation: Create the output directory if it doesn't exist yet
        # os.path.dirname gets the folder path from the full file path.
        os.makedirs(os.path.dirname(output_audio_path) or ".", exist_ok=True)

        logger.info(f"Extracting audio from {os.path.basename(video_path)}...")
        
        # 3. The FFmpeg Command: This is the core logic
        # We build the command as a list of strings, which is safer than one long string.
        command = [
            "ffmpeg",
            "-y",                     # Overwrite output files without asking for confirmation
            "-i", video_path,         # Specify the input video file
            "-vn",                    # Strip away the video track entirely (speeds up extraction)
            "-acodec", "pcm_s16le",   # Set Audio Codec to Pulse-Code Modulation, 16-bit, Little Endian (WAV format)
            "-ar", str(self.target_sample_rate), # Set Audio Sample Rate to 16000 Hz
            "-ac", str(self.target_channels),    # Set Audio Channels to 1 (Mono)
            output_audio_path         # Specify where to save the final file
        ]

        try:
            # 4. Execution: Run the FFmpeg command
            # We capture standard output (stdout) and standard error (stderr) so we can see what went wrong if it crashes.
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # If returncode is not 0, FFmpeg encountered a fatal error
            if result.returncode != 0:
                logger.error(f"FFmpeg failed with error code {result.returncode}")
                logger.error(f"FFmpeg Error Output: {result.stderr}")
                return None
                
            logger.info(f"Audio extracted successfully to {output_audio_path}")
            return output_audio_path
            
        except Exception as e:
            # Catch any unexpected Python errors (like running out of memory)
            logger.error(f"An unexpected error occurred during audio extraction: {str(e)}")
            return None

# 5. Quick Testing Block
# This code only runs if you execute this file directly in the terminal
if __name__ == "__main__":
    import sys
    # Check if the user provided an input and output path in the terminal
    if len(sys.argv) > 2:
        extractor = AudioExtractor()
        extractor.extract(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python audio_extractor.py <input_video> <output_audio>")
