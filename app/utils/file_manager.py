import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union

# from config import PDF_DIR, PODCAST_DIR, SUMMARY_DIR


class FileManager:
    """
    Gerenciador de arquivos para a aplicação Paper-to-Podcast.
    Fornece métodos para manipular e organizar arquivos do aplicativo.
    """

    # @staticmethod
    # def ensure_directories() -> None:
    #     """
    #     Garante que os diretórios necessários para o aplicativo existem.
    #     """
    #     for dir_path in [PDF_DIR, SUMMARY_DIR, PODCAST_DIR]:
    #         dir_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def list_files(directory: Path, extension: str = "") -> List[Path]:
        """
        Lista todos os arquivos em um diretório com a extensão especificada.

        Args:
            directory: Diretório para listar os arquivos
            extension: Extensão dos arquivos a serem listados (opcional)

        Returns:
            Lista de caminhos dos arquivos encontrados
        """
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)

        if extension:
            return sorted(
                directory.glob(f"*.{extension}"),
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )

        return sorted(
            directory.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True
        )

    @staticmethod
    def save_file(
        source_path: Union[str, Path], target_dir: Path, rename: bool = True
    ) -> Path:
        """
        Salva um arquivo no diretório de destino com opção de renomear.

        Args:
            source_path: Caminho do arquivo de origem
            target_dir: Diretório de destino
            rename: Se True, renomeia o arquivo adicionando timestamp

        Returns:
            Caminho do arquivo salvo
        """
        source_path = Path(source_path)

        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)

        if rename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_filename = f"{timestamp}_{source_path.name}"
        else:
            dest_filename = source_path.name

        dest_path = target_dir / dest_filename

        shutil.copy2(source_path, dest_path)
        return dest_path

    @staticmethod
    def delete_file(file_path: Union[str, Path]) -> bool:
        """
        Exclui um arquivo com segurança.

        Args:
            file_path: Caminho do arquivo a ser excluído

        Returns:
            True se o arquivo foi excluído com sucesso, False caso contrário
        """
        try:
            Path(file_path).unlink(missing_ok=True)
            return True
        except Exception:
            return False

    @staticmethod
    def get_file_metadata(file_path: Union[str, Path]) -> Dict:
        """
        Obtém metadados de um arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Dicionário com metadados do arquivo
        """
        path = Path(file_path)

        if not path.exists():
            return {
                "exists": False,
                "filename": path.name,
                "error": "Arquivo não encontrado",
            }

        return {
            "exists": True,
            "filename": path.name,
            "extension": path.suffix.lower(),
            "size_bytes": path.stat().st_size,
            "size_kb": round(path.stat().st_size / 1024, 2),
            "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(path.stat().st_ctime).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "modified": datetime.fromtimestamp(path.stat().st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "parent_dir": str(path.parent),
        }

    @staticmethod
    def find_related_files(
        file_path: Union[str, Path], extensions: List[str]
    ) -> List[Path]:
        """
        Encontra arquivos relacionados com base no nome e extensões.

        Args:
            file_path: Caminho do arquivo base
            extensions: Lista de extensões para buscar

        Returns:
            Lista de caminhos dos arquivos relacionados
        """
        path = Path(file_path)
        base_name = path.stem
        parent_dir = path.parent

        related_files = []
        for ext in extensions:
            ext = ext if ext.startswith(".") else f".{ext}"
            related_path = parent_dir / f"{base_name}{ext}"
            if related_path.exists():
                related_files.append(related_path)

        return related_files

    @staticmethod
    def open_directory(directory: Union[str, Path]) -> bool:
        """
        Abre um diretório no explorador de arquivos do sistema.

        Args:
            directory: Caminho do diretório para abrir

        Returns:
            True se o diretório foi aberto com sucesso, False caso contrário
        """
        try:
            import platform
            import subprocess

            dir_path = str(Path(directory))

            if platform.system() == "Windows":
                os.startfile(dir_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", dir_path], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", dir_path], check=True)

            return True
        except Exception:
            return False
