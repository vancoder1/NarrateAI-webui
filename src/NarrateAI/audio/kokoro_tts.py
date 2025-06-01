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
    def _get_config_value(self, arg_value, settings_dict: dict, key: str, default_value):
        """Helper to get config value, prioritizing arg_value."""
        if arg_value is not None:
            return arg_value
        return settings_dict.get(key, default_value)

    def __init__(self,
                 sample_rate: int = SAMPLE_RATE,
                 lang_code: Optional[str] = None,
                 voice: Optional[str] = None,
                 speed: Optional[float] = None,
                 device: Optional[str] = None):
        self.sample_rate = sample_rate
        
        tts_settings = json_handler.get_setting('settings.kokoro_tts')
        if tts_settings is None:
            logger.critical("Failed to load 'settings.kokoro_tts' from JSON. TTS functionality will be impaired or use hardcoded defaults.")
            tts_settings = {} # Prevent NoneType errors, rely on defaults

        self.lang_code = self._get_config_value(lang_code, tts_settings, 'lang_code', None)
        self.voice = self._get_config_value(voice, tts_settings, 'voice', None)
        self.speed = float(self._get_config_value(speed, tts_settings, 'speed', 1.0))
        self.device = self._get_config_value(device, tts_settings, 'device', 'cpu')
        self.output_format = 'wav'

        self.pipeline: Optional[KPipeline] = None

        if self.lang_code and self.voice:
            try:
                self.pipeline = self._initialize_pipeline()
                logger.info(f"TTS initialized: lang='{self.lang_code}', voice='{self.voice}', speed='{self.speed}', device='{self.device}', format='{self.output_format}'")
            except RuntimeError as e: # Catch errors from _initialize_pipeline
                logger.error(f"TTS initialization failed during __init__: {e}", exc_info=True)
        else:
            logger.warning("TTS pipeline not auto-initialized in __init__: lang_code or voice is missing. Configure settings or expect errors during processing.")

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

    def process_audio(self, input_text: str, base_file_name: str, progress_callback: Optional[Callable[[int, int, str], None]] = None) -> Optional[str]:
        base_file_name = os.path.basename(base_file_name)

        if not self.pipeline:
            logger.warning("TTS pipeline was not initialized. Attempting to initialize now for processing.")
            if self.lang_code and self.voice:
                try:
                    self.pipeline = self._initialize_pipeline()
                    logger.info("TTS pipeline successfully re-initialized for processing.")
                except RuntimeError as e:
                    logger.error(f"Failed to re-initialize TTS pipeline for '{base_file_name}': {e}")
                    raise # Re-raise, as processing cannot continue without a pipeline
            else:
                logger.error(f"Cannot initialize TTS pipeline for '{base_file_name}': lang_code or voice is missing.")
                raise RuntimeError("TTS pipeline cannot be initialized due to missing settings (lang_code, voice).")

        if not input_text or input_text.isspace():
            logger.warning(f"Input text for '{base_file_name}' is empty or whitespace. Skipping audio generation.")
            return None

        chunk_output_dir = os.path.join(OUTPUTS_DIR, base_file_name + "_chunks")
        os.makedirs(chunk_output_dir, exist_ok=True)
        logger.debug(f"Chunk output directory for '{base_file_name}': {chunk_output_dir}")
        
        audio_output_paths: List[str] = []
        split_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|։|۔|。)\s'
        
        segments = re.split(split_pattern, input_text)
        # Filter out empty strings that can result from re.split and strip whitespace
        filtered_segments = [seg.strip() for seg in segments if seg and seg.strip()]

        total_chunks_estimate = len(filtered_segments)
        if total_chunks_estimate == 0 and input_text and input_text.strip():
            # If splitting yields nothing for genuinely non-empty text, assume it's one large chunk.
            total_chunks_estimate = 1
        
        # Ensure total_chunks_estimate is at least 1 for progress calculation if there's any text
        current_progress_total_chunks = max(total_chunks_estimate, 1)


        try:
            generator = self.pipeline(
                text=input_text,
                voice=self.voice,
                speed=self.speed,
                split_pattern=split_pattern
            )
            
            generated_chunk_count = 0
            for i, (_gs, _ps, audio_data) in enumerate(generator):
                generated_chunk_count += 1
                chunk_file_name = f"chunk_{generated_chunk_count:04d}.wav"
                chunk_file_path = os.path.join(chunk_output_dir, chunk_file_name)
                
                sf.write(chunk_file_path, audio_data, self.sample_rate)
                audio_output_paths.append(chunk_file_path)
                
                if progress_callback:
                    progress_callback(generated_chunk_count, current_progress_total_chunks, f"Generating audio chunk {generated_chunk_count}/{current_progress_total_chunks}")
            
            if not audio_output_paths:
                logger.warning(f"No audio chunks generated for '{base_file_name}'. Text might be unsuitable or too short for the TTS.")
                return None

            logger.info(f"Generated {len(audio_output_paths)} audio chunks for '{base_file_name}'.")

            # Combine audio chunks
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
                    continue # Skip problematic chunk

            if len(combined_audio) == 0: # All chunks failed or were unsuitable
                logger.error(f"Combined audio for '{base_file_name}' is empty. All chunks might have failed processing or were unsuitable.")
                return None

            final_output_filename = f'{base_file_name}.{self.output_format}' # self.output_format is 'wav'
            final_output_path = os.path.join(OUTPUTS_DIR, final_output_filename)
            
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
            # Clean up individual chunk files and then the directory
            for path in audio_output_paths:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError as e_rm:
                        logger.warning(f"Could not remove chunk file {path} for '{base_file_name}': {e_rm}")
            
            if os.path.exists(chunk_output_dir):
                try:
                    if not os.listdir(chunk_output_dir): # Check if directory is empty
                         os.rmdir(chunk_output_dir)
                         logger.debug(f"Successfully removed empty chunk directory: {chunk_output_dir}")
                    else:
                        logger.warning(f"Chunk directory {chunk_output_dir} for '{base_file_name}' was not empty after processing known chunks. Not removing. Contents: {os.listdir(chunk_output_dir)}")
                except OSError as e_rmdir:
                    logger.warning(f"Could not remove chunk directory {chunk_output_dir} for '{base_file_name}': {e_rmdir}")