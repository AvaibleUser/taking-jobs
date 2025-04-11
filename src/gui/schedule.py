import tkinter as tk
from collections import defaultdict
from datetime import datetime, time
from functools import partial
from itertools import groupby
from threading import Thread
from tkinter import filedialog, messagebox, ttk

import duckdb as dd
import matplotlib.pyplot as plt
import pandas as pd
from attrs import asdict
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from algorithm.search import genetic_algorithm
from domain.dtos.config import Config
from domain.dtos.gene import Gene
from domain.dtos.reports import Reports
from domain.enums.period import Period
from domain.utils.genetic import Population
from export.pdf import PDF


class ScheduleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de Horarios")
        self.geometry("600x350")
        self.setup_principal_window()

        self.pdf_exporter = PDF()
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

    def data_setter(self) -> None:
        courses = dd.sql("SELECT * FROM course").fetchall()
        classrooms = dd.sql("SELECT * FROM classroom").fetchall()
        teachers = dd.sql("SELECT * FROM teacher").fetchall()
        relations = dd.sql("SELECT * FROM teacher_course_available").fetchall()

        courses = list(map(lambda c: (c[0], c[1], c[2], c[3], c[4], "Opcional" if c[5]
                       else "Obligatorio", "Si" if c[6] else "Inactivo"), courses))
        classrooms = list(
            map(lambda c: (c[0], c[1], c[2] or "No definido"), classrooms))
        teachers = list(map(lambda t: (t[0], t[1], Period.to_time(
            t[2]), Period.to_time(t[3]), "Si" if t[4] else "Inactivo"), teachers))

        return courses, classrooms, teachers, relations

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

    def open_data_management(self):
        s = ttk.Style()
        s.configure('Treeview', rowheight=20)

        window = tk.Toplevel(self)
        window.title("Gestión de Datos")
        window.geometry("800x600")

        notebook = ttk.Notebook(window)

        courses, classrooms, teachers, relations = self.data_setter()

        course_frame = ttk.Frame(notebook)
        self.create_table_management(course_frame, "Cursos",
                                     ["Código", "Nombre", "Carrera", "Semestre", "Seccion", "Tipo", "Activo"], courses)

        classroom_frame = ttk.Frame(notebook)
        self.create_table_management(classroom_frame, "Salones",
                                     ["Identificador", "Nombre", "Capacidad"], classrooms, with_edit=False)

        teacher_frame = ttk.Frame(notebook)
        self.create_table_management(teacher_frame, "Docentes",
                                     ["Registro", "Nombre", "Hora Entrada", "Hora Salida", "Activo"], teachers)

        relation_frame = ttk.Frame(notebook)
        self.create_table_management(relation_frame, "Cursos que puede dar el docente",
                                     ["Docente", "Curso"], relations, with_edit=False)

        notebook.add(course_frame, text="Cursos")
        notebook.add(classroom_frame, text="Salones")
        notebook.add(teacher_frame, text="Docentes")
        notebook.add(relation_frame, text="Relaciones")
        notebook.pack(expand=True, fill='both')

        buttons_frame = ttk.Frame(window)
        ttk.Button(buttons_frame, text="Importar CSV",
                   command=self.import_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Exportar CSV",
                   command=partial(self.export_csv, title=notebook.tab(notebook.select(), "text"))).pack(side=tk.LEFT, padx=5)
        buttons_frame.pack(pady=10)

    def create_table_management(self, parent, title, columns, data, with_edit=True):
        frame = ttk.LabelFrame(parent, text=title)
        frame.pack(expand=True, fill='both', padx=10, pady=10)

        tree = ttk.Treeview(frame, columns=columns, show='headings')
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        for row in data:
            tree.insert("", 'end', values=row)

        buttons_frame = ttk.Frame(frame)
        ttk.Button(buttons_frame, text="Agregar",
                   command=lambda: self.show_form(title, tree)).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Eliminar",
                   command=lambda: self.delete_item(tree, title)).pack(side=tk.LEFT, padx=2)
        if with_edit:
            ttk.Button(buttons_frame, text="Activar/Desactivar",
                       command=lambda: self.edit_item(tree, title)).pack(side=tk.LEFT, padx=2)

        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        buttons_frame.grid(row=2, column=0, pady=5)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def open_algorithm_config(self):
        window = tk.Toplevel(self)
        window.title("Configuración del Algoritmo")

        parameters = [
            ("Tamaño de población:", "pop_size"),
            ("Máximo de generaciones:", "max_generations"),
            ("Valor de aptitud objetivo (%):", "fitness_objective"),
            ("Tasa de cruce (%):", "crossover_rate"),
            ("Tasa de mutación (%):", "mutation_rate"),
            ("Porcentaje élite (%):", "elite_percent")
        ]

        self.touch_config = {
            "pop_size": self.algorithm_config.pop_size,
            "max_generations": self.algorithm_config.max_generations,
            "fitness_objective": self.algorithm_config.fitness_objective,
            "crossover_rate": self.algorithm_config.crossover_rate,
            "mutation_rate": self.algorithm_config.mutation_rate,
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

    def show_form(self, type, tree, editar=False):
        window = tk.Toplevel(self)
        window.title(f"{"Agregar" if not editar else "Editar"} {type}")

        fields = {
            "Cursos": ["Código", "Nombre", "Carrera", "Semestre", "Seccion", "Tipo"],
            "Salones": ["ID", "Nombre"],
            "Docentes": ["Registro", "Nombre", "Hora Entrada", "Hora Salida"],
            "Cursos que puede dar el docente": ["Registro Docente", "Codigo Curso"]
        }[type]

        frame = ttk.Frame(window, padding=20)
        frame.pack()

        entries = []
        for i, field in enumerate(fields):
            ttk.Label(frame, text=field).grid(row=i, column=0, pady=5)
            entry = ttk.Entry(frame)
            entry.grid(row=i, column=1, pady=5)
            entries.append(entry)

        ttk.Button(frame, text="Guardar",
                   command=lambda: self.save_item(type, entries, window, tree)).grid(row=len(fields), columnspan=2)

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

    def import_csv(self):
        filepath = filedialog.askopenfilename(
            title="Importar archivo CSV", filetypes=[("CSV", "*.csv")])
        if not filepath:
            return

        df = dd.read_csv(filepath, null_padding=True).to_df()
        match len(df.columns):
            case 2:
                df = df.rename(
                    columns={df.columns[0]: "teacher", df.columns[1]: "course"})
                try:
                    dd.sql("SELECT * FROM df").insert_into("teacher_course_available")
                    messagebox.showinfo(
                        "Importar", "Relaciones importadas correctamente")
                except Exception as e:
                    messagebox.showinfo(
                        "Importar", "Error al importar archivo CSV, revise los datos")

            case 4:
                df = df.rename(columns={
                               df.columns[0]: "name", df.columns[1]: "personal_record", df.columns[2]: "check_in", df.columns[3]: "check_out"})
                df = df.reindex(
                    columns=["personal_record", "name", "check_in", "check_out"])

                df.insert(4, "active", True)
                if df.check_in.dtype != "int":
                    df.check_in = df.check_in.apply(Period.to_check_in)

                if df.check_out.dtype != "int":
                    df.check_out = df.check_out.apply(Period.to_check_out)

                try:
                    dd.sql("SELECT * FROM df").insert_into("teacher")
                    messagebox.showinfo(
                        "Importar", "Docentes importados correctamente")
                except Exception as e:
                    messagebox.showinfo(
                        "Importar", "Error al importar archivo CSV, revise los datos")

            case 6:
                df = df.rename(columns={df.columns[0]: "name", df.columns[1]: "code", df.columns[2]: "degree",
                               df.columns[3]: "semester", df.columns[4]: "section", df.columns[5]: "optional"})
                df = df.reindex(
                    columns=["code", "name", "degree", "semester", "section", "optional"])

                df.insert(6, "active", True)
                if df.optional.dtype != "bool":
                    df.loc[df.optional.eq("optativo"), "optional"] = True
                    df.loc[df.optional.eq("obligatorio"), "optional"] = False

                try:
                    dd.sql("SELECT * FROM df").insert_into("course")
                    messagebox.showinfo(
                        "Importar", "Cursos importados correctamente")
                except Exception as e:
                    messagebox.showinfo(
                        "Importar", "Error al importar archivo CSV, revise los datos")

            case _:
                messagebox.showinfo("Importar", "Archivo CSV inválido")

    def export_csv(self, title):
        table = {
            "Cursos": "course",
            "Salones": "classroom",
            "Docentes": "teacher",
            "Relaciones": "teacher_course_available"
        }[title]

        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[
                                                ("CSV", "*.csv")], initialfile=f"{table}.csv")
        if not filepath:
            return

        dd.sql(f"SELECT * FROM {table}").to_csv(filepath)

    def export_pdf(self):
        self.pdf_exporter.export_pdf(
            self.classrooms, self.periods, self.data, self.reports)

    def save_item(self, type, entries, window, tree):
        table = {
            "Cursos": "course",
            "Salones": "classroom",
            "Docentes": "teacher",
            "Cursos que puede dar el docente": "teacher_course_available"
        }[type]

        fields = {
            "Cursos": ["code", "name", "degree", "semester", "section", "optional"],
            "Salones": ["id", "name"],
            "Docentes": ["personal_record", "name", "check_in", "check_out"],
            "Cursos que puede dar el docente": ["teacher", "course"]
        }[type]

        data = list(map(lambda e: e.get(), entries))
        row = list(data)
        if type == "Docentes":
            row[2] = Period.to_check_in(
                datetime.strptime(data[2], "%H:%M").time())
            row[3] = Period.to_check_out(
                datetime.strptime(data[3], "%H:%M").time())

        if type == "Cursos":
            row[5] = True if data[5] == "Opcional" else False

        dd.execute(
            f"""
            INSERT INTO {table} ({', '.join(fields)})
            VALUES ({', '.join('?' * len(fields))})
            """,
            row
        )

        window.destroy()
        messagebox.showinfo("Guardar", f"{type} guardado correctamente")

        tree.insert("", 'end', values=data)

    def edit_item(self, tree, type):
        selection = tree.focus()
        if not selection:
            messagebox.showinfo(
                "Editar", "Seleccione un elemento para modificarlo")
            return

        data = tree.item(selection)['values']

        table = {
            "Cursos": "course",
            "Docentes": "teacher",
        }[type]

        field = {
            "Cursos": "code",
            "Docentes": "personal_record",
        }[type]

        if type == "Cursos":
            row = [data[0], True if data[6] == "Si" else False]

        else:
            row = [data[0], True if data[4] == "Si" else False]

        dd.execute(f"UPDATE {table} SET active = ? WHERE {field} = ?", (row))

        messagebox.showinfo("Editar", f"{type} editado correctamente")

        if type == "Cursos":
            data[6] = "Inactivo" if data[6] == "Si" else "Si"

        else:
            data[4] = "Inactivo" if data[4] == "Si" else "Si"

        tree.item(selection, values=data)

    def delete_item(self, tree, type):
        selection = tree.focus()
        if not selection:
            messagebox.showinfo(
                "Editar", "Seleccione un elemento para modificarlo")
            return

        data = tree.item(selection)['values']

        table = {
            "Cursos": "course",
            "Salones": "classroom",
            "Docentes": "teacher",
            "Cursos que puede dar el docente": "teacher_course_available"
        }[type]

        field = {
            "Cursos": "code",
            "Salones": "id",
            "Docentes": "personal_record",
            "Cursos que puede dar el docente": "teacher = ? AND course"
        }[type]

        row = [data[0]]
        if type == "Cursos que puede dar el docente":
            row.append(data[1])

        dd.execute(f"DELETE FROM {table} WHERE {field} = ?", row)

        messagebox.showinfo("Eliminar", f"{type} eliminado correctamente")

        tree.delete(selection)

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
                float(self.algorithm_config.mutation_rate) / 100,
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


if __name__ == "__main__":
    app = ScheduleGUI()
    app.mainloop()
