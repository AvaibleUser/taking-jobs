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
from domain.models.priorities import ContinuousSemesterCourses
from domain.utils.genetic import Population

Setter = Callable[[float], None]


def __genetic_algorithm_step(
        population: Population,
        population_size: int,
        crossover_rate: float,
        swap_prob: float,
        mutation_rate: float,
        inversion_rate: float,
        generation: int,
        elite_percent: float
) -> Population:
    # elites = select_elites_deterministic(population, avg_score)
    # if not (population_size * 0.2 > len(elites) > population_size * 0.1):
    elites = select_elites_ranked(population, elite_percent)

    mating_pool = select_parents(population, int(
        population_size * (1 - elite_percent)) + 1)

    children, rest = crossover(
        mating_pool, crossover_rate, swap_prob, generation)
    new_population = children + rest

    mutated = mutate(new_population, mutation_rate, inversion_rate, generation)

    new_population = elites + mutated + new_population

    return new_population[:population_size]


def genetic_algorithm(
        population_size: int,
        crossover_rate: float,
        swap_prob: float,
        mutation_rate: float,
        inversion_rate: float,
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

    start_method = time.time()
    while True:
        stop, avg_score = check_termination_criteria(
            population, generation, generation_threshold, fitness_objective)
        if stop:
            break

        generation += 1
        population = __genetic_algorithm_step(
            population,
            population_size,
            crossover_rate,
            swap_prob,
            mutation_rate,
            inversion_rate,
            generation,
            elite_percent
        )
        evolution.append(avg_score)
        conflicts.append(
            sum(map(lambda c: sum(map(lambda g: len(g.failed_in), c.genes)), population)))

        progress((population[0].score + generation /
                 generation_threshold) / 2)
        duration += - start_method + (start_method := time.time())

        if generation % 5 == 0:
            print(
                f"gen {generation}: avg {avg_score}, best {population[0].score}, time {duration}")

    final_population = sorted(population, key=lambda c: c.score, reverse=True)
    non_consecutive = sum(map(lambda g: int(
        ContinuousSemesterCourses.__name__ in g.failed_in), final_population[0].genes))

    _, peak_memory = tracemalloc.get_traced_memory()
    total_duration = time.time() - start
    print(f"non consecutive: {non_consecutive}")

    reports = Reports(
        conflicts_per_generation=conflicts,
        avg_fitnesses=evolution,
        avg_durations=duration / generation,
        total_generations=generation,
        total_duration=total_duration,
        consecutive_courses_percent=1 -
        (non_consecutive / len(final_population[0].genes)),
        memory_consumption=peak_memory,
    )
    return final_population, reports
