from attrs import define, field


@define
class Config:
    pop_size: int = field(default=300)
    max_generations: int = field(default=200)
    fitness_objective: float = field(default=99)
    crossover_rate: float = field(default=80)
    swap_prob: float = field(default=50)
    mutation_rate: float = field(default=40)
    inversion_rate: float = field(default=10)
    elite_percent: float = field(default=5)
