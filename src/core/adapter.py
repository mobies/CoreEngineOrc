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
        # Default to environment variables or st.secrets
        try:
            import streamlit as st
            cloud_provider = st.secrets.get("DEFAULT_PROVIDER")
            cloud_model = st.secrets.get("DEFAULT_MODEL")
        except:
            cloud_provider = None
            cloud_model = None

        self.provider = provider or cloud_provider or os.getenv("DEFAULT_PROVIDER", "google").lower()
        self.model_name = model_name or cloud_model or os.getenv("DEFAULT_MODEL", "gemini-1.5-pro")
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """
        Initializes the specific LLM based on the provider, checking Streamlit Secrets if available.
        """
        google_key = os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        try:
            import streamlit as st
            google_key = st.secrets.get("GOOGLE_API_KEY") or google_key
            openai_key = st.secrets.get("OPENAI_API_KEY") or openai_key
            anthropic_key = st.secrets.get("ANTHROPIC_API_KEY") or anthropic_key
        except:
            pass

        if self.provider == "google":
            if not google_key:
                raise ValueError("GOOGLE_API_KEY not found.")
            return ChatGoogleGenerativeAI(model=self.model_name, google_api_key=google_key)
        
        elif self.provider == "openai":
            if not openai_key:
                raise ValueError("OPENAI_API_KEY not found.")
            return ChatOpenAI(model=self.model_name, openai_api_key=openai_key)
            
        elif self.provider == "anthropic":
            if not anthropic_key:
                raise ValueError("ANTHROPIC_API_KEY not found.")
            return ChatAnthropic(model=self.model_name, anthropic_api_key=anthropic_key)
        
        else:
            raise ValueError(f"Provider '{self.provider}' is not supported yet.")

    def chat(self, prompt: str):
        """
        A simple method to send a prompt and get a response.
        """
        return self.llm.invoke(prompt)
