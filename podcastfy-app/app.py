import gradio as gr
import os
import tempfile
import logging
from podcastfy.client import generate_podcast
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_api_key(key_name, ui_value):
    return ui_value if ui_value else os.getenv(key_name)

def process_inputs(
    text_input, 
    urls_input,
    pdf_files,
    image_files,
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
        logger.info("Starting podcast generation process")
        
        # API key handling
        logger.debug("Setting API keys")
        os.environ["GEMINI_API_KEY"] = get_api_key("GEMINI_API_KEY", gemini_key)
        
        if tts_model == "openai":
            logger.debug("Setting OpenAI API key")
            if not openai_key and not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OpenAI API key is required when using OpenAI TTS model")
            os.environ["OPENAI_API_KEY"] = get_api_key("OPENAI_API_KEY", openai_key)
            
        if tts_model == "elevenlabs":
            logger.debug("Setting ElevenLabs API key")
            if not elevenlabs_key and not os.getenv("ELEVENLABS_API_KEY"):
                raise ValueError("ElevenLabs API key is required when using ElevenLabs TTS model")
            os.environ["ELEVENLABS_API_KEY"] = get_api_key("ELEVENLABS_API_KEY", elevenlabs_key)
        
        # Process URLs
        urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
        logger.debug(f"Processed URLs: {urls}")
        
        temp_files = []
        temp_dirs = []
        
        # Handle PDF files
        if pdf_files is not None and len(pdf_files) > 0:
            logger.info(f"Processing {len(pdf_files)} PDF files")
            pdf_temp_dir = tempfile.mkdtemp()
            temp_dirs.append(pdf_temp_dir)
            
            for i, pdf_file in enumerate(pdf_files):
                pdf_path = os.path.join(pdf_temp_dir, f"input_pdf_{i}.pdf")
                temp_files.append(pdf_path)
                
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_file)
                urls.append(pdf_path)
                logger.debug(f"Saved PDF {i} to {pdf_path}")
        
        # Handle image files
        image_paths = []
        if image_files is not None and len(image_files) > 0:
            logger.info(f"Processing {len(image_files)} image files")
            img_temp_dir = tempfile.mkdtemp()
            temp_dirs.append(img_temp_dir)
            
            for i, img_file in enumerate(image_files):
                # Get file extension from the original name in the file tuple
                original_name = img_file.orig_name if hasattr(img_file, 'orig_name') else f"image_{i}.jpg"
                extension = original_name.split('.')[-1]
                
                logger.debug(f"Processing image file {i}: {original_name}")
                img_path = os.path.join(img_temp_dir, f"input_image_{i}.{extension}")
                temp_files.append(img_path)
                
                try:
                    # Write the bytes directly to the file
                    with open(img_path, 'wb') as f:
                        if isinstance(img_file, (tuple, list)):
                            f.write(img_file[1])  # Write the bytes content
                        else:
                            f.write(img_file)     # Write the bytes directly
                    image_paths.append(img_path)
                    logger.debug(f"Saved image {i} to {img_path}")
                except Exception as e:
                    logger.error(f"Error saving image {i}: {str(e)}")
                    raise
        
        # Prepare conversation config
        logger.debug("Preparing conversation config")
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
        logger.info("Calling generate_podcast function")
        logger.debug(f"URLs: {urls}")
        logger.debug(f"Image paths: {image_paths}")
        logger.debug(f"Text input present: {'Yes' if text_input else 'No'}")
        
        audio_file = generate_podcast(
            urls=urls if urls else None,
            text=text_input if text_input else None,
            image_paths=image_paths if image_paths else None,
            tts_model=tts_model,
            conversation_config=conversation_config
        )
        
        logger.info("Podcast generation completed")
        
        # Cleanup
        logger.debug("Cleaning up temporary files")
        for file_path in temp_files:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug(f"Removed temp file: {file_path}")
        for dir_path in temp_dirs:
            if os.path.exists(dir_path):
                os.rmdir(dir_path)
                logger.debug(f"Removed temp directory: {dir_path}")
        
        return audio_file
        
    except Exception as e:
        logger.error(f"Error in process_inputs: {str(e)}", exc_info=True)
        # Cleanup on error
        for file_path in temp_files:
            if os.path.exists(file_path):
                os.unlink(file_path)
        for dir_path in temp_dirs:
            if os.path.exists(dir_path):
                os.rmdir(dir_path)
        return str(e)

