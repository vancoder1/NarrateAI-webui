import os
import gradio as gr
import modules.silero_tts as silero
import modules.file_reader as fr

# Function to generate an audiobook using SileroTTS
def generate_audiobook(text, tts):
    audio_path = tts.process_audio(text)
    return audio_path

# Gradio interface handler function
def handle_inputs(file):
    reader = silero.Silero_TTS()
    reader.load_model()
    if file.name.lower().endswith('.txt'):
        text = fr.read_txt(file.name)
    elif file.name.lower().endswith('.pdf'):
        text = fr.read_pdf(file.name)
    else:
        raise ValueError("Invalid file extension")
    audio_path = generate_audiobook(text, reader)
    return audio_path

# Setting up Gradio interface
inputs = [ gr.components.File(label='Upload TXT', type='filepath') ]
outputs = [ gr.components.Audio(label='Generated Audiobook', type='filepath') ]
interface = gr.Interface(fn=handle_inputs, inputs=inputs, outputs=outputs)

# Launch the Gradio interface
if __name__ == "__main__":
    interface.launch(share=False)