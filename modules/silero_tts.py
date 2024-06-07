import os
import torch
from scipy.io.wavfile import write
import modules.json_handler as jh
import modules.logging_config as lf

logger = lf.configure_logger(__name__)
json_handler = jh.JsonHandler('config.json')

LANGUAGE = json_handler.get_setting('settings.language')
MODEL_ID = json_handler.get_setting('settings.model_id')
SPEAKER = json_handler.get_setting('settings.speaker')
SAMPLE_RATE = json_handler.get_setting('settings.sample_rate')

class Silero_TTS:
    def __init__(self, 
                 language: str = LANGUAGE, 
                 model_id: str = MODEL_ID, 
                 speaker: str = SPEAKER, 
                 sample_rate: int = SAMPLE_RATE, 
                 output_dir: str = 'outputs',
                 output_file: str = 'output.mp3',
                 model_dir: str = 'models'):
        self.language = language
        self.model_id = model_id
        self.speaker = speaker
        self.sample_rate = sample_rate
        self.output_dir = output_dir
        self.output_file = output_file
        self.model_dir = model_dir
        self.model = None

    def load_model(self):
        model_path = self.model_dir + '/' + self.model_id
        if not os.path.exists(model_path):
            os.makedirs(model_path, exist_ok=True)

        model_path = model_path + '/' + 'model.pt'
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if not os.path.isfile(model_path):
            torch.hub.download_url_to_file('https://models.silero.ai/models/tts/en/v3_en.pt', 
                                           model_path)  
        self.model = torch.package.PackageImporter(model_path).load_pickle("tts_models", "model")
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