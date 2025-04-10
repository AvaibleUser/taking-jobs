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
    classrooms = (Classroom(**row) for row in classrooms_df.to_dict("records"))

    courses_df = dd.sql("SELECT * FROM course WHERE active=TRUE").to_df()
    courses_df = courses_df.sample(frac=1).reset_index(drop=True)
    courses = (Course(**row) for row in courses_df.to_dict("records"))

    teachers_df = dd.sql("SELECT * FROM teacher WHERE active=TRUE").to_df()
    teachers = (Teacher(**row) for row in teachers_df.to_dict("records"))

    periods = list(Period)

    dd.execute("INSERT INTO chromosome (generation) VALUES (0)")
    chromosome_id = dd.sql("SELECT MAX(id) FROM chromosome").first()[0]

    dd.executemany(
        """
        INSERT INTO gene (classroom, course, teacher, period) VALUES (?, ?, ?, ?);
        INSERT INTO chromosome_gene (chromosome, gene) SELECT ?, MAX(id) FROM gene;
        """,
        [(choice(classrooms).id, c.code, choice(
            teachers).personal_record, choice(periods), chromosome_id)
         for c in courses])

    genes_df = dd.sql(
        "SELECT * FROM gene WHERE chromosome = ?", chromosome_id).to_df()
    genes = (Gene(**row) for row in genes_df.to_dict("records"))

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
        "SELECT COUNT(*) FROM course WHERE active=TRUE").first()[0]

    dd.execute("DELETE FROM chromosome WHERE 1=1")
    dd.execute("DELETE FROM gene WHERE 1=1")

    population = (__generate_chromosome() for _ in range(population_size))

    dd.commit()

    return population
