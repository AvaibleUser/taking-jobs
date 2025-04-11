from attrs import define, field


@define
class Config:
    pop_size: int = field(default=150)
    max_generations: int = field(default=75)
    fitness_objective: float = field(default=99)
    crossover_rate: float = field(default=80)
    mutation_rate: float = field(default=25)
    elite_percent: float = field(default=5)
