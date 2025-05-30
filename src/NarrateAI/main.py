import os
import gradio as gr
import audio.kokoro_tts as kokoro
from utils.file_reader import FileReader
import utils.logging_config as lf

logger = lf.configure_logger(__name__)

class AudiobookGeneratorApp:
    def __init__(self):
        self.tts_engine = kokoro.Kokoro_TTS()
        self.file_reader = FileReader()

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


    def create_main_interface(self):
        logger.info("Creating main Gradio interface.")
        inputs = [
            gr.File(
                label="Upload your document (TXT, PDF, EPUB, DOCX, HTML)",
                type="filepath"
            )
        ]
        outputs = [
            gr.Audio(
                label="Generated Audiobook",
                type="filepath"
            )
        ]

        interface = gr.Interface(
            fn=self.generate_audiobook,
            inputs=inputs,
            outputs=outputs,
            title="NarrateAI Audiobook Generator"
        )
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