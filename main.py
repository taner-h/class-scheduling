from utils import *
from evolve import *
from export import *
import cProfile


def main():
    SIZE = 100                  # Population size
    LIMIT = 50                  # Stagnation limit

    population = generatePopulation(SIZE)
    best = evolution(SIZE, LIMIT, population)
    saveToExcel(best, openFile=True)
    # imported = importSchedule(name='Problem2', info=True)


if __name__ == '__main__':
    # cProfile.run('main()')
    main()
