# This is the main entry point for Hugging Face Spaces
from gradio_app import create_interface

if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