# Create Gradio interface with updated theme
with gr.Blocks(
    title="Podcastfy.ai",
    theme=gr.themes.Base(
        primary_hue="blue",
        secondary_hue="slate",
        neutral_hue="slate"
    ),
    css="""
        /* Move toggle arrow to left side */
        .gr-accordion {
            --accordion-arrow-size: 1.5em;
        }
        .gr-accordion > .label-wrap {
            flex-direction: row !important;
            justify-content: flex-start !important;
            gap: 1em;
        }
        .gr-accordion > .label-wrap > .icon {
            order: -1;
        }
    """
) as demo:
    # Add theme toggle at the top
    with gr.Row():
        gr.Markdown("# 🎙️ Podcastfy.ai")
        theme_btn = gr.Button("🌓", scale=0, min_width=0)

    gr.Markdown("An Open Source alternative to NotebookLM's podcast feature")
    gr.Markdown("For full customization, please check Python package on github (www.podcastfy.ai).")
    
    with gr.Tab("Content"):
        # API Keys Section
        gr.Markdown(
            """
            <h2 style='color: #2196F3; margin-bottom: 10px; padding: 10px 0;'>
                🔑 API Keys
            </h2>
            """,
            elem_classes=["section-header"]
        )
        with gr.Accordion("Configure API Keys", open=False):
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
                info="Required only if using OpenAI TTS model"
            )
            elevenlabs_key = gr.Textbox(
                label="ElevenLabs API Key",
                type="password",
                value=os.getenv("ELEVENLABS_API_KEY", ""),
                info="Required only if using ElevenLabs TTS model [recommended]"
            )
        
        # Content Input Section
        gr.Markdown(
            """
            <h2 style='color: #2196F3; margin-bottom: 10px; padding: 10px 0;'>
                📝 Input Content
            </h2>
            """,
            elem_classes=["section-header"]
        )
        with gr.Accordion("Configure Input Content", open=False):
            with gr.Group():
                text_input = gr.Textbox(
                    label="Text Input", 
                    placeholder="Enter or paste text here...", 
                    lines=3
                )
                urls_input = gr.Textbox(
                    label="URLs", 
                    placeholder="Enter URLs (one per line) - supports websites and YouTube videos.", 
                    lines=3
                )
                
                # Place PDF and Image uploads side by side
                with gr.Row():
                    with gr.Column():
                        pdf_files = gr.Files(  # Changed from gr.File to gr.Files
                            label="Upload PDFs",  # Updated label
                            file_types=[".pdf"],
                            type="binary"
                        )
                        gr.Markdown("*Upload one or more PDF files to generate podcast from*", elem_classes=["file-info"])
                    
                    with gr.Column():
                        image_files = gr.Files(
                            label="Upload Images",
                            file_types=["image"],
                            type="binary"
                        )
                        gr.Markdown("*Upload one or more images to generate podcast from*", elem_classes=["file-info"])
        
        # Customization Section
        gr.Markdown(
            """
            <h2 style='color: #2196F3; margin-bottom: 10px; padding: 10px 0;'>
                ⚙️ Customization Options
            </h2>
            """,
            elem_classes=["section-header"]
        )
        with gr.Accordion("Configure Podcast Settings", open=False):
            # Basic Settings
            gr.Markdown(
                """
                <h3 style='color: #1976D2; margin: 15px 0 10px 0;'>
                    📊 Basic Settings
                </h3>
                """,
            )
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
            gr.Markdown(
                """
                <h3 style='color: #1976D2; margin: 15px 0 10px 0;'>
                    👥 Roles and Structure
                </h3>
                """,
            )
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
            gr.Markdown(
                """
                <h3 style='color: #1976D2; margin: 15px 0 10px 0;'>
                    🎙️ Podcast Identity
                </h3>
                """,
            )
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
            gr.Markdown(
                """
                <h3 style='color: #1976D2; margin: 15px 0 10px 0;'>
                    🗣️ Voice Settings
                </h3>
                """,
            )
            tts_model = gr.Radio(
                choices=["openai", "elevenlabs", "edge"],
                value="edge",
                label="Text-to-Speech Model",
                info="Choose the voice generation model (edge is free but of low quality, others are superior but require API keys)"
            )
            
            # Advanced Settings
            gr.Markdown(
                """
                <h3 style='color: #1976D2; margin: 15px 0 10px 0;'>
                    🔧 Advanced Settings
                </h3>
                """,
            )
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
    gr.Markdown(
        """
        <h2 style='color: #2196F3; margin-bottom: 10px; padding: 10px 0;'>
            🎵 Generated Output
        </h2>
        """,
        elem_classes=["section-header"]
    )
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
            text_input, urls_input, pdf_files, image_files,
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
