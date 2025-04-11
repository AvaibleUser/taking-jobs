from random import choice

import duckdb as dd

from domain.dtos import Chromosome, Classroom, Course, Gene, Teacher
from domain.enums import Period
from domain.utils.genetic import Population

__population_size = 100
__chromosome_len = 0
__crossover_rate = 0.7
__mutation_rate = 0.1
__generation_threshold = 100


def chromosome_len() -> int:
    return __chromosome_len


def population_size() -> int:
    return __population_size


def crossover_rate() -> float:
    return __crossover_rate


def mutation_rate() -> float:
    return __mutation_rate


def generation_threshold() -> int:
    return __generation_threshold


def __generate_chromosome() -> Chromosome:
    classrooms_df = dd.sql("SELECT * FROM classroom").to_df()
    classrooms = tuple(Classroom(**row)
                       for row in classrooms_df.to_dict("records"))

    courses_df = dd.sql("SELECT * FROM course WHERE active=TRUE ORDER BY code").to_df()
    courses = tuple(Course(**row) for row in courses_df.to_dict("records"))

    teachers_df = dd.sql(
        """
        SELECT t.*, tca.course AS available_courses
        FROM teacher t
            JOIN teacher_course_available tca
                ON t.personal_record = tca.teacher
        WHERE active = TRUE
        """).to_df()
    teachers_df = teachers_df.groupby("personal_record", as_index=False).agg(
        {"name": "first", "check_in": "min", "check_out": "max", "available_courses": list}).reset_index(drop=True)
    teachers = tuple(Teacher(**row) for row in teachers_df.to_dict("records"))

    periods = tuple(Period)

    dd.execute("INSERT INTO chromosome (generation) VALUES (0)")
    chromosome_id = dd.sql("SELECT MAX(id) FROM chromosome").fetchall()[0][0]

    dd.executemany(
        "INSERT INTO gene (classroom, course, teacher, period) VALUES (?, ?, ?, ?)",
        ((choice(classrooms).id, c.code, choice(teachers).personal_record, choice(periods)) for c in courses))

    dd.execute(
        "INSERT INTO chromosome_gene SELECT ? AS chromosome, id AS gene FROM gene g ORDER BY id DESC LIMIT ?",
        (chromosome_id, len(courses)))

    genes_df = dd.sql(
        "SELECT g.* FROM gene g JOIN chromosome_gene cg ON g.id = cg.gene WHERE cg.chromosome = ?",
        params=[chromosome_id]).to_df()
    genes = list(Gene(
        id=row["id"],
        classroom=next(filter(lambda c: c.id == row["classroom"], classrooms)),
        course=next(filter(lambda c: c.code == row["course"], courses)),
        teacher=next(filter(lambda t: t.personal_record ==
                     row["teacher"], teachers)),
        period=next(filter(lambda p: p == row["period"], periods))
    ) for row in genes_df.to_dict("records"))

    return Chromosome(id=chromosome_id, generation=0, genes=genes)


def generate_initial_population(
        population_size: int = population_size(),
        crossover_rate: float = crossover_rate(),
        mutation_rate: float = mutation_rate(),
        generation_threshold: int = generation_threshold()) -> Population:
    dd.begin()

    global __population_size
    __population_size = population_size

    global __crossover_rate
    __crossover_rate = crossover_rate

    global __mutation_rate
    __mutation_rate = mutation_rate

    global __generation_threshold
    __generation_threshold = generation_threshold

    global __chromosome_len
    __chromosome_len = dd.sql(
        "SELECT COUNT(*) FROM course WHERE active=TRUE").fetchall()[0][0]

    dd.execute("DELETE FROM chromosome WHERE 1=1")
    dd.execute("DELETE FROM gene WHERE 1=1")

    population = list(__generate_chromosome() for _ in range(population_size))

    dd.commit()

    return population
