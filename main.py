from utils import *
from evolve import *
from export import *

SIZE = 64                   # Population size
LIMIT = 50                  # Stagnation limit


population = generatePopulation(SIZE)
best = evolution(SIZE, LIMIT, population)
saveToExcel(best, openFile=True)
# imported = importSchedule(name='Problem2', info=True)
