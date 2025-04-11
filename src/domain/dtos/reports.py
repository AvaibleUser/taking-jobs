from attrs import define, field


@define
class Reports:
    conflicts_per_generation: list[int] = field(factory=list)
    avg_fitnesses: list[float] = field(factory=list)
    avg_durations: float = field(default=0)
    total_generations: int = field(default=0)
    total_duration: float = field(default=0)
    consecutive_courses_percent: float = field(default=0)
    memory_consumption: float = field(default=0)
