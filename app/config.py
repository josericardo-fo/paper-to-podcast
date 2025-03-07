import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Diretórios da aplicação
BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "pdfs"
SUMMARY_DIR = BASE_DIR / "output" / "summaries"
PODCAST_DIR = BASE_DIR / "output" / "podcasts"

# Criar diretórios necessários
PDF_DIR.mkdir(exist_ok=True, parents=True)
SUMMARY_DIR.mkdir(exist_ok=True, parents=True)
PODCAST_DIR.mkdir(exist_ok=True, parents=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")

# Configuração de LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
)

# Configurações da interface
UI_THEME = "dark"  # ou "light"
UI_DEFAULT_WIDTH = 800
UI_DEFAULT_HEIGHT = 600
