import gradio as gr
import os
from podcastfy.client import generate_podcast
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_api_key(key_name, ui_value):
    return ui_value if ui_value else os.getenv(key_name)

def process_inputs(
    text_input, 
    urls_input, 
    gemini_key,
    openai_key,
    elevenlabs_key,
    word_count,
    conversation_style,
    roles_person1,
    roles_person2,
    dialogue_structure,
    podcast_name,
    podcast_tagline,
    tts_model,
    creativity_level,
    user_instructions
):
    try:
        # Set API keys
        os.environ["GEMINI_API_KEY"] = get_api_key("GEMINI_API_KEY", gemini_key)
        os.environ["OPENAI_API_KEY"] = get_api_key("OPENAI_API_KEY", openai_key)
        os.environ["ELEVENLABS_API_KEY"] = get_api_key("ELEVENLABS_API_KEY", elevenlabs_key)
        
        # Process URLs
        urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
        
        # Prepare conversation config
        conversation_config = {
            "word_count": word_count,
            "conversation_style": conversation_style.split(','),
            "roles_person1": roles_person1,
            "roles_person2": roles_person2,
            "dialogue_structure": dialogue_structure.split(','),
            "podcast_name": podcast_name,
            "podcast_tagline": podcast_tagline,
            "creativity": creativity_level,
            "user_instructions": user_instructions
        }
        
        # Generate podcast
        audio_file = generate_podcast(
            urls=urls if urls else None,
            text=text_input if text_input else None,
            tts_model=tts_model,
            conversation_config=conversation_config
        )
        
        return audio_file
        
    except Exception as e:
        return str(e)

# Create Gradio interface with updated theme
with gr.Blocks(
    title="Podcastfy.ai",
    theme=gr.themes.Base(
        primary_hue="blue",
        secondary_hue="slate",
        neutral_hue="slate"
    )
) as demo:
    # Add theme toggle at the top
    with gr.Row():
        gr.Markdown("# 🎙️ Podcastfy.ai")
        theme_btn = gr.Button("🌓", scale=0, min_width=0)

    gr.Markdown("An Open Source alternative to NotebookLM's podcast feature")
    gr.Markdown("For full customization, please check Python package on github (www.podcastfy.ai).")
    
    with gr.Tab("Content"):
        # API Keys Section
        gr.Markdown("### 🔑 API Keys")
        with gr.Accordion("Configure API Keys", open=True):
            gemini_key = gr.Textbox(
                label="Gemini API Key", 
                type="password", 
                value=os.getenv("GEMINI_API_KEY", ""),
                info="Required"
            )
            openai_key = gr.Textbox(
                label="OpenAI API Key", 
                type="password", 
                value=os.getenv("OPENAI_API_KEY", ""),
                info="Required only if using OpenAI TTS model - use Edge for a free option"
            )
            elevenlabs_key = gr.Textbox(
                label="ElevenLabs API Key",
                type="password",
                value=os.getenv("ELEVENLABS_API_KEY", ""),
                info="Required only if using ElevenLabs TTS model - use Edge for a free option"
            )
        
        # Content Input Section
        gr.Markdown("### 📝 Input Content")
        with gr.Group():
            text_input = gr.Textbox(
                label="Text Input", 
                placeholder="Enter or paste text here...", 
                lines=3,
                value="The wonderful world of AI"
            )
            urls_input = gr.Textbox(
                label="URLs", 
                placeholder="Enter URLs (one per line) - supports websites, YouTube videos, etc.", 
                lines=3,
                value="https://en.wikipedia.org/wiki/Artificial_intelligence"
            )
        
        # Customization Section
        gr.Markdown("### ⚙️ Customization Options")
        with gr.Accordion("Configure Podcast Settings", open=True):
            # Basic Settings
            gr.Markdown("#### 📊 Basic Settings")
            word_count = gr.Slider(
                minimum=500, 
                maximum=5000, 
                value=2000, 
                step=100, 
                label="Word Count",
                info="Target word count for the generated content"
            )
            
            conversation_style = gr.Textbox(
                label="Conversation Style", 
                value="engaging,fast-paced,enthusiastic",
                info="Comma-separated list of styles to apply to the conversation"
            )
            
            # Roles and Structure
            gr.Markdown("#### 👥 Roles and Structure")
            roles_person1 = gr.Textbox(
                label="Role of First Speaker",
                value="main summarizer",
                info="Role of the first speaker in the conversation"
            )
            
            roles_person2 = gr.Textbox(
                label="Role of Second Speaker",
                value="questioner/clarifier",
                info="Role of the second speaker in the conversation"
            )
            
            dialogue_structure = gr.Textbox(
                label="Dialogue Structure",
                value="Introduction,Main Content Summary,Conclusion",
                info="Comma-separated list of dialogue sections"
            )
            
            # Podcast Identity
            gr.Markdown("#### 🎙️ Podcast Identity")
            podcast_name = gr.Textbox(
                label="Podcast Name",
                value="PODCASTFY",
                info="Name of the podcast"
            )
            
            podcast_tagline = gr.Textbox(
                label="Podcast Tagline",
                value="YOUR PERSONAL GenAI PODCAST",
                info="Tagline or subtitle for the podcast"
            )
            
            # Voice Settings
            gr.Markdown("#### 🗣️ Voice Settings")
            tts_model = gr.Radio(
                choices=["openai", "elevenlabs", "edge"],
                value="edge",
                label="Text-to-Speech Model",
                info="Choose the voice generation model (edge is free, others require API keys)"
            )
            
            # Advanced Settings
            gr.Markdown("#### 🔧 Advanced Settings")
            creativity_level = gr.Slider(
                minimum=0, 
                maximum=1, 
                value=0.7, 
                step=0.1, 
                label="Creativity Level",
                info="Controls the creativity of the generated conversation (0 for focused/factual, 1 for more creative)"
            )
            
            user_instructions = gr.Textbox(
                label="Custom Instructions",
                value="",
                lines=2,
                placeholder="Add any specific instructions to guide the conversation...",
                info="Optional instructions to guide the conversation focus and topics"
            )
    
    # Output Section
    gr.Markdown("### 🎵 Generated Output")
    with gr.Group():
        generate_btn = gr.Button("🎙️ Generate Podcast", variant="primary")
        audio_output = gr.Audio(
            type="filepath", 
            label="Generated Podcast"
        )
        
    # Footer
    gr.Markdown("---")
    gr.Markdown("Created with ❤️ using [Podcastfy](https://github.com/souzatharsis/podcastfy)")
    
    # Handle generation
    generate_btn.click(
        process_inputs,
        inputs=[
            text_input, urls_input,
            gemini_key, openai_key, elevenlabs_key,
            word_count, conversation_style,
            roles_person1, roles_person2,
            dialogue_structure, podcast_name,
            podcast_tagline, tts_model,
            creativity_level, user_instructions
        ],
        outputs=audio_output
    )

    # Add theme toggle functionality
    theme_btn.click(
        None,
        None,
        None,
        js="""
        function() {
            document.querySelector('body').classList.toggle('dark');
            return [];
        }
        """
    )

if __name__ == "__main__":
    demo.queue().launch(share=True)
