import logging
from faster_whisper import WhisperModel
import torch
import gc

logger = logging.getLogger(__name__)

class LanguageDetector:
    """
    Detects the primary language of an audio file using Faster-Whisper.
    It only processes the first 30 seconds to be extremely fast.
    """
    
    def __init__(self, model_size: str = "base", device: str = "cuda"):
        # "base" model is small and fast. It's highly accurate for language detection.
        # "cuda" tells it to use your RTX 5050 GPU instead of your CPU.
        self.model_size = model_size
        self.device = device
        
        # We start with the model as None so it doesn't take up VRAM until we actually need it.
        self.model = None

    def load(self):
        """Loads the AI model into the GPU (VRAM)."""
        if self.model is None:
            logger.info(f"Loading Language Detector ({self.model_size}) into {self.device}...")
            
            # compute_type="float16" forces the model to use 16-bit precision.
            # This cuts the VRAM usage in half compared to standard 32-bit float, 
            # without losing any noticeable accuracy.
            self.model = WhisperModel(self.model_size, device=self.device, compute_type="float16")
    
    def unload(self):
        """Unloads the AI model and clears the GPU memory. Critical for 8GB VRAM limit."""
        if self.model is not None:
            logger.info("Unloading Language Detector to free VRAM...")
            del self.model             # Delete the Python object
            self.model = None          # Reset the pointer
            
            if self.device == "cuda":
                torch.cuda.empty_cache() # Force PyTorch to give the VRAM back to Windows
            
            gc.collect()               # Force Python's Garbage Collector to clean RAM

    def detect(self, audio_path: str) -> tuple[str, float]:
        """
        Detect language from audio.
        Returns a tuple containing: (language_code, probability_score)
        """
        try:
            # 1. Load model into VRAM
            self.load()
            logger.info(f"Detecting language for {audio_path}...")
            
            # 2. Transcribe
            # We don't actually care about the text right now. 
            # We just want the 'info' object which contains the detected language.
            # beam_size=1 makes it run instantly (it doesn't try to guess alternative words).
            _, info = self.model.transcribe(audio_path, beam_size=1)
            
            logger.info(f"Detected language: '{info.language}' with probability {info.language_probability:.2f}")
            
            # 3. Return the result (e.g., "en" for English, "hi" for Hindi)
            return info.language, info.language_probability
            
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return "en", 0.0 # Default fallback if it crashes
            
        finally:
            # 4. UNLOAD THE MODEL
            # The 'finally' block guarantees this runs even if the code crashes above.
            # This is your ultimate protection against "CUDA Out of Memory" errors.
            self.unload() 

# Quick testing block
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        detector = LanguageDetector()
        lang, prob = detector.detect(sys.argv[1])
        print(f"Result: {lang} ({prob})")
