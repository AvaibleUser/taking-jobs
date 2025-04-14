import tkinter as tk
from collections import defaultdict
from threading import Thread
from tkinter import messagebox, ttk

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from algorithm.search import genetic_algorithm
from domain.dtos.gene import Gene
from domain.dtos.reports import Reports
from domain.utils.genetic import Population


class ResultsGUI:
    def table_setter(self, population: Population, reports: Reports) -> None:
        self.data = {
            1: defaultdict(str),
            2: defaultdict(str),
            3: defaultdict(str),
            4: defaultdict(str),
            5: defaultdict(str),
            6: defaultdict(str),
            7: defaultdict(str),
            8: defaultdict(str),
            9: defaultdict(str),
        }

        genes: list[Gene] = population[0].genes
        genes = sorted(genes, key=lambda g: g.period)
        self.classrooms = list(set(map(lambda g: g.classroom.name, genes)))
        genes = list(map(lambda g: (g.period, {
                     g.classroom.name: f"{g.course.name}\n{g.course.degree} | {g.course.semester} | {g.course.section}\n{g.teacher.name}"}), genes))
        any(map(lambda g: self.data[g[0]].update(g[1]), genes))

        self.reports = reports

    def show_results(self):
        s = ttk.Style()
        s.configure('Treeview', rowheight=80)

        window = tk.Toplevel(self)
        window.title("Resultados Generados")
        window.geometry("1200x800")

        table_frame = ttk.Frame(window)
        table_frame.pack(expand=True, fill='both', padx=10, pady=10)

        columns = ["Hora"] + self.classrooms
        tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        for i, period in enumerate(self.periods):
            values = [period]
            values.extend(self.data[i+1][cl] for cl in self.classrooms)
            tree.insert("", 'end', values=values)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(
            table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.show_reports()

    def show_reports(self):
        window = tk.Toplevel(self)
        window.title("Reportes")
        window.geometry("1200x800")

        notebook = ttk.Notebook(window)

        conflicts_frame = ttk.Frame(notebook)
        fig_c = plt.figure(figsize=(15, 10))
        ax_c = fig_c.add_subplot(111)
        ax_c.plot(self.reports.conflicts_per_generation)
        ax_c.set_xlabel("Generación")
        ax_c.set_ylabel("Conflictos")
        ax_c.set_title("Evolución de Conflictos por Generación")
        canvas_c = FigureCanvasTkAgg(fig_c, master=conflicts_frame)
        canvas_c.get_tk_widget().pack(pady=20)

        avg_fitness_frame = ttk.Frame(notebook)
        fig_af = plt.figure(figsize=(15, 10))
        ax_af = fig_af.add_subplot(111)
        ax_af.plot(self.reports.avg_fitnesses)
        ax_af.set_xlabel("Generación")
        ax_af.set_ylabel("Función de aptitud")
        ax_af.set_title("Evolución de la Aptitud Promedio")
        canvas_af = FigureCanvasTkAgg(fig_af, master=avg_fitness_frame)
        canvas_af.get_tk_widget().pack(pady=20)

        rest_report_frame = ttk.Frame(notebook)
        rest_report_frame.pack(expand=True, fill='both', padx=10, pady=20)

        ttk.Label(rest_report_frame,
                  text="Sistema de Generación de Horarios",
                  font=('MonaspiceKr Nerd Font Mono', 14)).pack(pady=18, side="top")

        rest_reports = [
            ("Tiempo de ejecución promedio:",
             f"{self.reports.avg_durations:.2f} segundos"),
            ("Tiempo total de ejecución:",
             f"{self.reports.total_duration:.2f} segundos"),
            ("Generaciones totales:", f"{self.reports.total_generations}"),
            ("Porcentaje de cursos continuos:",
             f"{self.reports.consecutive_courses_percent:.2f}%"),
            ("Consumo de memoria:",
             f"{self.reports.memory_consumption / 1024 / 1024:.2f} MB"),
        ]

        for text, value in rest_reports:
            labels_frame = ttk.Frame(rest_report_frame)
            labels_frame.pack(expand=True, fill='y', padx=2, pady=10)

            ttk.Label(labels_frame, text="").pack(side=tk.LEFT, padx=2)
            ttk.Label(labels_frame, text=text).pack(side=tk.LEFT, padx=2)
            ttk.Label(labels_frame, text=value).pack(side=tk.RIGHT, padx=2)
            ttk.Label(labels_frame, text="").pack(side=tk.RIGHT, padx=2)

        ttk.Button(rest_report_frame, text="Exportar a PDF",
                   command=self.export_pdf).pack(pady=10)

        notebook.add(rest_report_frame, text="Datos generales")
        notebook.add(conflicts_frame, text="Conflictos vs generación")
        notebook.add(avg_fitness_frame,
                     text="Funcion de aptitud vs generación")
        notebook.pack(expand=True, fill='both')

    def start_generation(self):
        progress_window = tk.Toplevel(self)
        progress_window.title("Progreso de Generación")

        progress_percent = tk.DoubleVar(value=0)

        ttk.Label(progress_window, text="Generando horarios...").pack(pady=10)
        progress = ttk.Progressbar(
            progress_window, variable=progress_percent, maximum=1)
        progress.pack(pady=10)
        progress.start()

        def start_generation():
            population, reports = genetic_algorithm(
                int(self.algorithm_config.pop_size),
                float(self.algorithm_config.crossover_rate) / 100,
                float(self.algorithm_config.swap_prob) / 100,
                float(self.algorithm_config.mutation_rate) / 100,
                float(self.algorithm_config.inversion_rate) / 100,
                int(self.algorithm_config.max_generations),
                float(self.algorithm_config.elite_percent) / 100,
                float(self.algorithm_config.fitness_objective) / 100,
                progress_percent.set)

            self.table_setter(population, reports)

            self.end_generation(progress_window)

        Thread(target=start_generation).start()

    def end_generation(self, window):
        window.destroy()
        messagebox.showinfo("Éxito", "Horarios generados correctamente")
