import queue
import threading
import tkinter as tk
from tkinter import ttk

from config import UI_DEFAULT_HEIGHT, UI_DEFAULT_WIDTH, UI_THEME
from ui.views.podcast_view import PodcastView
from ui.views.summary_view import SummaryView
from ui.views.upload_view import UploadView


class PaperToPodcastApp(tk.Tk):
    """
    Aplicação principal para converter papers em podcasts.
    """

    def __init__(self):
        super().__init__()

        self.title("Paper to Podcast")
        self.geometry(f"{UI_DEFAULT_WIDTH}x{UI_DEFAULT_HEIGHT}")
        self.minsize(600, 500)

        # Configurar estilo
        self.style = ttk.Style()
        if UI_THEME == "dark":
            self._apply_dark_theme()
        else:
            self._apply_light_theme()

        # Gerenciador de tarefas em segundo plano
        self.task_queue = queue.Queue()

        # Configurar a interface
        self._create_widgets()

        # Inicializar o processamento em segundo plano
        self._start_background_worker()

    def _create_widgets(self):
        """Cria os widgets principais da aplicação."""
        # Criar notebook (abas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Inicializar views
        self.upload_view = UploadView(self.notebook, self)
        self.notebook.add(self.upload_view, text="Upload PDF")

        self.summary_view = SummaryView(self.notebook, self)
        self.notebook.add(self.summary_view, text="Resumo")

        self.podcast_view = PodcastView(self.notebook, self)
        self.notebook.add(self.podcast_view, text="Podcast")

        # Barra de status
        self.status_var = tk.StringVar(value="Pronto")
        self.status_bar = ttk.Label(
            self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Barra de progresso
        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(side=tk.BOTTOM, fill=tk.X, before=self.status_bar)
        self.progress.pack_forget()  # Esconder inicialmente

    def set_status(self, message, show_progress=False):
        """Atualiza a barra de status e controla a barra de progresso."""
        self.status_var.set(message)

        if show_progress:
            self.progress.pack(side=tk.BOTTOM, fill=tk.X, before=self.status_bar)
            self.progress.start(10)
        else:
            self.progress.stop()
            self.progress.pack_forget()

    def add_task(self, task, *args, **kwargs):
        """Adiciona uma tarefa à fila para execução em segundo plano."""
        self.task_queue.put((task, args, kwargs))

    def _start_background_worker(self):
        """Inicia o processamento de tarefas em segundo plano."""

        def worker():
            while True:
                task, args, kwargs = self.task_queue.get()
                try:
                    task(*args, **kwargs)
                except Exception as e:
                    print(f"Erro na execução da tarefa: {e}")
                finally:
                    self.task_queue.task_done()

        threading.Thread(target=worker, daemon=True).start()

    def _apply_dark_theme(self):
        """Aplica tema escuro à aplicação."""
        self.configure(bg="#2e2e2e")
        self.style.theme_use("clam")

        # Configurar cores para o tema escuro
        self.style.configure("TFrame", background="#2e2e2e")
        self.style.configure("TLabel", background="#2e2e2e", foreground="#ffffff")
        self.style.configure("TButton", background="#3a3a3a", foreground="#ffffff")
        self.style.configure("TNotebook", background="#2e2e2e", foreground="#ffffff")
        self.style.configure(
            "TNotebook.Tab", background="#3a3a3a", foreground="#ffffff"
        )

        # Adicionar mais configurações de estilo conforme necessário

    def _apply_light_theme(self):
        """Aplica tema claro à aplicação."""
        self.configure(bg="#f0f0f0")
        self.style.theme_use("clam")

        # Configurar cores para o tema claro
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", foreground="#000000")
        self.style.configure("TButton", background="#e0e0e0", foreground="#000000")
        self.style.configure("TNotebook", background="#f0f0f0")
        self.style.configure(
            "TNotebook.Tab", background="#e0e0e0", foreground="#000000"
        )
