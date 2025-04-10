from random import shuffle

from algorithm.assesment import check_termination_criteria, fitness
from algorithm.crossover import crossover
from algorithm.initialize import generate_initial_population
from algorithm.mutation import mutate
from algorithm.selection import (select_elites_deterministic,
                                 select_elites_ranked, select_parents)
from domain.utils.genetic import Population


def __genetic_algorithm_step(population: Population, population_size: int, crossover_rate: float, mutation_rate: float, generation: int) -> Population:
    avg_score = fitness(population)

    # elites = select_elites_deterministic(population, avg_score)
    # if not (population_size * 0.2 > len(elites) > population_size * 0.1):
    elites = select_elites_ranked(population, 0.05)

    mating_pool = select_parents(population, population_size, avg_score)

    children, rest = crossover(mating_pool, crossover_rate, generation)
    new_population = children + rest

    mutate(new_population, mutation_rate)

    new_population = elites + new_population

    if generation % 5 == 0:
        print(f"gen {generation}: avg {avg_score}, best {elites[0].score}")

    return new_population[:population_size]


def genetic_algorithm(population_size: int, crossover_rate: float, mutation_rate: float, generation_threshold: int) -> Population:
    generation = 0
    population = generate_initial_population(
        population_size=population_size, generation_threshold=generation_threshold)

    while not check_termination_criteria(population, generation, generation_threshold):
        population = __genetic_algorithm_step(
            population, population_size, crossover_rate, mutation_rate, generation)
        generation += 1
    return sorted(population, key=lambda c: c.score, reverse=True)
