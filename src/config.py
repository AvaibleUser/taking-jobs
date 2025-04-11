import duckdb as dd

from domain.enums import Period


def config() -> dd.DuckDBPyConnection:
    con = dd.connect(':memory:')
    dd.set_default_connection(con)

    __config_duckdb()
    __config_classrooms()
    __config_courses()
    __config_teachers()
    __config_teacher_courses()

    return con


def __config_duckdb() -> None:
    dd.execute("""
        CREATE TABLE classroom (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            capacity INTEGER
        )
        """)

    dd.execute("""
        CREATE TABLE course (
            code INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            degree VARCHAR NOT NULL,
            semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 10),
            section VARCHAR NOT NULL,
            optional BOOLEAN NOT NULL,
            classroom INTEGER,
            active BOOLEAN DEFAULT TRUE
        )
        """)

    dd.execute("""
        CREATE TABLE teacher (
            personal_record INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            check_in INTEGER NOT NULL CHECK (check_in BETWEEN 1 AND 10),
            check_out INTEGER NOT NULL CHECK (check_out BETWEEN 1 AND 10),
            active BOOLEAN DEFAULT TRUE
        )
        """)

    dd.execute("""
        CREATE TABLE teacher_course_available (
            teacher INTEGER,
            course INTEGER,
            PRIMARY KEY (teacher, course)
        )
        """)

    dd.execute("""
        CREATE SEQUENCE ch_id START 1;
        CREATE TABLE chromosome (
            id INTEGER DEFAULT NEXTVAL('ch_id'),
            generation INTEGER NOT NULL,
            score REAL,
            active BOOLEAN DEFAULT TRUE,
            parent1 INTEGER NULL,
            parent2 INTEGER NULL,
            PRIMARY KEY (id)
        )
        """)

    dd.execute("""
        CREATE SEQUENCE ge_id START 1;
        CREATE TABLE gene (
            id INTEGER DEFAULT NEXTVAL('ge_id'),
            classroom INTEGER,
            course INTEGER,
            teacher INTEGER,
            period INTEGER NOT NULL CHECK (period BETWEEN 1 AND 10),
            PRIMARY KEY (id)
        )
        """)

    dd.execute("""
        CREATE TABLE chromosome_gene (
            chromosome INTEGER,
            gene INTEGER,
            PRIMARY KEY (chromosome, gene)
        )
        """)


def __config_classrooms() -> None:
    df = dd.read_csv("data/salones.csv", header=True,
                     null_padding=True, names=["name", "id"]).to_df()

    df = df.reindex(columns=["id", "name"])
    df.insert(2, "capacity", None)

    dd.sql("SELECT * FROM df").insert_into("classroom")


def __config_courses() -> None:
    df = dd.read_csv("data/cursos.csv", header=True,
                     null_padding=True, names=["name", "code", "degree", "semester", "section", "optional"]).to_df()

    df = df.reindex(columns=["code", "name", "degree",
                    "semester", "section", "optional"])

    df.insert(6, "classroom", None)
    df.insert(7, "active", True)
    if df.optional.dtype != "bool":
        df.loc[df.optional.eq("optativo"), "optional"] = True
        df.loc[df.optional.eq("obligatorio"), "optional"] = False

    dd.sql("SELECT * FROM df").insert_into("course")


def __config_teachers() -> None:
    df = dd.read_csv("data/docentes.csv", header=True,
                     null_padding=True, names=["name", "personal_record", "check_in", "check_out"]).to_df()

    df = df.reindex(columns=["personal_record",
                    "name", "check_in", "check_out"])

    df.insert(4, "active", True)
    if df.check_in.dtype != "int":
        df.check_in = df.check_in.apply(Period.to_check_in)

    if df.check_out.dtype != "int":
        df.check_out = df.check_out.apply(Period.to_check_out)

    dd.sql("SELECT * FROM df").insert_into("teacher")


def __config_teacher_courses() -> None:
    dd.read_csv("data/relacion.csv", header=True, null_padding=True,
                names=["teacher", "course"]).insert_into("teacher_course_available")
