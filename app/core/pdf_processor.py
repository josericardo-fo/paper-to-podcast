from pathlib import Path
from typing import List

from config import PDF_DIR
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from utils.file_manager import FileManager


class PDFProcessor:
    """
    Gerencia o processamento de arquivos PDF, incluindo carregamento,
    armazenamento e extração de conteúdo.
    """

    @staticmethod
    def get_all_pdfs() -> List[Path]:
        """Retorna lista de todos os PDFs armazenados."""
        return FileManager.list_files(PDF_DIR, "pdf")

    @staticmethod
    def save_pdf(filepath: str) -> Path:
        """
        Salva um PDF no diretório de PDFs.
        Retorna o caminho do arquivo salvo.
        """
        return FileManager.save_file(filepath, PDF_DIR, rename=True)

    @staticmethod
    def extract_text(pdf_path: Path) -> List[Document]:
        """
        Extrai texto do PDF usando PyPDFLoader.
        Retorna lista de documentos Langchain.
        """
        try:
            loader = PyPDFLoader(str(pdf_path))
            return loader.load()
        except Exception as e:
            print(f"Erro ao extrair texto do PDF: {e}")
            return []

    @staticmethod
    def get_pdf_metadata(pdf_path: Path) -> dict:
        """Extrai metadados do PDF."""
        return FileManager.get_file_metadata(pdf_path)
