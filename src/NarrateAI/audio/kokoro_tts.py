import os
import time
from typing import Optional
import torch
import soundfile as sf
from pydub import AudioSegment
from kokoro import KPipeline
import utils.json_handler as jh
import utils.logging_config as lf

logger = lf.configure_logger(__name__)
json_handler = jh.JsonHandler()

# Retrieve settings dynamically
MODEL_PATH = json_handler.get_setting('settings.kokoro_tts.model_path')

# --- Constants ---
SAMPLE_RATE = 24000

class Kokoro_TTS:
    def __init__(self,
                 sample_rate: int = SAMPLE_RATE,
                 model_path: str = MODEL_PATH,
                 lang_code: str = None,
                 voice: str = None):
        self.sample_rate = sample_rate
        self.model_path = model_path 
        self.lang_code = lang_code if lang_code is not None else json_handler.get_setting('settings.kokoro_tts.lang_code')
        self.voice = voice if voice is not None else json_handler.get_setting('settings.kokoro_tts.voice')     
        self.pipeline: Optional[KPipeline] = None      
        if self.lang_code and self.voice and KPipeline is not None:
            self.pipeline = self._initialize_pipeline()
            logger.info(f"TTS initialized with lang_code='{self.lang_code}', voice='{self.voice}'")
        else:
            logger.warning("TTS pipeline not initialized due to missing lang_code/voice or KPipeline not available.")

    def _initialize_pipeline(self) -> Optional[KPipeline]:
        if KPipeline is None:
            return None
        try:
            repo_id = 'hexgrad/Kokoro-82M'
            logger.info(f"Initializing KokoroTTS pipeline (repo='{repo_id}', lang='{self.lang_code}')...")
            start_time = time.time()
            pipeline = KPipeline(repo_id=repo_id, lang_code=self.lang_code)
            end_time = time.time()
            logger.info(f"KokoroTTS pipeline initialized successfully in {end_time - start_time:.2f} seconds.")
            return pipeline
        except Exception as e:
            logger.error(f'Fatal: Failed to initialize KokoroTTS pipeline: {e}', exc_info=True)
            raise RuntimeError("TTS Pipeline initialization failed.") from e
    
    def process_audio(self, input_text: str, file_name: str):
        if self.pipeline is None:
            logger.error("TTS pipeline is not initialized. Cannot process audio.")
            raise RuntimeError("TTS pipeline is not initialized. Please check settings.")
        try:
            output_dir = 'outputs'
            chunk_output_dir = os.path.join(output_dir, file_name)
            # Ensure output directory exists
            if not os.path.exists(chunk_output_dir):
                os.makedirs(chunk_output_dir, exist_ok=True)

            generator = self.pipeline(
                text=input_text,
                voice=self.voice,
                speed=1,
                split_pattern=r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s'
            )

            # Generate and save audio for each chunk
            audio_output_paths = []
            for i, (gs, ps, audio) in enumerate(generator):
                chunk_file_name = f"{file_name}_chunk_{i}.wav"
                sf.write(os.path.join(chunk_output_dir, chunk_file_name), audio, self.sample_rate)
                audio_output_paths.append(os.path.join(chunk_output_dir, chunk_file_name))

            # Combine all chunks into one audio file
            combined = AudioSegment.empty()
            for path in audio_output_paths:
                segment = AudioSegment.from_wav(path)
                combined += segment

            combined_output_path = os.path.join(output_dir, f'{file_name}.wav')
            combined.export(combined_output_path, format="wav")

            # Delete the chunk files
            for path in audio_output_paths:
                os.remove(path)
            os.removedirs(chunk_output_dir)

            return combined_output_path
        except Exception as e:
            logger.error(f"An error occurred while processing audio: {e}", exc_info=True)
            raise RuntimeError(f"Audio processing failed: {e}")