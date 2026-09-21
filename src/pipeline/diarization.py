import logging
from typing import Any, Dict, List
import torch
import gc
from pyannote.audio import Pipeline

logger = logging.getLogger(__name__)

class SpeakerDiarizer:
    """
    Identifies who spoke when in the audio file using pyannote.audio
    """
    def __init__(self, auth_token: str, device: str = "cuda"):
        """
        Initializes the speaker diarizer

        Args:
            auth_token: Hugging Face authentication token for pyannote.audio
            device: Device to use for processing ('cuda' for GPU, 'cpu' for CPU)
        """
        # the pyannote.audio model is gated by researchers
        self.auth_token = auth_token
        self.device = device
        self.pipeline = None

    def load(self):
        """ 
        Loads the Diarization pipeline into the VRAM.
        """
        if self.pipeline is None:
            logger.info("Loading Pyannote Speaker Diarization model...")

            try:
                # The pyannote.audio pipeline downloads the model from the Hugging Face Hub using token and caches it locally for future use.
                
                self.pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=self.auth_token
                )
                if self.device == "cuda":
                    self.pipeline.to(torch.device(self.device))

            except Exception as e:
                logger.error(f"Failed to load Pyannote. Ensure you have accepted the terms on Hugging Face and have a valid token. Error: {e}")
                raise

    def unload(self):
        """ 
        Unloads the Pyannote model to free VRAM. 
        """
        if self.pipeline is not None:
            logger.info("Unloading Pyannote Speaker Diarization Model to free VRAM...")
            del self.pipeline
            self.pipeline = None
            if self.device == "cuda":
                torch.cuda.empty_cache()
            gc.collect()

    def diarize(self, audio_path: str, num_speakers: int = None) -> List[Dict[str, Any]]:
        """ 
        Processes the audio to find speaker segments.
        Args:
            audio_path: Path to the clean .wav audio file
            num_speakers: Optional if you know the number of speakers in the video providing this can help the model diarize more accurately.

        Returns:
            A list of dictionaries, where each dictionary represents a speech segment with the speaker label and the start/end times.
            Example:
            [
                {'start': 0.0, 'end': 5.0, 'speaker': 'SPEAKER_00'},
                {'start': 5.0, 'end': 10.0, 'speaker': 'SPEAKER_01'}
            ]            
        """
        try:
            self.load()
            logger.info(f"Diarizing {audio_path}...")
            # If we pass num_speakers, it forces the AI to only look for that many unique voices.

            diarization_output = self.pipeline(audio_path, num_speakers = num_speakers)

            segments = []
            for turn, _, speaker in diarization_output.itertracks(yield_label=True):
                seg_dict = {
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                }
                segments.append(seg_dict)

                print(f"[{turn.start:.2f}s -> {turn.end:.2f}s] {speaker}")
            
            logger.info(f"Diarization complete. Found {len(segments)} speaker segments.")
            return segments

        except Exception as e:
            logger.error(f"Diarization failed: {str(e)}")
            return []
        finally:
            self.unload()

# Quick test block
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        audio_file = sys.argv[1]
        token = sys.argv[2]

        diarizer = SpeakerDiarizer(auth_token=token)
        # We'll leave num_speakers as blank for now so it auto-detects
        diarizer.diarize(audio_file)
    else:
        print("Usage: python src/pipeline/diarization.py <audio_file> <hf_token>")