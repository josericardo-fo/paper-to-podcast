import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext, ttk
from typing import Optional

from core.podcast_generator import PodcastGenerator


class PodcastView(ttk.Frame):
    """
    View para geração e reprodução de podcasts a partir de resumos.
    """

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.podcast_generator = PodcastGenerator()
        self.current_text = None
        self.current_podcast_path = None
        self.current_title = None
        self.available_voices = []

        # Inicializar widgets
        self._create_widgets()

        # Carregar vozes disponíveis em segundo plano
        threading.Thread(target=self._load_available_voices, daemon=True).start()

    def _create_widgets(self):
        """Cria os widgets da view de podcast."""
        # Frame superior com informações
        info_frame = ttk.LabelFrame(self, text="Podcast")
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.info_var = tk.StringVar(value="Nenhum texto selecionado para podcast")
        info_label = ttk.Label(info_frame, textvariable=self.info_var)
        info_label.pack(fill=tk.X, padx=10, pady=5)

        # Frame de texto para edição
        text_frame = ttk.LabelFrame(self, text="Texto para Podcast")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            bg="#2a2a2a",
            fg="white",
            font=("Arial", 11),
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame de opções
        options_frame = ttk.Frame(self)
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        # Seleção de voz
        voice_frame = ttk.Frame(options_frame)
        voice_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(voice_frame, text="Voz:").pack(side=tk.LEFT, padx=5)
        self.voice_var = tk.StringVar(value="Rachel (Default)")
        self.voice_dropdown = ttk.Combobox(
            voice_frame,
            textvariable=self.voice_var,
            state="readonly",
            width=25,
        )
        self.voice_dropdown.pack(side=tk.LEFT, padx=5)
        self.voice_dropdown["values"] = ["Rachel (Default)", "Carregando..."]

        # Frame de ações
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        self.generate_button = ttk.Button(
            action_frame,
            text="Gerar Podcast",
            command=self._generate_podcast,
            state=tk.DISABLED,
        )
        self.generate_button.pack(side=tk.LEFT, padx=5)

        self.play_button = ttk.Button(
            action_frame,
            text="Reproduzir Podcast",
            command=self._play_podcast,
            state=tk.DISABLED,
        )
        self.play_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(
            action_frame,
            text="Abrir Pasta de Podcasts",
            command=self._open_podcast_folder,
        )
        self.save_button.pack(side=tk.RIGHT, padx=5)

        # Status do podcast
        self.status_frame = ttk.LabelFrame(self, text="Status")
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_var = tk.StringVar(value="Pronto")
        status_label = ttk.Label(self.status_frame, textvariable=self.status_var)
        status_label.pack(fill=tk.X, padx=10, pady=5)

    def prepare_podcast(self, text: str, title: Optional[str] = None):
        """
        Prepara a view para gerar um podcast a partir de um texto.
        """
        self.current_text = text
        self.current_title = title or "Novo Podcast"
        self.info_var.set(f"Podcast: {self.current_title}")

        # Inserir texto na área de texto
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, text)

        # Habilitar botão de geração
        self.generate_button.config(state=tk.NORMAL)

        # Reset do status
        self.status_var.set("Pronto para gerar podcast")
        self.current_podcast_path = None
        self.play_button.config(state=tk.DISABLED)

    def _generate_podcast(self):
        """Gera um podcast a partir do texto atual."""
        if not self.current_text:
            self.app.set_status("Nenhum texto disponível para gerar podcast")
            return

        # Obter texto atualizado da área de texto
        text = self.text_area.get(1.0, tk.END)

        # Obter ID da voz selecionada
        voice_name = self.voice_var.get()
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel (padrão)

        for voice in self.available_voices:
            if voice["name"] in voice_name:
                voice_id = voice["voice_id"]
                break

        # Desabilitar botões durante geração
        self.generate_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.DISABLED)

        # Atualizar status
        self.status_var.set("Gerando podcast... Aguarde.")
        self.app.set_status("Gerando podcast...", show_progress=True)

        # Executar em thread separada
        def generate_task():
            try:
                result = self.podcast_generator.generate_podcast(
                    text, voice_id=voice_id
                )

                # Atualizar UI no thread principal
                if "error" in result:
                    self.after(
                        0, lambda: self._handle_generation_error(result["error"])
                    )
                else:
                    self.after(0, lambda: self._handle_generation_success(result))
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda: self._handle_generation_error(error_msg))

        threading.Thread(target=generate_task, daemon=True).start()

    def _handle_generation_success(self, result):
        """Manipula sucesso na geração do podcast."""
        self.current_podcast_path = result["audio_path"]

        # Atualizar status
        duration = result["metadata"]["duration_seconds"]
        self.status_var.set(
            f"Podcast gerado com sucesso! Duração aproximada: {duration} segundos"
        )
        self.app.set_status("Podcast gerado com sucesso!")

        # Habilitar botões
        self.generate_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.NORMAL)

    def _handle_generation_error(self, error_msg):
        """Manipula erro na geração do podcast."""
        self.status_var.set(f"Erro: {error_msg}")
        self.app.set_status(f"Erro na geração do podcast: {error_msg}")

        # Habilitar botão de nova tentativa
        self.generate_button.config(state=tk.NORMAL)

    def _play_podcast(self):
        """Reproduz o podcast gerado."""
        if (
            not self.current_podcast_path
            or not Path(self.current_podcast_path).exists()
        ):
            self.status_var.set("Nenhum podcast disponível para reprodução")
            return

        # Usar o player padrão do sistema
        import platform
        import subprocess

        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", self.current_podcast_path])
            elif platform.system() == "Windows":
                os.startfile(self.current_podcast_path)
            else:  # Linux
                subprocess.Popen(["xdg-open", self.current_podcast_path])

            self.status_var.set("Reproduzindo podcast...")
        except Exception as e:
            self.status_var.set(f"Erro ao reproduzir: {str(e)}")


def _open_podcast_folder(self):
    """Abre a pasta onde os podcasts estão salvos."""
    from utils.file_manager import FileManager

    from app.config import PODCAST_DIR

    FileManager.open_directory(PODCAST_DIR)

    def _load_available_voices(self):
        """Carrega as vozes disponíveis da API ElevenLabs."""
        try:
            voices = self.podcast_generator.list_available_voices()
            voice_names = ["Rachel (Default)"]

            for voice in voices:
                if voice["name"] != "Rachel":  # Rachel já é o padrão
                    name_with_category = f"{voice['name']} ({voice['category']})"
                    voice_names.append(name_with_category)
                    # Guardar mapeamento para uso posterior
                    voice["display_name"] = name_with_category

            self.available_voices = voices

            # Atualizar dropdown no thread principal
            self.after(0, lambda: self._update_voice_dropdown(voice_names))
        except Exception as e:
            print(f"Erro ao carregar vozes: {e}")
            self.after(0, lambda: self._update_voice_dropdown(["Rachel (Default)"]))

    def _update_voice_dropdown(self, voices):
        """Atualiza o dropdown com as vozes disponíveis."""
        self.voice_dropdown["values"] = voices
        self.voice_var.set(voices[0])
