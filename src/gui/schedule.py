import tkinter as tk
from tkinter import ttk

from domain.dtos.config import Config
from domain.dtos.reports import Reports
from gui.config import AlgorithmConfigGUI
from gui.data_management import DataManagementGUI
from gui.results import ResultsGUI
from ie.pdf import PDFExport


class ScheduleGUI(tk.Tk, DataManagementGUI, AlgorithmConfigGUI, ResultsGUI):
    def __init__(self):
        super().__init__()
        self.tk.call("source", "themes/azure.tcl")
        self.tk.call("set_theme", "dark")

        self.title("Generador de Horarios")
        self.geometry("600x350")
        self.setup_principal_window()

        self.pdf_exporter = PDFExport()
        self.algorithm_config = Config()
        self.data = {
            1: {},
            2: {},
            3: {},
            4: {},
            5: {},
            6: {},
            7: {},
            8: {},
            9: {},
        }
        self.classrooms = []
        self.reports = Reports()
        self.periods = ["13:40", "14:30", "15:20", "16:10",
                        "17:00", "17:50", "18:40", "19:30", "20:20"]

    def setup_principal_window(self):
        principal_frame = ttk.Frame(self)
        principal_frame.pack(expand=True, fill='both', padx=20, pady=20)

        ttk.Label(principal_frame,
                  text="Sistema de Generación de Horarios",
                  font=('MonaspiceKr Nerd Font Mono', 16)).pack(pady=20)

        buttons = [
            ("Gestión de Datos", self.open_data_management),
            ("Configurar Algoritmo", self.open_algorithm_config),
            ("Generar Horarios", self.start_generation),
            ("Ver Resultados", self.show_results),
            ("Salir", self.destroy)
        ]

        for text, command in buttons:
            ttk.Button(principal_frame, text=text, command=command,
                       width=30).pack(pady=5)


if __name__ == "__main__":
    app = ScheduleGUI()
    app.mainloop()
