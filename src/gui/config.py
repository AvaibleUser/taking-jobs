import tkinter as tk
from tkinter import ttk

from attrs import asdict

from domain.dtos.config import Config


class AlgorithmConfigGUI:
    def open_algorithm_config(self):
        window = tk.Toplevel(self)
        window.title("Configuración del Algoritmo")

        parameters = [
            ("Tamaño de población:", "pop_size"),
            ("Máximo de generaciones:", "max_generations"),
            ("Valor de aptitud objetivo (%):", "fitness_objective"),
            ("Tasa de cruce (%):", "crossover_rate"),
            ("Tasa de intercambio en cruce (%):", "swap_prob"),
            ("Tasa de mutación (%):", "mutation_rate"),
            ("Tasa de inversión en mutación (%):", "inversion_rate"),
            ("Porcentaje élite (%):", "elite_percent")
        ]

        self.touch_config = {
            "pop_size": self.algorithm_config.pop_size,
            "max_generations": self.algorithm_config.max_generations,
            "fitness_objective": self.algorithm_config.fitness_objective,
            "crossover_rate": self.algorithm_config.crossover_rate,
            "swap_prob": self.algorithm_config.swap_prob,
            "mutation_rate": self.algorithm_config.mutation_rate,
            "inversion_rate": self.algorithm_config.inversion_rate,
            "elite_percent": self.algorithm_config.elite_percent,
        }

        frame = ttk.Frame(window, padding=20)
        frame.pack(expand=True)

        for i, (texto, var) in enumerate(parameters):
            ttk.Label(frame, text=texto).grid(
                row=i, column=0, sticky='e', pady=5)
            entry = ttk.Entry(frame)
            entry.insert(0, str(self.touch_config[var]))
            entry.grid(row=i, column=1, pady=5)
            self.touch_config[var] = entry

        def save_config():
            config = asdict(self.algorithm_config)
            for key, value in self.touch_config.items():
                config[key] = value.get()

            self.algorithm_config = Config(**config)

            window.destroy()

        ttk.Button(frame, text="Guardar Configuración",
                   command=save_config).grid(row=len(parameters), columnspan=2, pady=10)
