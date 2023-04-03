from utils import *
from evolve import *
from export import *

SIZE = 64                   # Population size
LIMIT = 25                  # Stagnation limit


population = generatePopulation(SIZE)
best = evolution(SIZE, LIMIT, population)
saveToExcel(best)
# imported = importSchedule(name='Problem2', info=True)
