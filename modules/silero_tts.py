import os
import torch
from scipy.io.wavfile import write
from pydub import AudioSegment
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
                 model_dir: str = 'models'):
        self.language = language
        self.model_id = model_id
        self.speaker = speaker
        self.sample_rate = sample_rate
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

    def split_text(self, text, max_length=1000):
        """
        Splits the text into chunks of a maximum length.
        """
        words = text.split()
        chunks = []
        chunk = []

        for word in words:
            if len(' '.join(chunk + [word])) > max_length:
                chunks.append(' '.join(chunk))
                chunk = [word]
            else:
                chunk.append(word)
        
        if chunk:
            chunks.append(' '.join(chunk))
        
        return chunks
    
    def process_audio(self, input_text: str, file_name: str):
        try:
            output_dir = 'outputs/' + file_name + '/'
            # Ensure output directory exists
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            # Split the input text into smaller chunks
            text_chunks = self.split_text(input_text)

            # Generate and save audio for each chunk
            audio_output_paths = []
            for i, chunk in enumerate(text_chunks):
                audio = self.model.apply_tts(text=chunk, speaker=self.speaker, sample_rate=self.sample_rate)
                chunk_file_name = f"{file_name}_chunk_{i}.mp3"
                output = output_dir + chunk_file_name
                write(output, self.sample_rate, audio.numpy())
                audio_output_paths.append(output)

            # Combine all chunks into one audio file
            combined = AudioSegment.empty()
            for path in audio_output_paths:
                segment = AudioSegment.from_wav(path)
                combined += segment

            combined_output_path = f'{output_dir}{file_name}.mp3'
            combined.export(combined_output_path, format="mp3")

            # Delete the individual chunk files
            for path in audio_output_paths:
                os.remove(path)

            return combined_output_path
        except Exception as e:
            logger.error(f"An error occurred while processing audio: {e}")
            return None