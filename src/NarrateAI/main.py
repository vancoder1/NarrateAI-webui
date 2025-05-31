import os
import warnings
import gradio as gr
import audio.kokoro_tts as kokoro
from utils.file_reader import FileReader
import utils.logging_config as lf
import utils.json_handler as jh

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

    def generate_audiobook(self, uploaded_file_object):
        logger.info(f"Attempting to generate audiobook for file: {uploaded_file_object.name}")
        temp_file_path = uploaded_file_object.name
        try:
            text_content = self.file_reader.read_file(temp_file_path)
            logger.info(f"Successfully read content from {os.path.basename(temp_file_path)}")
            if not text_content or text_content.isspace():
                logger.warning(f"File {os.path.basename(temp_file_path)} is empty or contains no readable text.")
                raise gr.Error(f"The file '{os.path.basename(temp_file_path)}' appears to be empty or contains no readable text.")
            
            base_name_for_output = os.path.splitext(os.path.basename(temp_file_path))[0]
            logger.info(f"Processing audio for {base_name_for_output}")
            audio_output_path = self.tts_engine.process_audio(text_content, base_name_for_output)
            if audio_output_path and os.path.exists(audio_output_path):
                logger.info(f"Audiobook generated successfully at: {audio_output_path}")
                return audio_output_path
            else:
                logger.error(f"Audiobook generation failed for {base_name_for_output}. Output path: {audio_output_path}")
                raise gr.Error("Audiobook generation failed. The audio file could not be created. Please check the logs.")

        except FileNotFoundError as e:
            logger.error(f"FileNotFoundError during audiobook generation: {e}")
            raise gr.Error(f"An error occurred: {str(e)}. Please ensure the file was uploaded correctly.")
        except ValueError as e:
            logger.error(f"ValueError during audiobook generation: {e}")
            raise gr.Error(f"{str(e)}")
        except NotImplementedError as e:
            logger.error(f"NotImplementedError during audiobook generation: {e}")
            raise gr.Error(f"Processing error: {str(e)}. You might need to install additional libraries.")
        except Exception as e:
            logger.critical(f"Critical Error: An unexpected error occurred in generate_audiobook: {e}", exc_info=True)
            raise gr.Error(f"An unexpected error occurred. Please try again or check the application logs. Details: {str(e)}")


    def update_settings(self, lang_code, voice):
        self.json_handler.set_setting('settings.kokoro_tts.lang_code', lang_code)
        self.json_handler.set_setting('settings.kokoro_tts.voice', voice)
        # Re-initialize TTS engine with new settings
        self.tts_engine = kokoro.Kokoro_TTS(lang_code=lang_code, voice=voice)
        logger.info(f"Settings updated")
        return "Settings updated successfully!"

    def create_settings_interface(self):
        logger.info("Creating settings Gradio interface.")
        with gr.Blocks() as settings_interface:
            gr.Markdown("## Settings")
            language_voices_map = self.json_handler.get_setting('settings.kokoro_tts.language_voices_map')
            current_lang_code = self.json_handler.get_setting('settings.kokoro_tts.lang_code')
            current_voice = self.json_handler.get_setting('settings.kokoro_tts.voice')

            # Get initial language codes and voices
            available_lang_codes = list(language_voices_map.keys())
            initial_voices = language_voices_map.get(current_lang_code, [])

            lang_code_input = gr.Dropdown(
                label="Language Code",
                choices=available_lang_codes,
                value=current_lang_code,
                interactive=True
            )
            voice_input = gr.Dropdown(
                label="Voice",
                choices=initial_voices,
                value=current_voice if current_voice in initial_voices else (initial_voices[0] if initial_voices else None),
                interactive=True
            )
            update_button = gr.Button("Update Settings")
            output_message = gr.Textbox(label="Status", interactive=False)

            def get_voices_for_lang(lang_code):
                return gr.Dropdown(choices=language_voices_map.get(lang_code, []), value=None)

            lang_code_input.change(
                fn=get_voices_for_lang,
                inputs=[lang_code_input],
                outputs=[voice_input]
            )

            update_button.click(
                fn=self.update_settings,
                inputs=[lang_code_input, voice_input],
                outputs=output_message
            )
        logger.info("Settings Gradio interface created.")
        return settings_interface

    def create_main_interface(self):
        logger.info("Creating main Gradio interface.")
        with gr.TabbedInterface(
            [
                gr.Interface(
                    fn=self.generate_audiobook,
                    inputs=[
                        gr.File(
                            label="Upload your document (TXT, PDF, EPUB, DOCX, HTML)",
                            type="filepath"
                        )
                    ],
                    outputs=[
                        gr.Audio(
                            label="Generated Audiobook",
                            type="filepath"
                        )
                    ],
                    title="NarrateAI Audiobook Generator"
                ),
                self.create_settings_interface()
            ],
            ["Audiobook Generator", "Settings"]
        ) as interface:
            logger.info("Gradio interface created.")
            return interface

    def launch(self):
        logger.info("Launching Gradio interface.")
        interface = self.create_main_interface()
        interface.launch(share=False)
        logger.info("Gradio interface launched.")

# Launch the Gradio interface
if __name__ == "__main__":
    app = AudiobookGeneratorApp()
    app.launch()