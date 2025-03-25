import re
from pathlib import Path
from typing import List, Tuple

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
    def remove_references(documents: List[Document]) -> Tuple[List[Document], bool]:
        """
        Remove seções de referências dos documentos.

        Args:
            documents: Lista de documentos Langchain extraídos do PDF

        Returns:
            Tuple contendo:
                - Lista de documentos com referências removidas
                - Boolean indicando se referências foram encontradas e removidas
        """
        if not documents:
            return documents, False

        # Padrões comuns que indicam o início de seções de referências
        reference_patterns = [
            r"^references$",
            r"^referências$",
            # r"^bibliografia$",
            # r"^referências bibliográficas$",
            # r"^works cited$",
            # r"^literatura citada$",
            # r"^cited literature$",
            # r"^citation$",
            # r"^citations$",
            # r"^reference list$",
        ]

        # Combinar padrões em uma expressão regular (case insensitive)
        combined_pattern = "|".join(reference_patterns)

        cleaned_documents = []
        references_removed = False

        # Procurar pela seção de referências
        for _, doc in enumerate(documents):
            content = doc.page_content

            # Verificar se este documento contém o início da seção de referências
            match = re.search(combined_pattern, content.lower(), re.MULTILINE)

            if match:
                # Obter apenas o conteúdo antes da seção de referências
                ref_start_pos = match.start()
                if ref_start_pos > 0:
                    # Atualizar o conteúdo para incluir apenas o que está antes das referências
                    doc.page_content = content[:ref_start_pos].strip()
                    cleaned_documents.append(doc)

                # Não incluir páginas após a seção de referências
                references_removed = True
                break

            # Se não encontrou referências, manter o documento como está
            cleaned_documents.append(doc)

        # Se já encontrou a seção de referências, não incluir os documentos seguintes
        if references_removed:
            return cleaned_documents, True

        return documents, False

    @staticmethod
    def get_pdf_metadata(pdf_path: Path) -> dict:
        """Extrai metadados do PDF."""
        return FileManager.get_file_metadata(pdf_path)
