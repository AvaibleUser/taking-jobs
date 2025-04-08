from utils.memory import execute


def config() -> None:
    __config_duckdb()


def __config_duckdb() -> None:
    execute("""
        CREATE TABLE classroom (
            id INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            capacity INTEGER,
            PRIMARY KEY (id)
        );
        """)

    execute("""
        CREATE TABLE course (
            code INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            degree VARCHAR NOT NULL,
            semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 10),
            section VARCHAR NOT NULL,
            optional BOOLEAN NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            PRIMARY KEY (code)
        );
        """)

    execute("""
        CREATE TABLE teacher (
            personal_record INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            check_in INTEGER NOT NULL,
            check_out INTEGER NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            PRIMARY KEY (personal_record)
        );
        """)

    execute("""
        CREATE TABLE teacher_course_available (
            teacher INTEGER REFERENCES teacher (personal_record),
            course INTEGER REFERENCES course (code),
            PRIMARY KEY (teacher, course)
        );
        """)

    execute("""
        CREATE TABLE chromosome (
            id INTEGER INCREMENT,
            generation INTEGER NOT NULL,
            score REAL,
            active BOOLEAN DEFAULT TRUE,
            PRIMARY KEY (id)
        );
        """)

    execute("""
        CREATE TABLE gene (
            id INTEGER INCREMENT,
            classroom INTEGER REFERENCES classroom (id),
            course INTEGER REFERENCES course (code),
            teacher INTEGER REFERENCES teacher (personal_record),
            period INTEGER NOT NULL CHECK (period BETWEEN 1 AND 10),
            chromosome INTEGER REFERENCES chromosome (id),
            PRIMARY KEY (id)
        );
        """)
