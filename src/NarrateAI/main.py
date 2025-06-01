import os
import warnings
import gradio as gr
import audio.kokoro_tts as kokoro
from utils.file_reader import FileReader
import utils.logging_config as lf
import utils.json_handler as jh
from utils.constants import OUTPUTS_DIR

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

logger = lf.configure_logger(__name__)

class AudiobookGeneratorApp:
    def __init__(self):
        self.tts_engine = kokoro.Kokoro_TTS()
        self.file_reader = FileReader()
        self.json_handler = jh.JsonHandler()

    def _read_and_validate_input_file(self, uploaded_file_path: str, progress_reporter):
        """Reads the uploaded file and performs initial validation."""
        if not uploaded_file_path:
            logger.warning("No file path provided to _read_and_validate_input_file.")
            raise ValueError("Uploaded file path is missing.")

        base_uploaded_filename = os.path.basename(uploaded_file_path)
        progress_reporter(0.05, desc=f"Reading file: {base_uploaded_filename}...")
        
        text_content = self.file_reader.read_file(uploaded_file_path) # Can raise FileNotFoundError, ValueError, NotImplementedError
        logger.info(f"Successfully read content from {base_uploaded_filename}")

        if not text_content or text_content.isspace():
            logger.warning(f"File {base_uploaded_filename} is empty or contains no readable text.")
            raise ValueError(f"The file '{base_uploaded_filename}' is empty or contains no extractable text.")
        
        return text_content, base_uploaded_filename

    def generate_audiobook(self, uploaded_file_path: str, progress=gr.Progress()):
        progress(0, desc="Initializing...")
        if not uploaded_file_path:
            logger.warning("No file uploaded for audiobook generation.")
            raise gr.Error("Please upload a file to generate an audiobook.")

        base_uploaded_filename_for_error_logging = os.path.basename(uploaded_file_path) if uploaded_file_path else "unknown_file"

        try:
            text_content, base_uploaded_filename = self._read_and_validate_input_file(uploaded_file_path, progress)
            base_uploaded_filename_for_error_logging = base_uploaded_filename # Update with actual name

            progress(0.1, desc="File read successfully. Preparing for audio generation...")
            output_base_name = os.path.splitext(base_uploaded_filename)[0]
            logger.info(f"Processing audio for '{output_base_name}'")

            def tts_progress_callback(current_step: int, total_steps: int, description: str):
                if total_steps > 0:
                    stage_progress = current_step / total_steps
                    if "Generating" in description:
                        # Initial app progress is 0.1, TTS generation phase is 80% of the rest
                        overall_progress = 0.1 + (stage_progress * 0.8)
                    elif "Combining" in description:
                        # TTS combining phase is 10% after generation (0.1 + 0.8 base)
                        overall_progress = 0.1 + 0.8 + (stage_progress * 0.1)
                    else: # Fallback for other descriptions if any
                        overall_progress = 0.1 + (current_step / total_steps * 0.9) # Assume it fits within the 90% post-initial
                    progress(min(overall_progress, 0.99), desc=description) # Cap at 0.99 until truly done
                else: # When total_steps is not meaningful (e.g., initialization phase within TTS)
                    progress(desc=description)


            audio_output_path = self.tts_engine.process_audio(
                text_content,
                output_base_name,
                progress_callback=tts_progress_callback
            )

            if audio_output_path and os.path.exists(audio_output_path):
                progress(1.0, desc="Audiobook generated successfully!")
                logger.info(f"Audiobook generated successfully: {audio_output_path}")
                return audio_output_path
            elif audio_output_path is None:
                 logger.warning(f"Audiobook generation for '{output_base_name}' resulted in no output file (e.g. input text was empty after processing).")
                 raise gr.Error(f"Audiobook generation for '{output_base_name}' did not produce an audio file. Input text might have been empty or unsuitable.")
            else: # audio_output_path is not None, but file doesn't exist
                logger.error(f"Audiobook generation failed for '{output_base_name}'. Output path '{audio_output_path}' does not exist.")
                raise gr.Error("Audiobook generation failed: The audio file was not created. Please check logs.")

        except FileNotFoundError as e:
            logger.error(f"File not found during audiobook generation for '{base_uploaded_filename_for_error_logging}': {e}", exc_info=True)
            raise gr.Error(f"An error occurred: {str(e)}. Ensure the file exists and was uploaded correctly.")
        except ValueError as e:
            logger.error(f"Value error during audiobook generation for '{base_uploaded_filename_for_error_logging}': {e}", exc_info=True)
            raise gr.Error(str(e))
        except NotImplementedError as e:
            logger.error(f"NotImplementedError during audiobook generation for '{base_uploaded_filename_for_error_logging}': {e}", exc_info=True)
            raise gr.Error(f"Processing error: {str(e)}. You might need to install additional libraries (e.g., python-docx).")
        except RuntimeError as e:
            logger.error(f"Runtime error during audiobook generation for '{base_uploaded_filename_for_error_logging}': {e}", exc_info=True)
            raise gr.Error(f"Audiobook generation encountered a runtime problem: {str(e)}. Check logs for details.")
        except Exception as e:
            logger.critical(f"Critical unexpected error in generate_audiobook for {base_uploaded_filename_for_error_logging}: {e}", exc_info=True)
            raise gr.Error(f"An unexpected error occurred. Details: {str(e)}. Check application logs.")

    def update_settings(self, lang_code, voice, speed, device):
        logger.info(f"Updating settings: lang='{lang_code}', voice='{voice}', speed={speed}, device='{device}', format='wav' (hardcoded)")

        self.json_handler.set_setting('settings.kokoro_tts.lang_code', lang_code)
        self.json_handler.set_setting('settings.kokoro_tts.voice', voice)
        self.json_handler.set_setting('settings.kokoro_tts.speed', float(speed))
        self.json_handler.set_setting('settings.kokoro_tts.device', device)

        try:
            self.tts_engine = kokoro.Kokoro_TTS(
                lang_code=lang_code,
                voice=voice,
                speed=float(speed),
                device=device
            )
            logger.info("Settings updated and TTS engine re-initialized successfully.")
            return "Settings updated successfully!"
        except RuntimeError as e:
            logger.error(f"Failed to re-initialize TTS engine with new settings: {e}", exc_info=True)
            return f"Settings saved, but TTS engine re-initialization failed: {e}. Check logs."
        except Exception as e:
            logger.error(f"Unexpected error during settings update or TTS re-initialization: {e}", exc_info=True)
            return f"Unexpected error during settings update: {e}. Check logs."

    def build_settings_components(self):
        logger.info("Building settings UI components.")
        gr.Markdown("## Settings")

        kokoro_settings = self.json_handler.get_setting('settings.kokoro_tts')
        if kokoro_settings is None:
            logger.error("Failed to load 'settings.kokoro_tts' for settings UI. Using defaults/empty.")
            kokoro_settings = {}

        language_voices_map = kokoro_settings.get('language_voices_map', {})
        current_lang_code = kokoro_settings.get('lang_code', list(language_voices_map.keys())[0] if language_voices_map else "")
        current_voice = kokoro_settings.get('voice', "")
        current_speed = float(kokoro_settings.get('speed', 1.0))
        current_device = kokoro_settings.get('device', 'cpu')

        available_lang_codes = list(language_voices_map.keys())
        initial_voices = language_voices_map.get(current_lang_code, [])

        if not initial_voices: # If current_lang_code has no voices
             current_voice = None
        elif current_voice not in initial_voices :
            current_voice = initial_voices[0]


        with gr.Row():
            lang_code_input = gr.Dropdown(
                label="Language Code", choices=available_lang_codes, value=current_lang_code, interactive=True
            )
            voice_input = gr.Dropdown(
                label="Voice", choices=initial_voices, value=current_voice, interactive=True
            )

        speed_input = gr.Slider(
            minimum=0.1, maximum=2.0, step=0.1, value=current_speed, label="Speed", interactive=True
        )
        device_input = gr.Radio(
            choices=["cpu", "cuda"], value=current_device, label="Device", interactive=True
        )

        update_button = gr.Button("Update Settings")
        output_message = gr.Textbox(label="Status", interactive=False, lines=1)

        def get_voices_for_lang_dropdown_update(lang_code_selection):
            voices = language_voices_map.get(lang_code_selection, [])
            new_voice_value = voices[0] if voices else None
            return gr.Dropdown.update(choices=voices, value=new_voice_value, interactive=True)

        lang_code_input.change(
            fn=get_voices_for_lang_dropdown_update,
            inputs=[lang_code_input],
            outputs=[voice_input]
        )

        update_button.click(
            fn=self.update_settings,
            inputs=[lang_code_input, voice_input, speed_input, device_input],
            outputs=output_message
        )
        logger.info("Settings UI components built.")


    def create_main_interface(self):
        logger.info("Creating main Gradio interface using gr.Tabs.")
        with gr.Blocks(theme=gr.themes.Soft(), title="NarrateAI Audiobook Generator") as demo_ui:
            with gr.Tabs():
                with gr.TabItem("Audiobook Generator"):
                    gr.Markdown("## Audiobook Generator")
                    gr.Interface(
                        fn=self.generate_audiobook,
                        inputs=[gr.File(label="Upload your document (TXT, PDF, EPUB, DOCX, HTML)", type="filepath")],
                        outputs=[gr.Audio(label="Generated Audiobook (WAV format)", type="filepath")],
                        allow_flagging="never"
                    )

                with gr.TabItem("Settings"):
                    self.build_settings_components()

        logger.info("Gradio main interface with gr.Tabs created.")
        return demo_ui

    def launch(self):
        logger.info("Launching Gradio interface.")
        main_ui = self.create_main_interface()
        main_ui.launch(share=False, inbrowser=True)
        logger.info("Gradio interface launched.")

if __name__ == "__main__":
    if not os.path.exists(OUTPUTS_DIR):
        os.makedirs(OUTPUTS_DIR)
        logger.info(f"Created output directory: {OUTPUTS_DIR}")

    app = AudiobookGeneratorApp()
    app.launch()