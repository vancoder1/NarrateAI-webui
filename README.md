# NarrateAI-webui

Welcome to NarrateAI-webui, your ultimate tool for converting books into audiobooks effortlessly! Harnessing the power of Silero TTS, this application offers a seamless way to transform written text into captivating audio content. With its intuitive Gradio web UI, you can swiftly upload your favorite books and receive high-quality audiobooks in return.

<img width="1280" alt="Screenshot 2024-06-07 220047" src="https://github.com/vancoder1/NarrateAI-webui/assets/53685919/57665255-ae33-4f2b-ac2c-e97578230229">

## 🌟 Features

- **Simple Upload**: Effortlessly upload your book files in .txt and .pdf formats.
- **Local TTS**: Leveraging Silero TTS, enjoy fast yet high-quality text-to-speech conversion locally.
- **Fast Interference**: Silero TTS ensures rapid processing without compromising on audio quality.
- **Customizability**: Tailor your experience by configuring models and voices in `config.json`.
- **Automatic Output**: Your audiobook is automatically saved in the `outputs/your-file-name/` directory.

## 🖥️ System Requirements

### Minimum Requirements:
- **RAM**: 8GB
- **Free Disk Space**: 1GB

### Recommended Requirements:
- **RAM**: 16GB
- **Free Disk Space**: 1GB

#### Notes:
- **GPU Support**: Nvidia GPU recommended for optimal performance; CPU can be used as an alternative.
- **OS Compatibility**: Windows is preferable; Linux and macOS platforms have not undergone testing.

## 🚀 Installation

### Prerequisites

1. **Python 3.8+**: Make sure Python is installed on your system. You can download it from [python.org](https://www.python.org/).

2. **CUDA Toolkit** (if using GPU): Ensure you have the CUDA toolkit installed to leverage GPU acceleration. Download it from [NVIDIA's website](https://developer.nvidia.com/cuda-toolkit).

3. **Miniconda**: Ensure Miniconda is installed. Don't forget to check `Add to PATH` during installation. Download it here [Miniconda](https://docs.anaconda.com/free/miniconda/index.html).

### Steps

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/vancoder1/NarrateAI-webui.git
    cd NarrateAI-webui
    ```

2. **Install everything using install_windows.bat**:
    ```sh
    .\install_windows.bat
    ```

3. **Wait for the installation to complete**.

## 📖 Usage

1. **Start the Application**:
    ```sh
    .\start_windows.bat
    ```

2. **Upload File**: Select your desired file and wait for transcription. Once processing is complete, find the output in `outputs/your-file-name/`.

## 🤝 Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, feel free to open an issue or submit a pull request.

## 📜 License

This project is licensed under the [Apache License 2.0](LICENSE).

## 🙏 Acknowledgements

- [Gradio](https://github.com/gradio-app/gradio)
- [SileroTTS](https://github.com/snakers4/silero-models)

## 📬 Contact

For any questions or feedback, please open an issue on this repository or reach out to `ivanzaporozhets25@gmail.com`.
