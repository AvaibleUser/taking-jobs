from utils.memory import CON


def config():
    CON.execute("""
        CREATE TABLE classroom (
            id INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            capacity INTEGER,
            PRIMARY KEY (id)
        );
        """)

    CON.execute("""
        CREATE TABLE course (
            code INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            degree VARCHAR NOT NULL,
            semester INTEGER NOT NULL CHECK (semester IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)),
            section VARCHAR NOT NULL,
            optional BOOLEAN NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            PRIMARY KEY (code)
        );
        """)

    CON.execute("""
        CREATE TABLE teacher (
            personal_record INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            check_in INTEGER NOT NULL,
            check_out INTEGER NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            PRIMARY KEY (personal_record)
        );
        """)

    CON.execute("""
        CREATE TABLE teacher_course_available (
            teacher INTEGER NOT NULL,
            course INTEGER NOT NULL,
            PRIMARY KEY (teacher, course)
        );
        """)

    CON.execute("""
        CREATE TABLE chromosome (
            classroom INTEGER NOT NULL,
            course INTEGER NOT NULL,
            teacher INTEGER NOT NULL,
            period INTEGER NOT NULL CHECK (period IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)),
            score REAL,
            active BOOLEAN DEFAULT TRUE,
            PRIMARY KEY (classroom, course, teacher, period)
        );
        """)
