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
        # Default to environment variables if not provided
        self.provider = provider or os.getenv("DEFAULT_PROVIDER", "google").lower()
        self.model_name = model_name or os.getenv("DEFAULT_MODEL", "gemini-1.5-pro")
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """
        Initializes the specific LLM based on the provider.
        """
        if self.provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment.")
            return ChatGoogleGenerativeAI(model=self.model_name, google_api_key=api_key)
        
        elif self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment.")
            return ChatOpenAI(model=self.model_name, openai_api_key=api_key)
            
        elif self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment.")
            return ChatAnthropic(model=self.model_name, anthropic_api_key=api_key)
        
        else:
            raise ValueError(f"Provider '{self.provider}' is not supported yet.")

    def chat(self, prompt: str):
        """
        A simple method to send a prompt and get a response.
        """
        return self.llm.invoke(prompt)

if __name__ == "__main__":
    # Test simple initialization
    try:
        adapter = AIAdapter()
        print(f"✅ AI Adapter initialized for provider: {adapter.provider} with model: {adapter.model_name}")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
