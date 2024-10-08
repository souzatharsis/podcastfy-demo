import gradio as gr
from podcastfy.client import generate_podcast
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_api_key(key_name, ui_value):
    return ui_value if ui_value else os.getenv(key_name)

def create_podcast(urls, openai_key, jina_key, gemini_key):
	try:
		# Set API keys, prioritizing UI input over .env file
		os.environ["OPENAI_API_KEY"] = get_api_key("OPENAI_API_KEY", openai_key)
		os.environ["JINA_API_KEY"] = get_api_key("JINA_API_KEY", jina_key)
		os.environ["GEMINI_API_KEY"] = get_api_key("GEMINI_API_KEY", gemini_key)
		
		url_list = [url.strip() for url in urls.split(',') if url.strip()]
		
		if not url_list:
			return "Please provide at least one URL."
		
		audio_file = generate_podcast(urls=url_list)
		return audio_file
	except Exception as e:
		return str(e)

# Create the Gradio interface
with gr.Blocks(title="Podcastfy.ai", theme=gr.themes.Default()) as iface:
	gr.Markdown("# Podcastfy.ai demo")
	gr.Markdown("Generate a podcast from multiple URLs using Podcastfy.")
	gr.Markdown("For full customization, please check [Podcastfy package](https://github.com/souzatharsis/podcastfy).")

	with gr.Accordion("API Keys", open=False):
		with gr.Row(variant="panel"):
			with gr.Column(scale=1):
				openai_key = gr.Textbox(label="OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
				gr.Markdown('<a href="https://platform.openai.com/api-keys" target="_blank">Get OpenAI API Key</a>')
			with gr.Column(scale=1):
				jina_key = gr.Textbox(label="Jina API Key", type="password", value=os.getenv("JINA_API_KEY", ""))
				gr.Markdown('<a href="https://jina.ai/reader/#apiform" target="_blank">Get Jina API Key</a>')
			with gr.Column(scale=1):
				gemini_key = gr.Textbox(label="Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
				gr.Markdown('<a href="https://makersuite.google.com/app/apikey" target="_blank">Get Gemini API Key</a>')

	urls = gr.Textbox(lines=2, placeholder="Enter URLs separated by commas...", label="URLs")

	generate_button = gr.Button("Generate Podcast", variant="primary")

	with gr.Column():
		gr.Markdown('<p style="color: #666; font-style: italic; margin-bottom: 5px;">Note: Podcast generation may take a couple of minutes.</p>', elem_id="generation-note")
		audio_output = gr.Audio(type="filepath", label="Generated Podcast")

	generate_button.click(
		create_podcast,
		inputs=[urls, openai_key, jina_key, gemini_key],
		outputs=audio_output
	)

	gr.Markdown('<p style="text-align: center;">Created with ❤️ by <a href="https://github.com/souzatharsis/podcastfy" target="_blank">Podcastfy</a></p>')

	# Add JavaScript for splash screen and positioning the disclaimer
	iface.load(js="""
	function addSplashScreen() {
		const audioElement = document.querySelector('.audio-wrap');
		if (audioElement) {
			const splashScreen = document.createElement('div');
			splashScreen.id = 'podcast-splash-screen';
			splashScreen.innerHTML = '<p>Generating podcast... This may take a couple of minutes.</p>';
			splashScreen.style.cssText = `
				position: absolute;
				top: 0;
				left: 0;
				right: 0;
				bottom: 0;
				background-color: rgba(0, 0, 0, 0.7);
				color: white;
				display: flex;
				justify-content: center;
				align-items: center;
				z-index: 1000;
			`;
			audioElement.style.position = 'relative';
			audioElement.appendChild(splashScreen);
		}
	}

	function removeSplashScreen() {
		const splashScreen = document.getElementById('podcast-splash-screen');
		if (splashScreen) {
			splashScreen.remove();
		}
	}

	function positionGenerationNote() {
		const noteElement = document.getElementById('generation-note');
		const audioElement = document.querySelector('.audio-wrap');
		if (noteElement && audioElement) {
			noteElement.style.position = 'absolute';
			noteElement.style.top = '-25px';
			noteElement.style.left = '0';
			noteElement.style.zIndex = '10';
			audioElement.style.position = 'relative';
		}
	}

	document.querySelector('#generate_podcast').addEventListener('click', addSplashScreen);

	// Use a MutationObserver to watch for changes in the audio element
	const observer = new MutationObserver((mutations) => {
		mutations.forEach((mutation) => {
			if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
				removeSplashScreen();
				positionGenerationNote();
			}
		});
	});

	observer.observe(document.querySelector('.audio-wrap'), { childList: true, subtree: true });

	// Position the note on initial load
	window.addEventListener('load', positionGenerationNote);
	""")

if __name__ == "__main__":
	iface.launch(share=True)
