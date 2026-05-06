import os
from typing import Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Load environment variables from .env
load_dotenv()

class AIAdapter:
    """
    Adapter class to standardize communication with different AI providers.
    """
    
    def __init__(self, provider: Optional[str] = None, model_name: Optional[str] = None):
        # Default keys
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        # Try to get from Streamlit Secrets (Cloud)
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                self.google_api_key = st.secrets.get("GOOGLE_API_KEY") or self.google_api_key
                self.openai_api_key = st.secrets.get("OPENAI_API_KEY") or self.openai_api_key
                self.anthropic_api_key = st.secrets.get("ANTHROPIC_API_KEY") or self.anthropic_api_key
                
                cloud_provider = st.secrets.get("DEFAULT_PROVIDER")
                cloud_model = st.secrets.get("DEFAULT_MODEL")
            else:
                cloud_provider = None
                cloud_model = None
        except:
            cloud_provider = None
            cloud_model = None

        self.provider = provider or cloud_provider or os.getenv("DEFAULT_PROVIDER", "google").lower()
        self.model_name = model_name or cloud_model or os.getenv("DEFAULT_MODEL", "gemini-1.5-pro")
        
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """
        Initializes the specific LLM based on the provider.
        """
        if self.provider == "google":
            if not self.google_api_key:
                raise ValueError("GOOGLE_API_KEY not found. Please check your .env or Streamlit Secrets.")
            return ChatGoogleGenerativeAI(model=self.model_name, google_api_key=self.google_api_key)
        
        elif self.provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY not found. Please check your .env or Streamlit Secrets.")
            return ChatOpenAI(model=self.model_name, openai_api_key=self.openai_api_key)
            
        elif self.provider == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not found. Please check your .env or Streamlit Secrets.")
            return ChatAnthropic(model=self.model_name, anthropic_api_key=self.anthropic_api_key)
        
        else:
            raise ValueError(f"Provider '{self.provider}' is not supported yet.")

    def chat(self, prompt: str) -> dict:
        """
        Sends a prompt and returns a dictionary with 'content' and 'usage'.
        """
        response = self.llm.invoke(prompt)
        
        # Extract content
        content = response.content if hasattr(response, 'content') else str(response)
        if isinstance(content, list):
            content = "".join([str(part.get('text', part)) if isinstance(part, dict) else str(part) for part in content])
        
        # Extract Usage (Metrik biaya)
        usage = {}
        if hasattr(response, 'response_metadata'):
            usage = response.response_metadata.get('token_usage', {})
            # Handle OpenAI style usage if needed
            if not usage:
                usage = response.response_metadata.get('usage', {})

        return {
            "content": str(content).strip(),
            "usage": usage
        }
