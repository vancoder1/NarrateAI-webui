import os
import torch
from scipy.io.wavfile import write
import modules.logging_config as lf

logger = lf.configure_logger(__name__)

class Silero_TTS:
    def __init__(self, 
                 language: str = 'en', 
                 model_id: str = 'v3_en', 
                 speaker: str = 'en_107', 
                 sample_rate: int = 48000, 
                 output_dir: str = 'outputs/',
                 output_file: str = 'output.mp3',
                 model_dir: str = 'models/',
                 model_file: str = 'silero_model.pt'):
        self.language = language
        self.model_id = model_id
        self.speaker = speaker
        self.sample_rate = sample_rate
        self.output_dir = output_dir
        self.output_file = output_file
        self.model_dir = model_dir
        self.model_file = model_file
        self.model = None

    def load_model(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)
        if not os.path.isfile(self.model_dir + self.model_file):
            torch.hub.download_url_to_file('https://models.silero.ai/models/tts/en/v3_en.pt', 
                                           self.model_dir + self.model_file)  
        self.model = torch.package.PackageImporter(self.model_dir + 
                                                   self.model_file).load_pickle("tts_models", "model")
        self.model.to(self.device)
    
    def process_audio(self, input_text: str):
        try:
            # Generate audio from text
            audio = self.model.apply_tts(text=input_text, speaker=self.speaker, sample_rate=self.sample_rate)
            
            # Ensure output directory exists
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, exist_ok=True)
            
            # Save the audio to a .wav file
            output_path = os.path.join(self.output_dir, self.output_file)
            write(output_path, self.sample_rate, audio.numpy())
            
            return output_path
        except Exception as e:
            logger.error(f"An error occurred while processing audio: {e}")
            return None