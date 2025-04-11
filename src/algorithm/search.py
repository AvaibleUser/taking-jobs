import time
import tracemalloc
from typing import Callable, List, Tuple

from algorithm.assesment import check_termination_criteria, fitness
from algorithm.crossover import crossover
from algorithm.initialize import generate_initial_population
from algorithm.mutation import mutate
from algorithm.selection import (select_elites_deterministic,
                                 select_elites_ranked, select_parents)
from domain.dtos.reports import Reports
from domain.models.priorities.continuous_semester_courses import \
    ContinuousSemesterCourses
from domain.utils.genetic import Population

Setter = Callable[[float], None]


def __genetic_algorithm_step(
        population: Population,
        population_size: int,
        crossover_rate: float,
        mutation_rate: float,
        generation: int,
        elite_percent: float
) -> Tuple[Population, float]:
    avg_score = fitness(population)

    # elites = select_elites_deterministic(population, avg_score)
    # if not (population_size * 0.2 > len(elites) > population_size * 0.1):
    elites = select_elites_ranked(population, elite_percent)

    mating_pool = select_parents(population, population_size, avg_score)

    children, rest = crossover(mating_pool, crossover_rate, generation)
    new_population = children + rest

    mutate(new_population, mutation_rate)

    new_population = elites + new_population

    if generation % 5 == 0:
        print(f"gen {generation}: avg {avg_score}, best {elites[0].score}")

    return new_population[:population_size], avg_score


def genetic_algorithm(
        population_size: int,
        crossover_rate: float,
        mutation_rate: float,
        generation_threshold: int,
        elite_percent: float,
        fitness_objective: float,
        progress: Setter,

) -> Tuple[Population, Reports]:
    tracemalloc.start()
    start = time.time()
    generation = 0
    duration = 0
    conflicts = []
    evolution = []
    population = generate_initial_population(
        population_size=population_size, generation_threshold=generation_threshold)

    start = time.time()
    while not check_termination_criteria(population, generation, generation_threshold, fitness_objective):
        population, avg_score = __genetic_algorithm_step(
            population,
            population_size,
            crossover_rate,
            mutation_rate,
            generation,
            elite_percent
        )
        generation += 1
        duration += duration
        evolution.append(avg_score)
        conflicts.append(
            sum(map(lambda c: sum(map(lambda g: len(g.failed_in), c.genes)), population)))

        progress(sum(population[-1].score,
                 generation / generation_threshold) / 2)
        duration += - start + (start := time.time())

    final_population = sorted(population, key=lambda c: c.score, reverse=True)
    consecutive = sum(map(lambda g: int(
        ContinuousSemesterCourses.__name__ in g.failed_in), final_population[0].genes))

    _, peak_memory = tracemalloc.get_traced_memory()
    total_duration = time.time() - start

    reports = Reports(
        conflicts_per_generation=conflicts,
        avg_fitnesses=evolution,
        avg_durations=duration / generation,
        total_generations=generation,
        total_duration=total_duration,
        consecutive_courses_percent=consecutive /
        len(final_population[0].genes),
        memory_consumption=peak_memory,
    )
    return final_population, reports
