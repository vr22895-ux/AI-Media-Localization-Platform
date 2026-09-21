import logging
from typing import Any, Dict, List, Optional
from faster_whisper import WhisperModel
import torch
import gc

logger = logging.getLogger(__name__)

class FasterWhisperASR:
    """ 
    
    """

    def __init__(self, model_size: str = "large-v3", device: str = "cuda"):
        self.model_size = model_size
        self.device = device
        self.model = None

    def load(self):
        """ Loads the ASR model into VRAM(GPU memory) """
        if self.model is None:
            logger.info(f"Loading ASR Model ({self.model_size}) into {self.device}...")
            self.model = WhisperModel(self.model_size, device=self.device, compute_type="float16")
        
    def unload(self):
        """ Unloads the ASR model to free VRAM """
        if self.model is not None:
            logger.info("Unloading the ASR Model to free VRAM...")
            del self.model
            self.model = None
            if self.device == "cuda":
                torch.cuda.empty_cache()
            gc.collect()
    
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Transcribe the audio using Faster-Whisper

        Args:
            audio_path: Path to the audio file
            language: Optional language code (e.g., "en", "hi")

        Returns:
            List of dictionaries, where each dictionary is a spoken sentence with a start time, end time and the text.
            Example: [{"start": 0.0, "end": 5.0, "text": "Hello, my name is Vivek."}]
        """
        try:
            # 1. Load the ASR model into VRAM 
            self.load()
            logger.info(f"Transcribing {audio_path} using {self.model_size}...")

            # 2. Transcribe with beam_size=5 (good balance of speed and accuracy)
            # If language is detected, pass it to the model for better accuracy
            # word_timestamps=True forces the AI to map exact seconds to exact words.
            segments_generator, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                word_timestamps = True
            )

            # The model outputs a 'generator', so we need to loop through it 
            # to extract the data into a clean python list of dictionaries.

            segments = []
            for segment in segments_generator:
                seg_dict = {
                    "id": segment.id,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(), # strip removes leading/trailing whitespace 
                    # List comprehension to get the word timestamps and we also save the timing of every single word inside the sentence
                    "words": [{"word": w.word, "start": w.start, "end": w.end} for w in segment.words]
                }
                segments.append(seg_dict)
                
                # Print the time and the text of each segment for debugging purposes
                print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")

            logger.info(f"Transcription Complete. Found {len(segments)} segments.")
            return segments

        except Exception as e:
            logger.error(f"ASR transcription failed: {str(e)}")
            return []
        finally:
            # 4. UNLOAD THE MODEL - Free up GPU memory immediately
            self.unload()

# Quick testing block 
# Usage: python asr.py <audio_path>
# Example: python asr.py data/input.wav

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        asr = FasterWhisperASR("large-v3")
        # we don't know language initially, so we try to infer it using the language detector 
        # if you provide a language code as 3rd argument, it uses it instead
        lang = sys.argv[2] if len(sys.argv) > 2 else None
        asr.transcribe(sys.argv[1], language = lang)