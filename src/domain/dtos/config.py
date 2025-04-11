from attrs import define, field


@define
class Config:
    pop_size: int = field(default=300)
    max_generations: int = field(default=150)
    fitness_objective: float = field(default=99.75)
    crossover_rate: float = field(default=80)
    mutation_rate: float = field(default=40)
    elite_percent: float = field(default=5)
