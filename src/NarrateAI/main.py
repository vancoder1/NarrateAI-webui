import os
import gradio as gr
import audio.silero_tts as silero
import utils.file_reader as fr

class AudiobookGeneratorApp:
    def __init__(self):
        self.reader = silero.Silero_TTS()
        self.reader.load_model()

    def generate_audiobook(self, file):
        if file.name.lower().endswith('.txt'):
            text = fr.read_txt(file.name)
        elif file.name.lower().endswith('.pdf'):
            text = fr.read_pdf(file.name)
        else:
            raise ValueError("Invalid file extension")
        file_name = os.path.basename(file.name)
        file_name = os.path.splitext(file_name)[0]
        audio_path = self.reader.process_audio(text, file_name)
        return audio_path

    def create_main_interface(self):
        inputs = [gr.File(label='Upload TXT or PDF', type='filepath')]
        outputs = [gr.Audio(label='Generated Audiobook', type='filepath')]
        return gr.Interface(fn=self.generate_audiobook, inputs=inputs, outputs=outputs)

    def launch(self):
        interface = self.create_main_interface()
        interface.launch(share=False)

# Launch the Gradio interface
if __name__ == "__main__":
    app = AudiobookGeneratorApp()
    app.launch()