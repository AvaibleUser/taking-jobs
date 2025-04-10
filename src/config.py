import duckdb as dd


def config() -> dd.DuckDBPyConnection:
    con = dd.connect(':memory:')
    dd.set_default_connection(con)

    __config_duckdb()
    __config_classrooms()

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
            active BOOLEAN DEFAULT TRUE
        )
        """)

    dd.execute("""
        CREATE TABLE teacher (
            personal_record INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            check_in INTEGER NOT NULL,
            check_out INTEGER NOT NULL,
            active BOOLEAN DEFAULT TRUE
        )
        """)

    dd.execute("""
        CREATE TABLE teacher_course_available (
            teacher INTEGER REFERENCES teacher (personal_record),
            course INTEGER REFERENCES course (code),
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
            parent1 INTEGER REFERENCES chromosome (id) NULL,
            parent2 INTEGER REFERENCES chromosome (id) NULL,
            PRIMARY KEY (id)
        )
        """)

    dd.execute("""
        CREATE SEQUENCE ge_id START 1;
        CREATE TABLE gene (
            id INTEGER DEFAULT NEXTVAL('ge_id'),
            classroom INTEGER REFERENCES classroom (id),
            course INTEGER REFERENCES course (code),
            teacher INTEGER REFERENCES teacher (personal_record),
            period INTEGER NOT NULL CHECK (period BETWEEN 1 AND 10),
            PRIMARY KEY (id)
        )
        """)

    dd.execute("""
        CREATE TABLE chromosome_gene (
            chromosome INTEGER REFERENCES chromosome (id),
            gene INTEGER REFERENCES gene (id),
            PRIMARY KEY (chromosome, gene)
        )
        """)


def __config_classrooms() -> None:
    df = dd.read_csv("data/salones.csv", header=True,
                     null_padding=True, names=["name", "id"]).to_df()

    df = df.reindex(columns=["id", "name"])
    df.insert(2, "capacity", None)

    dd.sql("SELECT * FROM df").insert_into("classroom")
