from algorithm.search import genetic_algorithm
from config import config

if __name__ == '__main__':
    with config():
        genetic_algorithm(300, 0.8, 0.2, 100)
