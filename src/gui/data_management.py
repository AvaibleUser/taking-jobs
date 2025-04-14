import tkinter as tk
from datetime import datetime
from functools import partial
from tkinter import messagebox, ttk

import duckdb as dd

from domain.enums import Period
from ie.csv import (export_classrooms_csv, export_courses_csv,
                    export_relations_csv, export_teachers_csv,
                    import_classrooms_csv, import_courses_csv,
                    import_relations_csv, import_teachers_csv)


class DataManagementGUI:
    def data_setter(self) -> None:
        courses = dd.sql("SELECT * FROM course").fetchall()
        classrooms = dd.sql("SELECT * FROM classroom").fetchall()
        teachers = dd.sql("SELECT * FROM teacher").fetchall()
        relations = dd.sql("SELECT * FROM teacher_course_available").fetchall()

        courses = list(map(lambda c: (c[0], c[1], c[2], c[3], c[4], "Opcional" if c[5]
                       else "Obligatorio", "" if c[6] is None else c[6], "Si" if c[7] else "Inactivo"), courses))
        classrooms = list(
            map(lambda c: (c[0], c[1], c[2] or "No definido"), classrooms))
        teachers = list(map(lambda t: (t[0], t[1], Period.to_time(
            t[2]), Period.to_time(t[3]), "Si" if t[4] else "Inactivo"), teachers))

        return courses, classrooms, teachers, relations

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
                                     ["Código", "Nombre", "Carrera", "Semestre", "Seccion", "Tipo", "Clase especifica", "Activo"], courses)

        classroom_frame = ttk.Frame(notebook)
        self.create_table_management(classroom_frame, "Salones",
                                     ["Identificador", "Nombre", "Capacidad"], classrooms, with_toggle=False)

        teacher_frame = ttk.Frame(notebook)
        self.create_table_management(teacher_frame, "Docentes",
                                     ["Registro", "Nombre", "Hora Entrada", "Hora Salida", "Activo"], teachers)

        relation_frame = ttk.Frame(notebook)
        self.create_table_management(relation_frame, "Cursos que puede dar el docente",
                                     ["Docente", "Curso"], relations, with_toggle=False, with_edit=False)

        notebook.add(course_frame, text="Cursos")
        notebook.add(classroom_frame, text="Salones")
        notebook.add(teacher_frame, text="Docentes")
        notebook.add(relation_frame, text="Relaciones")
        notebook.pack(expand=True, fill='both')

        buttons_frame = ttk.Frame(window)
        ttk.Button(buttons_frame, text="Importar CSV",
                   command=partial(self.import_csv, title=notebook.tab(notebook.select(), "text"))).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Exportar CSV",
                   command=partial(self.export_csv, title=notebook.tab(notebook.select(), "text"))).pack(side=tk.LEFT, padx=5)
        buttons_frame.pack(pady=10)

    def create_table_management(self, parent, title, columns, data, with_toggle=True, with_edit=True):
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
        if with_toggle:
            ttk.Button(buttons_frame, text="Activar/Desactivar",
                       command=lambda: self.toggle_active_item(tree, title)).pack(side=tk.LEFT, padx=2)
        if with_edit:
            ttk.Button(buttons_frame, text="Editar",
                       command=lambda: self.show_form(title, tree, editar=True)).pack(side=tk.LEFT, padx=2)

        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        buttons_frame.grid(row=2, column=0, pady=5)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def show_form(self, type, tree, editar=False):
        window = tk.Toplevel(self)
        window.title(f"{"Agregar" if not editar else "Editar"} {type}")

        fields = {
            "Cursos": ["Código", "Nombre", "Carrera", "Semestre", "Seccion", "Tipo", "Salon especifico"],
            "Salones": ["ID", "Nombre"],
            "Docentes": ["Registro", "Nombre", "Hora Entrada", "Hora Salida"],
            "Cursos que puede dar el docente": ["Registro Docente", "Codigo Curso"]
        }[type]

        frame = ttk.Frame(window, padding=20)
        frame.pack()

        entries = []
        selection = tree.focus()
        data = tree.item(selection)['values']
        for i, field in enumerate(fields):
            ttk.Label(frame, text=field).grid(row=i, column=0, pady=5)
            entry = ttk.Entry(frame)
            entry.grid(row=i, column=1, pady=5)
            entries.append(entry)
            if editar:
                entry.insert(0, data[i])

        ttk.Button(frame, text="Guardar",
                   command=lambda: self.save_item(type, entries, window, tree, editar)).grid(row=len(fields), columnspan=2)

    def import_csv(self, title: str):
        {
            "Cursos": import_courses_csv,
            "Salones": import_classrooms_csv,
            "Docentes": import_teachers_csv,
            "Relaciones": import_relations_csv
        }[title]()

    def export_csv(self, title: str):
        {
            "Cursos": export_courses_csv,
            "Salones": export_classrooms_csv,
            "Docentes": export_teachers_csv,
            "Relaciones": export_relations_csv
        }[title]()

    def export_pdf(self):
        self.pdf_exporter.export_pdf(
            self.classrooms, self.periods, self.data, self.reports)

    def save_item(self, type, entries, window, tree, edit=False):
        table = {
            "Cursos": "course",
            "Salones": "classroom",
            "Docentes": "teacher",
            "Cursos que puede dar el docente": "teacher_course_available"
        }[type]

        fields = {
            "Cursos": ["code", "name", "degree", "semester", "section", "optional", "classroom"],
            "Salones": ["id", "name"],
            "Docentes": ["personal_record", "name", "check_in", "check_out"],
            "Cursos que puede dar el docente": ["teacher", "course"]
        }[type]

        field = {
            "Cursos": "code",
            "Salones": "id",
            "Docentes": "personal_record",
            "Cursos que puede dar el docente": "teacher = ? AND course"
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
            row[6] = None if not data[6].isnumeric() else int(data[6])

        try:
            if not edit:
                dd.execute(
                    f"""
                        INSERT INTO {table} ({', '.join(fields)})
                        VALUES ({', '.join('?' * len(fields))})
                        """,
                    row
                )
                tree.insert("", 'end', values=data)

            else:
                selection = tree.focus()
                values = tree.item(selection)['values']
                dd.execute(
                    f"""
                    UPDATE {table} SET {', '.join(f"{field} = ?" for field in fields)}
                    WHERE {field} = ?
                    """,
                    row + values[:1]
                )
                tree.item(selection, values=data)

        except Exception:
            messagebox.showinfo(
                "Importar", "No se pudo importar el archivo CSV, revise los datos")
            window.destroy()
            return

        window.destroy()
        messagebox.showinfo("Guardar", f"{type} guardado correctamente")

        self.data_setter()

    def toggle_active_item(self, tree, type):
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
            row = [data[0], True if len(
                data) < 8 or data[7] == "Si" else False]

        else:
            row = [data[0], True if len(
                data) < 5 or data[4] == "Si" else False]

        dd.execute(f"UPDATE {table} SET active = ? WHERE {field} = ?", (row))

        messagebox.showinfo("Editar", f"{type} editado correctamente")

        if type == "Cursos":
            if len(data) < 8:
                data.append("Inactivo")
            else:
                data[7] = "Inactivo" if data[7] == "Si" else "Si"

        else:
            if len(data) < 5:
                data.append("Inactivo")
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
