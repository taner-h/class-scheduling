from utils import *
from evolve import *
from export import *
import cProfile


def main():

    best = evolution()
    saveToExcel(best, openFile=True)
    # imported = importSchedule(name='Problem2', info=True)


if __name__ == '__main__':
    # cProfile.run('main()')
    main()
