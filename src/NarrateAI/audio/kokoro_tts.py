import os
import time
from typing import Optional, List, Callable
import re
import soundfile as sf
from pydub import AudioSegment
from kokoro import KPipeline
import utils.json_handler as jh
import utils.logging_config as lf
from utils.constants import OUTPUTS_DIR

logger = lf.configure_logger(__name__)
json_handler = jh.JsonHandler()

# --- Constants ---
SAMPLE_RATE = 24000
KOKORO_REPO_ID = 'hexgrad/Kokoro-82M'

class Kokoro_TTS:
    def __init__(self,
                 sample_rate: int = SAMPLE_RATE,
                 lang_code: Optional[str] = None,
                 voice: Optional[str] = None,
                 speed: Optional[float] = None,
                 device: Optional[str] = None):
        self.sample_rate = sample_rate
        tts_settings = json_handler.get_setting('settings.kokoro_tts')
        if tts_settings is None:
            logger.critical("Failed to load 'settings.kokoro_tts' from JSON. TTS will likely fail.")
            tts_settings = {}

        self.lang_code = lang_code if lang_code is not None else tts_settings.get('lang_code')
        self.voice = voice if voice is not None else tts_settings.get('voice')
        self.speed = speed if speed is not None else tts_settings.get('speed', 1.0)
        self.device = device if device is not None else tts_settings.get('device', 'cpu')
        self.output_format = 'wav'
        
        self.pipeline: Optional[KPipeline] = None

        if self.lang_code and self.voice:
            try:
                self.pipeline = self._initialize_pipeline()
                logger.info(f"TTS initialized: lang='{self.lang_code}', voice='{self.voice}', speed='{self.speed}', device='{self.device}', format='{self.output_format}'")
            except RuntimeError as e:
                logger.error(f"TTS initialization failed during __init__: {e}")
        else:
            logger.warning("TTS pipeline not auto-initialized in __init__: lang_code or voice is missing. Configure settings or expect errors.")

    def _initialize_pipeline(self) -> KPipeline:
        if not self.lang_code or not self.voice:
             logger.error("Cannot initialize pipeline: lang_code or voice is not set.")
             raise RuntimeError("TTS Pipeline initialization failed: lang_code or voice missing.")
        try:
            logger.info(f"Initializing KokoroTTS pipeline (repo='{KOKORO_REPO_ID}', lang='{self.lang_code}', device='{self.device}')...")
            start_time = time.time()
            pipeline = KPipeline(repo_id=KOKORO_REPO_ID, lang_code=self.lang_code, device=self.device)
            end_time = time.time()
            logger.info(f"KokoroTTS pipeline initialized successfully in {end_time - start_time:.2f} seconds.")
            return pipeline
        except ImportError:
            logger.critical('Fatal: KPipeline could not be imported. Ensure "kokoro" library is installed.', exc_info=True)
            raise RuntimeError("TTS Pipeline initialization failed: 'kokoro' library not found.")
        except Exception as e:
            logger.critical(f'Fatal: Failed to initialize KokoroTTS pipeline: {e}', exc_info=True)
            raise RuntimeError(f"TTS Pipeline initialization failed: {e}") from e

    def process_audio(self, input_text: str, base_file_name: str, progress_callback: Optional[Callable] = None) -> Optional[str]:
        base_file_name = os.path.basename(base_file_name)

        if not self.pipeline:
            logger.warning("TTS pipeline was not initialized. Attempting to initialize now.")
            if self.lang_code and self.voice:
                try:
                    self.pipeline = self._initialize_pipeline()
                    logger.info("TTS pipeline successfully re-initialized for processing.")
                except RuntimeError as e:
                    logger.error(f"Failed to re-initialize TTS pipeline for '{base_file_name}': {e}")
                    raise # Re-raise, as processing cannot continue
            else:
                logger.error(f"Cannot initialize TTS pipeline for '{base_file_name}': lang_code or voice is missing.")
                raise RuntimeError("TTS pipeline cannot be initialized due to missing settings (lang_code, voice).")

        if not input_text or input_text.isspace():
            logger.warning(f"Input text for '{base_file_name}' is empty or whitespace. Skipping audio generation.")
            return None

        chunk_output_dir = os.path.join(OUTPUTS_DIR, base_file_name + "_chunks")
        audio_output_paths: List[str] = []

        split_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|։|۔|。)\s'

        segments = re.split(split_pattern, input_text)
        filtered_segments = [s for s in segments if s and s.strip()]
        total_chunks_estimate = len(filtered_segments)
        if not filtered_segments and input_text and input_text.strip():
            total_chunks_estimate = 1
        if total_chunks_estimate == 0 and input_text and input_text.strip():
            total_chunks_estimate = 1


        try:
            os.makedirs(chunk_output_dir, exist_ok=True)
            logger.debug(f"Chunk output directory for '{base_file_name}': {chunk_output_dir}")

            generator = self.pipeline(
                text=input_text,
                voice=self.voice,
                speed=self.speed,
                split_pattern=split_pattern
            )

            generated_chunk_count = 0
            for i, (gs, ps, audio_data) in enumerate(generator):
                generated_chunk_count +=1
                chunk_file_name = f"{base_file_name}_chunk_{i:03d}.wav" # Padded for sorting
                chunk_file_path = os.path.join(chunk_output_dir, chunk_file_name)
                sf.write(chunk_file_path, audio_data, self.sample_rate)
                audio_output_paths.append(chunk_file_path)
                if progress_callback:
                    current_progress_total = max(total_chunks_estimate, 1)
                    progress_callback(generated_chunk_count, current_progress_total, f"Generating audio chunk {generated_chunk_count}/{current_progress_total if total_chunks_estimate > 0 else '...'}")

            if not audio_output_paths:
                logger.warning(f"No audio chunks generated for '{base_file_name}'. Text might be unsuitable or too short.")
                return None

            logger.info(f"Generated {len(audio_output_paths)} audio chunks for '{base_file_name}'.")

            combined_audio = AudioSegment.empty()
            num_chunks_to_combine = len(audio_output_paths)
            for idx, path in enumerate(audio_output_paths):
                if progress_callback:
                    progress_callback(idx + 1, num_chunks_to_combine, f"Combining chunk {idx + 1}/{num_chunks_to_combine}")
                try:
                    segment = AudioSegment.from_wav(path)
                    combined_audio += segment
                except Exception as e:
                    logger.error(f"Error loading audio chunk '{path}' for '{base_file_name}': {e}. Skipping chunk.", exc_info=True)
                    continue

            if len(combined_audio) == 0:
                logger.error(f"Combined audio for '{base_file_name}' is empty. All chunks might have failed processing or were unsuitable.")
                return None

            final_output_path = os.path.join(OUTPUTS_DIR, f'{base_file_name}.{self.output_format}')
            combined_audio.export(final_output_path, format=self.output_format)
            logger.info(f"Audiobook '{final_output_path}' generated successfully for '{base_file_name}'.")
            return final_output_path

        except RuntimeError as e:
            logger.error(f"Runtime error during audio processing for '{base_file_name}': {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during audio processing for '{base_file_name}': {e}", exc_info=True)
            raise RuntimeError(f"Audio processing failed unexpectedly for '{base_file_name}': {e}") from e
        finally:
            if os.path.exists(chunk_output_dir):
                for path in audio_output_paths:
                    if os.path.exists(path):
                        try:
                            os.remove(path)
                        except OSError as e_rm:
                            logger.warning(f"Could not remove chunk file {path} for '{base_file_name}': {e_rm}")
                try:
                    if not os.listdir(chunk_output_dir):
                         os.rmdir(chunk_output_dir)
                         logger.debug(f"Successfully removed empty chunk directory: {chunk_output_dir}")
                    else:
                        logger.warning(f"Chunk directory {chunk_output_dir} for '{base_file_name}' not empty after processing, not removing. Contents: {os.listdir(chunk_output_dir)}")
                except OSError as e_rmdir:
                    logger.warning(f"Could not remove chunk directory {chunk_output_dir} for '{base_file_name}': {e_rmdir}")