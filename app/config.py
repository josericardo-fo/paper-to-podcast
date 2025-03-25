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

# Configuração da OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Configuração de LLM
llm = ChatOpenAI(
    model=OPENAI_MODEL,
    openai_api_key=OPENAI_API_KEY,
)
