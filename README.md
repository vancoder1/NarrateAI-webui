# NarrateAI-webui: Audiobook Generator 🎧📚

NarrateAI-webui is a user-friendly tool that leverages the power of **Kokoro TTS** to convert your documents and books into high-quality audiobooks. With its intuitive Gradio web interface, you can effortlessly upload files in various formats and receive a polished audiobook ready for listening.

<img width="1280" alt="NarrateAI Web UI Screenshot" src="https://github.com/vancoder1/NarrateAI-webui/assets/53685919/57665255-ae33-4f2b-ac2c-e97578230229">

## ✨ What's New in this Major Update?

*   **🚀 Upgraded TTS Engine**: Now powered by **Kokoro TTS** (`hexgrad/Kokoro-82M`) for diverse voice options and high-quality audio synthesis.
*   **📄 Expanded File Format Support**: Convert a wider range of documents! We now support:
    *   Plain Text (`.txt`)
    *   PDF (`.pdf`)
    *   EPUB (`.epub`)
    *   Microsoft Word (`.docx`)
    *   HTML (`.html`, `.htm`)
*   **⚙️ Enhanced Customization via UI**:
    *   A dedicated "Settings" tab in the web UI allows you to easily select language, voice, speaking speed, and processing device (CPU/CUDA).
    *   Changes are saved to `config/config.json` and the TTS engine re-initializes on the fly.
*   **🔧 Flexible Configuration**: The `config/config.json` file provides advanced control over Kokoro TTS defaults and available voice mappings.
*   **🔄 Easy Updates**: Keep your NarrateAI-webui up-to-date with the new `update.bat` script.

## 🌟 Core Features

*   **Multi-Format Upload**: Seamlessly upload your documents in TXT, PDF, EPUB, DOCX, and HTML formats.
*   **High-Quality Local TTS**: Utilizes Kokoro TTS for efficient and excellent text-to-speech conversion directly on your machine.
*   **Intuitive Web Interface**: A clean and simple Gradio UI for easy operation.
    *   **Audiobook Generator Tab**: Upload your document and start the generation process.
    *   **Settings Tab**: Fine-tune TTS parameters like language, specific voice, speech rate, and choose between CPU or GPU (CUDA) for processing.
*   **Customizable Audio Output**:
    *   Select preferred language and voice from available options.
    *   Adjust speaking speed (0.1x to 2.0x).
*   **Automatic Output**: Generated audiobooks are saved in `.wav` format directly into the `outputs/` directory (e.g., `outputs/your-file-name.wav`).
*   **Detailed Logging**: Comprehensive logs are stored in the `logs/` directory for monitoring and troubleshooting.

## 🖥️ System Requirements

### Minimum Requirements:
*   **RAM**: 8GB
*   **Free Disk Space**: 1GB (plus space for generated audiobooks and TTS models)

### Recommended Requirements:
*   **RAM**: 16GB
*   **Free Disk Space**: 2GB+

#### Notes:
*   **GPU Support**: An NVIDIA GPU with CUDA support is recommended for optimal performance and faster processing. CPU-only mode is also available.
*   **OS Compatibility**: Primarily developed and tested on Windows. Linux and macOS may work but have not been formally tested.

## 🚀 Installation

### Prerequisites

1.  **Python 3.8+**: Ensure Python is installed. Download from [python.org](https://www.python.org/). We recommend Python 3.12.x as used in the installer.
2.  **CUDA Toolkit** (Optional, for GPU acceleration): If you plan to use an NVIDIA GPU, install the appropriate CUDA Toolkit. Download from [NVIDIA Developer](https://developer.nvidia.com/cuda-toolkit). The installer provides options for different CUDA versions.
3.  **Miniconda/Anaconda**: A Conda environment is used for managing dependencies. Download Miniconda from [docs.anaconda.com](https://docs.anaconda.com/free/miniconda/index.html). **Ensure you check "Add to PATH" during installation.**

### Steps

1.  **Clone the Repository**:
    ```sh
    git clone https://github.com/vancoder1/NarrateAI-webui.git
    cd NarrateAI-webui
    ```

2.  **Run the Installer**:
    Execute the `install.bat` script. This will:
    *   Create a Conda environment named `narrate`.
    *   Install Python.
    *   Install all necessary dependencies from `requirements.txt`.
    *   Prompt you to choose a PyTorch version (CUDA 12.8, CUDA 11.8, or CPU-only).
    ```bat
    .\install.bat
    ```

3.  **Wait for the installation to complete.** The script will guide you through the PyTorch selection.

## 📖 Usage

1.  **Start the Application**:
    Run the `start.bat` script. This will activate the Conda environment and launch the Gradio web UI.
    ```bat
    .\start.bat
    ```
    The application will automatically open in your default web browser.

2.  **Configure Settings (Optional but Recommended for First Use)**:
    *   Navigate to the **Settings** tab.
    *   Select your desired **Language Code**, **Voice**, **Speed**, and **Device** (CPU/CUDA).
    *   Click "Update Settings". The available voices will update based on the selected language.

3.  **Generate Audiobook**:
    *   Navigate to the **Audiobook Generator** tab.
    *   Upload your document file (e.g., `.txt`, `.pdf`, `.epub`, `.docx`, `.html`).
    *   The generation process will begin, showing progress updates.
    *   Once completed, an audio player will appear with your generated audiobook, and the `.wav` file will be available in the `outputs/` directory (e.g., `outputs/your-book-title.wav`).

## 🔧 Configuration

The primary application settings can be managed through the **Settings** tab in the UI. These settings are persisted in `config/config.json`.

The `config/config.json` file stores:
```json
{
    "settings": {
        "kokoro_tts": {
            "lang_code": "a", // Default language code
            "voice": "af_heart", // Default voice
            "speed": 1.0, // Default speed
            "device": "cpu", // Default device ('cpu' or 'cuda')
            "language_voices_map": { // Defines available voices for language codes
                "a": ["af_heart", "af_bella", ...],
                "b": ["bf_emma", "bf_isabella", ...],
                // ... other language codes and their voices
            }
        }
    }
}
```
You can manually edit this file for advanced configuration, but changes made through the UI will override these defaults.

## 🔄 Updating the Application

To update NarrateAI-webui to the latest version:
1.  Ensure you have `git` installed.
2.  Run the `update.bat` script:
    ```bat
    .\update.bat
    ```
    This script will:
    *   Fetch the latest changes from the repository.
    *   Pull updates for your current branch.
    *   Upgrade dependencies based on `requirements.txt`.

## 🤝 Contributing

Contributions are highly welcome! If you have ideas, suggestions, feature requests, or find bugs, please:
1.  Open an issue on the GitHub repository to discuss the change.
2.  Fork the repository, make your changes, and submit a pull request.

Please ensure your code follows the existing style.

## 📜 License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for full details.

## 🙏 Acknowledgements

*   **Gradio**: For the easy-to-use Python library that helps build the web UI ([Gradio GitHub](https://github.com/gradio-app/gradio)).
*   **Kokoro TTS**: The powerful text-to-speech engine used for audio generation ([hexgrad/Kokoro-82M on Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M)).
*   All the creators and maintainers of the various Python libraries used in this project (see `requirements.txt`).

## 📬 Contact

For any questions, feedback, or issues, please open an issue on this GitHub repository. You can also reach out to `ivanzaporozhets25@gmail.com`.

---

Made with ❤️ by vancoder1