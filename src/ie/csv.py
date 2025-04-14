from tkinter import filedialog, messagebox
from typing import Callable

import duckdb as dd
import pandas as pd

from domain.enums import Period


def exporter(title: str):
    def exporter_decorator(func: Callable[[str], None]):
        def wrapper(*args, **kwargs):
            filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[
                                                    ("CSV", "*.csv")], initialfile=f"{title}.csv")

            if not filepath:
                return

            return func(filepath, *args, **kwargs)
        return wrapper
    return exporter_decorator


def importer(func: Callable[[str], None]):
    def wrapper(*args, **kwargs):
        filepath = filedialog.askopenfilename(
            title=f"Importar archivo CSV", filetypes=[("CSV", "*.csv")])

        if not filepath:
            return

        df = dd.read_csv(filepath, null_padding=True).to_df()
        return func(df, *args, **kwargs)
    return wrapper


@exporter("course")
def export_courses_csv(filepath: str) -> None:
    dd.sql(f"SELECT * FROM course").to_csv(filepath)


@exporter("classroom")
def export_classrooms_csv(filepath: str) -> None:
    dd.sql(f"SELECT * FROM classroom").to_csv(filepath)


@exporter("teacher")
def export_teachers_csv(filepath: str) -> None:
    dd.sql(f"SELECT * FROM teacher").to_csv(filepath)


@exporter("relation")
def export_relations_csv(filepath: str) -> None:
    dd.sql(f"SELECT * FROM teacher_course_available").to_csv(filepath)


def __fill_required_columns(df: pd.DataFrame, cols: dict, cols_rename: list[str], inserts: tuple[tuple]) -> pd.DataFrame:
    df = df.rename(columns=cols)
    df = df.reindex(columns=cols_rename)

    actual_cols = len(cols)
    for i, (col, value) in enumerate(inserts):
        df.insert(i + actual_cols, col, value)


@importer
def import_courses_csv(df: pd.DataFrame) -> None:
    def fill_required_columns(df: pd.DataFrame, rename_dict: dict, inserts: tuple[tuple]) -> pd.DataFrame:
        cols = {
            df.columns[0]: "name",
            df.columns[1]: "code",
        }
        rename_dict = {
            df.columns[2]: "degree",
            df.columns[3]: "semester",
            df.columns[4]: "section",
            df.columns[5]: "optional"
        } + rename_dict
        __fill_required_columns(
            df, cols + rename_dict, ["code", "name"] + rename_dict.values(), inserts)

        if df.optional.dtype != "bool":
            df.loc[df.optional.eq("optativo"), "optional"] = True
            df.loc[df.optional.eq("obligatorio"), "optional"] = False

        try:
            dd.sql("SELECT * FROM df").insert_into("course")
            messagebox.showinfo(
                "Importar", "Cursos importados correctamente")
        except Exception as e:
            messagebox.showinfo(
                "Importar", "Se esperaba 6, 7 u 8 columnas\nCon el orden: name, code, degree, semester, section, optional[, classroom[, active]]")

    match len(df.columns):
        case 6:
            fill_required_columns(
                df, dict(), (('classroom', None), ('active', True)))

        case 7:
            fill_required_columns(
                df, dict(classroom="classroom"), (('active', True),))

        case 8:
            fill_required_columns(
                df, dict(classroom="classroom", active="active"), tuple())

        case _:
            messagebox.showinfo(
                "Importar", "Se esperaba 6, 7 u 8 columnas\nCon el orden: name, code, degree, semester, section, optional[, classroom[, active]]")


@importer
def import_classrooms_csv(df: pd.DataFrame) -> None:
    def fill_required_columns(df: pd.DataFrame, rename_dict: dict, inserts: tuple[tuple]) -> pd.DataFrame:
        cols = {
            df.columns[0]: "name",
            df.columns[1]: "id",
        }
        __fill_required_columns(df, cols + rename_dict,
                                ["id", "name"] + rename_dict.values(), inserts)

        try:
            dd.sql("SELECT * FROM df").insert_into("classroom")
            messagebox.showinfo(
                "Importar", "Salones importados correctamente")
        except Exception as e:
            messagebox.showinfo(
                "Importar", "Se esperaba 2 o 3 columnas\nCon el orden: name, id[, capacity]")

    match len(df.columns):
        case 2:
            fill_required_columns(df, dict(), (('capacity', None),))

        case 3:
            fill_required_columns(df, dict(capacity="capacity"), tuple())

        case _:
            messagebox.showinfo(
                "Importar", "Se esperaba 2 o 3 columnas\nCon el orden: name, id[, capacity]")


@importer
def import_teachers_csv(df: pd.DataFrame) -> None:
    def fill_required_columns(df: pd.DataFrame, rename_dict: dict, inserts: tuple[tuple]) -> pd.DataFrame:
        cols = {
            df.columns[0]: "name",
            df.columns[1]: "personal_record",
        }
        rename_dict = {
            df.columns[2]: "check_in",
            df.columns[3]: "check_out"
        } + rename_dict
        __fill_required_columns(
            df, cols + rename_dict, ["personal_record", "name"] + rename_dict.values(), inserts)

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
                "Importar", "Se esperaba 4 o 5 columnas\nCon el orden: name, personal_record, check_in, check_out[, active]")

    match len(df.columns):
        case 4:
            fill_required_columns(df, dict(), (('active', True),))

        case 5:
            fill_required_columns(df, dict(active="active"), tuple())

        case _:
            messagebox.showinfo(
                "Importar", "Se esperaba 4 o 5 columnas\nCon el orden: name, personal_record, check_in, check_out[, active]")


@importer
def import_relations_csv(df: pd.DataFrame) -> None:
    def fill_required_columns(df: pd.DataFrame, rename_dict: dict, inserts: tuple[tuple]) -> pd.DataFrame:
        cols = {
            df.columns[0]: "teacher",
            df.columns[1]: "course",
        }
        __fill_required_columns(
            df, cols, ["teacher", "course"] + rename_dict.values(), inserts)

        try:
            dd.sql("SELECT * FROM df").insert_into("teacher_course_available")
            messagebox.showinfo(
                "Importar", "Relaciones importadas correctamente")
        except Exception as e:
            messagebox.showinfo(
                "Importar", "Se esperaba 2 columnas\nCon el orden: teacher, course")

    match len(df.columns):
        case 2:
            fill_required_columns(df, dict(), tuple())

        case _:
            messagebox.showinfo(
                "Importar", "Se esperaba 2 columnas\nCon el orden: teacher, course")
