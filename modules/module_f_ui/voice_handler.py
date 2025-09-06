"""
Voice Handler for Module F
Handles speech-to-text and text-to-speech functionality.
"""

import logging
import tempfile
import os
from typing import Optional, Dict, Any
import streamlit as st

logger = logging.getLogger(__name__)

class VoiceHandler:
    """Handles voice input and output functionality."""
    
    def __init__(self):
        self.whisper_available = False
        self.gtts_available = False
        
        # Check for optional dependencies
        try:
            import whisper
            self.whisper_available = True
            logger.info("Whisper (speech-to-text) available")
        except ImportError:
            logger.warning("Whisper not available - install with: pip install openai-whisper")
        
        try:
            from gtts import gTTS
            self.gtts_available = True
            logger.info("gTTS (text-to-speech) available")
        except ImportError:
            logger.warning("gTTS not available - install with: pip install gtts")
    
    def is_voice_enabled(self) -> bool:
        """Check if voice features are available."""
        return self.whisper_available or self.gtts_available
    
    def speech_to_text(self, audio_file) -> Optional[str]:
        """Convert speech to text using Whisper."""
        if not self.whisper_available:
            st.error("Speech-to-text not available. Install whisper: pip install openai-whisper")
            return None
        
        try:
            import whisper
            
            # Load Whisper model (using base model for balance of speed/accuracy)
            model = whisper.load_model("base")
            
            # Transcribe audio
            result = model.transcribe(audio_file)
            
            return result["text"].strip()
            
        except Exception as e:
            logger.error(f"Speech-to-text failed: {e}")
            st.error(f"Speech recognition failed: {e}")
            return None
    
    def text_to_speech(self, text: str, language: str = "de") -> Optional[bytes]:
        """Convert text to speech using gTTS."""
        if not self.gtts_available:
            st.error("Text-to-speech not available. Install gTTS: pip install gtts")
            return None
        
        try:
            from gtts import gTTS
            
            # Create gTTS object
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts.save(tmp_file.name)
                
                # Read audio data
                with open(tmp_file.name, "rb") as audio_file:
                    audio_data = audio_file.read()
                
                # Clean up
                os.unlink(tmp_file.name)
                
                return audio_data
                
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
            st.error(f"Speech synthesis failed: {e}")
            return None
    
    def render_voice_controls(self) -> Dict[str, Any]:
        """Render voice control UI components."""
        voice_controls = {
            'speech_input': None,
            'enable_tts': False
        }
        
        if not self.is_voice_enabled():
            st.info("🎤 Voice features available with optional dependencies:")
            st.code("pip install openai-whisper gtts")
            return voice_controls
        
        st.markdown("### 🎤 Voice Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if self.whisper_available:
                st.markdown("**Speech Input:**")
                audio_input = st.audio_input("Record your question")
                
                if audio_input is not None:
                    with st.spinner("🎤 Converting speech to text..."):
                        # Save uploaded audio to temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                            tmp_file.write(audio_input.read())
                            tmp_file_path = tmp_file.name
                        
                        # Convert to text
                        transcribed_text = self.speech_to_text(tmp_file_path)
                        
                        # Clean up
                        os.unlink(tmp_file_path)
                        
                        if transcribed_text:
                            st.success(f"🎤 Recognized: {transcribed_text}")
                            voice_controls['speech_input'] = transcribed_text
                        else:
                            st.error("Could not recognize speech")
            else:
                st.info("Speech-to-text: Install whisper")
        
        with col2:
            if self.gtts_available:
                st.markdown("**Speech Output:**")
                voice_controls['enable_tts'] = st.checkbox(
                    "Enable text-to-speech for responses",
                    help="Automatically convert AI responses to speech"
                )
            else:
                st.info("Text-to-speech: Install gTTS")
        
        return voice_controls
    
    def play_response_audio(self, text: str, language: str = "de"):
        """Generate and play audio for response text."""
        if not self.gtts_available:
            return
        
        try:
            audio_data = self.text_to_speech(text, language)
            
            if audio_data:
                st.audio(audio_data, format="audio/mp3", autoplay=True)
                
        except Exception as e:
            logger.error(f"Failed to play response audio: {e}")
            st.error("Could not generate speech audio")