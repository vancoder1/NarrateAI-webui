import os
import gradio as gr
import modules.silero_tts as silero

# Function to read text from a file
def read_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

# Function to generate an audiobook using SileroTTS
def generate_audiobook(text, tts):
    audio_path = tts.process_audio(text)
    return audio_path

# Gradio interface handler function
def handle_inputs(file):
    reader = silero.Silero_TTS()
    reader.load_model()
    text = read_text(file.name)
    audio_path = generate_audiobook(text, reader)
    return audio_path

# Setting up Gradio interface
inputs = [ gr.components.File(label='Upload TXT', type='filepath') ]
outputs = [ gr.components.Audio(label='Generated Audiobook', type='filepath') ]
interface = gr.Interface(fn=handle_inputs, inputs=inputs, outputs=outputs)

# Launch the Gradio interface
if __name__ == "__main__":
    interface.launch(share=False)