from classes import Teacher, Session, Course, Schedule, teachers, courses, sessions
from utils import *
from export import *
import copy
import random
import time


PRINT_GENERATION = False


def generateInitialSemesterSchedule(semester):
    semester = copy.deepcopy(semester)
    available = copy.deepcopy(initialAvailableSlots)

    fixedSessions = [session for session in semester if session.isFixed]

    if fixedSessions:
        for fixedSession in fixedSessions:
            available[fixedSession.day] = [x for x in available[fixedSession.day]
                                           if x not in list(range(fixedSession.hour, fixedSession.hour + fixedSession.length))]

    availableDays = [i for (i, x) in enumerate(available) if x]
    scheduledSessions = []
    shuffledSemester = random.sample(semester, len(semester))

    for session in semester:
        if session.isFixed:
            scheduledSessions.append(session)
            continue

        day, hour = selectAvailableDayAndHour(
            available, availableDays, session)

        if day is not False:
            session.day = day
            session.hour = hour
            available[day] = [x for x in available[day]
                              if x not in list(range(hour, hour + session.length))]
            availableDays = [i for (i, x) in enumerate(available) if x]

            scheduledSessions.append(session)

        else:
            return False

    return scheduledSessions


def selectAvailableDayAndHour(available, availableDays, session):
    count = 0

    while True:
        day = random.choice(availableDays)
        hour = random.choice(available[day])
        slots = list(range(hour, hour + session.length))

        if 12 in slots and 13 in slots:
            count += 1

        else:
            isAllAvailable = all(x in available[day] for x in slots)
            if (isAllAvailable):
                return day, hour
            count += 1

        if count > 50:
            if INITIALISATION_METHOD == 1:
                return False, False
            if INITIALISATION_METHOD == 2:
                return selectRandomDayAndHour(available, availableDays, session)


def selectRandomDayAndHour(available, availableDays, session):
    while True:
        day = random.choice(availableDays)
        length = session.length
        if length == 2:
            availableFor2 = [
                slot for slot in available[day] if slot != 17]
            if availableFor2:
                hour = random.choice(availableFor2)
            else:
                continue
        else:
            availableFor3 = [
                slot for slot in available[day] if slot not in [16, 17]]
            if availableFor3:
                hour = random.choice(availableFor3)
            else:
                continue

        return day, hour


def generateRandomSchedule():
    semesters = []

    for department in range(2):
        for year in range(1, 5):
            semester = list(filter(lambda session: session.course.department ==
                                   department and session.course.year == year, sessions))
            found = False

            while found == False or len(found) == 0:
                found = generateInitialSemesterSchedule(semester)
            semesters.extend(found)

    schedule = Schedule(semesters)

    return schedule


def generatePopulation(size):
    return [generateRandomSchedule() for _ in range(size)]


def performCrossover(schedule1, schedule2):
    index = random.choice(range(8))
    schedule1.semesters[index], schedule2.semesters[index] = schedule2.semesters[index], schedule1.semesters[index]

    newSchedule1 = Schedule(getStateFromSemesters(schedule1))
    newSchedule2 = Schedule(getStateFromSemesters(schedule2))

    return [newSchedule1, newSchedule2]


def selection(population, size, elite2):
    if INITIALISATION_METHOD == 1:
        scores = [max(schedule.fitness, 1) for schedule in population]
    else:
        sortedPopulation = sorted(
            population, key=lambda schedule: schedule.fitness)
        worstFitness = sortedPopulation[0].fitness
        offset = 0 - worstFitness
        scores = [schedule.fitness + offset for schedule in population]

    selected = random.choices(population, scores, k=size)
    selected.extend(elite2)
    return random.sample(selected, len(selected))


def crossover(population, size):
    newPopulation = []

    for index in range(size//2):
        willCrossover = random.choices(
            [True, False], [CROSSOVER_RATE, 1-CROSSOVER_RATE], k=1)

        if willCrossover:
            newSchedules = performCrossover(
                population[index * 2], population[index * 2 + 1])
            newPopulation.extend(newSchedules)
        else:
            newPopulation.append(population[index * 2])
            newPopulation.append(population[index * 2 + 1])

    return newPopulation


def safeMutation(schedule):
    n = random.choice(range(3))
    if n == 0:
        return mutateBySwapingSessions(schedule)
    if n == 1:
        return mutateByMovingSessionsIntoEmptySpaces(schedule)
    if n == 2:
        return mutateByMovingSessionVertically(schedule)


def correctiveMutation(schedule):
    n = random.choice(range(6))
    if n == 0:
        return mutateByMovingPeriod(schedule)
    if n == 1:
        return mutateBySwapingSessionsOfTeacher(schedule)
    if n == 2:
        return mutateByMovingSingleSessions(schedule)
    if n == 3:
        return mutateBySwapingSessionsOfCourse(schedule)
    if n == 4:
        return mutateBySwapingSessionsThatCannotCollide(schedule)
    if n == 5:
        return mutateBySlidingSessions(schedule)


def hybridMutation(schedule):
    n = random.choice(range(9))
    if n == 0:
        return mutateByMovingPeriod(schedule)
    if n == 1:
        return mutateBySwapingSessionsOfTeacher(schedule)
    if n == 2:
        return mutateByMovingSingleSessions(schedule)
    if n == 3:
        return mutateBySwapingSessionsOfCourse(schedule)
    if n == 4:
        return mutateBySwapingSessionsThatCannotCollide(schedule)
    if n == 5:
        return mutateBySwapingSessions(schedule)
    if n == 6:
        return mutateByMovingSessionsIntoEmptySpaces(schedule)
    if n == 7:
        return mutateByMovingSessionVertically(schedule)
    if n == 8:
        return mutateBySlidingSessions(schedule)


def smartMutation1(schedule):
    n = random.choice(range(2))
    if n == 0:
        return mutateByMovingPeriod(schedule)
    if n == 1:
        return mutateBySwapingSessionsOfTeacher(schedule)


def smartMutation2(schedule):
    n = random.choice(range(7))
    if n == 0:
        return mutateByMovingSingleSessions(schedule)
    if n == 1:
        return mutateBySwapingSessionsOfCourse(schedule)
    if n == 2:
        return mutateBySwapingSessionsThatCannotCollide(schedule)
    if n == 3:
        return mutateBySlidingSessions(schedule)
    if n == 4:
        return mutateBySwapingSessions(schedule)
    if n == 5:
        return mutateByMovingSessionsIntoEmptySpaces(schedule)
    if n == 6:
        return mutateByMovingSessionVertically(schedule)


def performMutation(schedule):
    if MUTATION_TYPE == 0:
        return safeMutation(schedule)

    if MUTATION_TYPE == 1:
        return correctiveMutation(schedule)

    if MUTATION_TYPE == 2:
        return hybridMutation(schedule)

    if MUTATION_TYPE == 3:
        if not schedule.isFeasible:
            return smartMutation1(schedule)
        else:
            return smartMutation2(schedule)


def mutateByMovingPeriod(schedule):
    if schedule.breakHourViolations:
        semester, day = random.choice(schedule.breakHourViolations)
    else:
        if MUTATION_TYPE == 3:
            return smartMutation2(schedule)
        return schedule

    availableSlotsOfDay = schedule.availableSlots[semester][day]
    morningSlots = [
        slot for slot in availableSlotsOfDay if slot in [9, 10, 11]]
    eveningSlots = [
        slot for slot in availableSlotsOfDay if slot in [14, 15, 16, 17]]

    sessionsOfDay = list(filter(
        lambda session: session.day == day, schedule.semesters[semester]))

    startTime = [session.hour for session in sessionsOfDay]
    morningPossible = []
    eveningPossible = []

    if sum(morningSlots):
        morningPossible = [slot for slot in range(
            morningSlots[0], 13) if slot in startTime]

    if sum(eveningSlots):
        eveningPossible = [slot for slot in range(
            12, eveningSlots[-1] + 1) if slot in startTime]

    period = random.randint(0, 1)

    if period == 0 and morningPossible:
        toMutate = [
            session for session in sessionsOfDay if session.hour in morningPossible]

        # make sure that a fixed session won't mutate
        for session in toMutate:
            if session.isFixed:
                return schedule

        for session in toMutate:
            if session.hour > 9:
                session.hour -= 1
        return Schedule(schedule.state)

    if period == 1 and eveningPossible:
        toMutate = [
            session for session in sessionsOfDay if session.hour in eveningPossible]

        # make sure that a fixed session won't mutate
        for session in toMutate:
            if session.isFixed:
                return schedule

        for session in toMutate:
            if session.hour + session.length < 18:
                session.hour += 1
        return Schedule(schedule.state)

    return schedule


def mutateBySwapingSessionsOfTeacher(schedule):
    if schedule.teacherCollisions:
        collision = random.choice(schedule.teacherCollisions)
    else:
        if MUTATION_TYPE == 3:
            return smartMutation2(schedule)
        return schedule

    for collidedSession in collision:
        swapableSessions = [session for session in schedule.state if isSafeToSwapTeacherCollision(
            session, collidedSession)]

        if swapableSessions:
            sessionToSwap = random.choice(swapableSessions)
            collidedSession.day, sessionToSwap.day = sessionToSwap.day, collidedSession.day
            collidedSession.hour, sessionToSwap.hour = sessionToSwap.hour, collidedSession.hour
            newSchedule = Schedule(schedule.state)

            return newSchedule

    return schedule


def mutateBySwapingSessionsThatCannotCollide(schedule):
    if schedule.cannotCollideViolations:
        collision = random.choice(schedule.cannotCollideViolations)
    else:
        if MUTATION_TYPE == 3:
            return smartMutation2(schedule)
        return schedule

    for collidedSession in collision:
        swapableSessions = [session for session in schedule.state if isSafeToSwapTeacherCollision(
            session, collidedSession)]

        if swapableSessions:
            sessionToSwap = random.choice(swapableSessions)
            collidedSession.day, sessionToSwap.day = sessionToSwap.day, collidedSession.day
            collidedSession.hour, sessionToSwap.hour = sessionToSwap.hour, collidedSession.hour
            newSchedule = Schedule(schedule.state)

            return newSchedule

    return schedule


def isSafeToSwapTeacherCollision(session, collidedSession):
    if session.course.id != collidedSession.course.id and \
            session.teacher.id != collidedSession.teacher.id and \
            session.course.year == collidedSession.course.year and \
            session.course.department == collidedSession.course.department and \
            session.length == collidedSession.length and \
            session.isFixed == False and \
            collidedSession.isFixed == False:
        return True
    else:
        return False


def mutateByMovingSingleSessions(schedule):

    if schedule.singleSessionDays:
        semesterIndex, day = random.choice(schedule.singleSessionDays)
    else:
        if MUTATION_TYPE == 3:
            return smartMutation2(schedule)
        return schedule

    semester = schedule.semesters[semesterIndex]
    if day in languageSlots[0]:
        return schedule

    sessions = [session for session in semester if session.day == day]
    if len(sessions) == 0:
        return schedule
    session = sessions[0]

    if session.isFixed:
        return schedule

    availableSlots = schedule.availableSlots[semesterIndex]

    length = session.length
    possibleSlots = []

    if length == 2:
        for availableSlotsOfDay in availableSlots:
            possibleSlots.append([
                slot for slot in availableSlotsOfDay if slot + 1 in availableSlotsOfDay])
    if length == 3:
        for availableSlotsOfDay in availableSlots:
            possibleSlots.append([slot for slot in availableSlotsOfDay if slot +
                                 1 in availableSlotsOfDay and slot + 2 in availableSlotsOfDay])
    allPossibleDays = []
    for day, daySlots in enumerate(possibleSlots):
        if daySlots:
            allPossibleDays.append(day)

    chosenDay = random.choice(allPossibleDays)
    chosenSlot = random.choice(possibleSlots[chosenDay])

    session.day = chosenDay
    session.hour = chosenSlot

    newSchedule = Schedule(schedule.state)

    return newSchedule


def mutateBySwapingSessionsOfCourse(schedule):
    if schedule.multipleCourseSessions:
        sessionsOfCourse = random.choice(schedule.multipleCourseSessions)
    else:
        if MUTATION_TYPE == 3:
            return smartMutation2(schedule)
        return schedule

    for sessionOfCourse in sessionsOfCourse:
        swapableSessions = [session for session in schedule.state if isSafeToSwapMultipleSessions(
            session, sessionOfCourse)]

        if swapableSessions:
            sessionToSwap = random.choice(swapableSessions)
            sessionOfCourse.day, sessionToSwap.day = sessionToSwap.day, sessionOfCourse.day
            sessionOfCourse.hour, sessionToSwap.hour = sessionToSwap.hour, sessionOfCourse.hour
            newSchedule = Schedule(schedule.state)

            return newSchedule

    return schedule


def isSafeToSwapMultipleSessions(session, sessionOfCourse):
    if session.course.id != sessionOfCourse.course.id and \
            session.course.year == sessionOfCourse.course.year and \
            session.course.department == sessionOfCourse.course.department and \
            session.length == sessionOfCourse.length and \
            session.isFixed == False and \
            sessionOfCourse.isFixed == False:
        return True
    else:
        return False


def mutateBySlidingSessions(schedule):
    if schedule.emptySlots:
        emptySlot = random.choice(schedule.emptySlots)
    else:
        if MUTATION_TYPE == 3:
            return smartMutation2(schedule)
        return schedule

    semester = schedule.semesters[emptySlot[0]]
    sessionsOfDay = [
        session for session in semester if session.day == emptySlot[1]]

    slot = emptySlot[2]

    if slot in [11, 12]:
        for session in sessionsOfDay:
            if session.hour + session.length - 1 < slot:
                session.hour += slot - (session.hour + session.length - 1)
    elif slot in [14, 15]:
        for session in sessionsOfDay:
            if session.hour > 14:
                session.hour -= session.hour - slot
    else:
        return schedule

    return Schedule(schedule.state)


def mutateBySwapingSessions(schedule):
    for _ in range(10):
        chosenSemester = random.choice(schedule.semesters)
        chosenSession = random.choice(chosenSemester)

        swapableSessions = [session for session in chosenSemester
                            if isSafeToRandomlySwapSessions(session, chosenSession, schedule.availableSlots)]

        if swapableSessions:
            sessionToSwap = random.choice(swapableSessions)
            chosenSession.day, sessionToSwap.day = sessionToSwap.day, chosenSession.day
            chosenSession.hour, sessionToSwap.hour = sessionToSwap.hour, chosenSession.hour
            newSchedule = Schedule(schedule.state)
            return newSchedule
    return schedule


def isSafeToRandomlySwapSessions(session, sessionToSwap, availableSlots):
    if session.isFixed == True and sessionToSwap.isFixed == True:
        return False

    if session.length == sessionToSwap.length:
        return True
    else:
        if session.length > sessionToSwap.length:
            shortSession = sessionToSwap
        else:
            shortSession = session

        semesterIndex = getSemesterIndex(
            shortSession.course.department, shortSession.course.year)
        dayIndex = shortSession.day
        followingSlot = shortSession.hour + shortSession.length

        if followingSlot == 13:
            return False

        if followingSlot == 12 and 13 not in availableSlots[semesterIndex][dayIndex]:
            return False

        if followingSlot in availableSlots[semesterIndex][dayIndex]:
            return True

        return False


def mutateByMovingSessionsIntoEmptySpaces(schedule):
    for _ in range(10):
        chosenSession = random.choice(schedule.state)
        if chosenSession.isFixed:
            continue
        availableSlots = getSemesterSlotsOfSession(chosenSession, schedule)
        consecutive = getConsecutiveSlots(availableSlots)

        possible = []
        for dayIndex, day in enumerate(consecutive):
            for groupIndex, group in enumerate(day):
                if len(group) >= chosenSession.length:
                    possible.append((dayIndex, groupIndex))

        if possible:
            chosenPeriodIndex = random.choice(possible)

            chosenDay = chosenPeriodIndex[0]
            chosenGroup = chosenPeriodIndex[1]
            chosenPeriod = consecutive[chosenDay][chosenGroup]

            possibleHours = chosenPeriod[:-(chosenSession.length-1)]
            chosenHour = random.choice(possibleHours)
            chosenSlots = list(
                range(chosenHour, chosenHour + chosenSession.length))

            availableSlotsOfChosen = availableSlots[chosenDay]
            slotsAfterMutation = [
                slot for slot in availableSlotsOfChosen if slot not in chosenSlots]

            if chosenDay in [2, 4] or 12 in slotsAfterMutation or 13 in slotsAfterMutation:
                chosenSession.day = chosenDay
                chosenSession.hour = chosenHour
                newSchedule = Schedule(schedule.state)
                return newSchedule
            else:
                continue

    return schedule


def mutateByMovingSessionVertically(schedule):
    for _ in range(10):
        chosenSession = random.choice(schedule.state)
        if chosenSession.isFixed:
            continue

        availableSlots = getSemesterSlotsOfSession(chosenSession, schedule)

        slotsOfDay = availableSlots[chosenSession.day]
        slotsOfSession = list(
            range(chosenSession.hour, chosenSession.hour + chosenSession.length))

        possible = getBorderingSlots(slotsOfDay, slotsOfSession)

        if possible:
            chosenHour = random.choice(possible)
            if chosenHour < chosenSession.hour:
                candidate = chosenHour

            if chosenHour > chosenSession.hour:
                difference = chosenHour - slotsOfSession[-1]
                candidate = chosenSession.hour + difference

            newSlotsOfSession = list(
                range(candidate, candidate + chosenSession.length))

            allSlots = slotsOfDay + slotsOfSession
            newAllSlots = [
                slot for slot in allSlots if slot not in newSlotsOfSession]

            if chosenSession.day in [2, 4] or 12 in newAllSlots or 13 in newAllSlots:
                chosenSession.hour = candidate
                newSchedule = Schedule(schedule.state)
                return newSchedule
            else:
                continue

    return schedule


def mutation(population, mutationRate):
    newPopulation = []

    for schedule in population:
        willMutate = random.choices(
            [True, False], [mutationRate, 1-mutationRate], k=1)

        if willMutate:
            newPopulation.append(performMutation(schedule))
        else:
            newPopulation.append(schedule)

    return newPopulation


def printInitilaPopulationFitness(population):
    sortedPopulation = sorted(
        population, key=lambda schedule: schedule.fitness, reverse=True)

    print(f'\n INITIAL POPULATION')

    for schedule in sortedPopulation:
        schedule.printFitness()
    average = sum([schedule.fitness for schedule in sortedPopulation]
                  ) / len(sortedPopulation)
    print(f'Average: {average}')


def printPopulationFitness(population, generation, stagnation, bestNonElite, bestSoFar, mutationRate, showAll=False):
    print(f'\nGENERATION {generation + 1}')

    if showAll:
        for schedule in population:
            schedule.printFitness()

    average = sum([schedule.fitness for schedule in population]
                  ) / len(population)

    print(f'Average: {round(average, 2)}')
    print(f'Best of Generation: {round(bestNonElite.fitness, 2)}')
    print(f'Best So Far: {round(bestSoFar.fitness, 2)}', end=' ')
    print('FEASIBLE') if bestSoFar.isFeasible else print('NON-FEASIBLE')
    print(f'stagnation = {stagnation}, mutation_rate = {mutationRate}')


def evolution():
    bestScore = float('-inf')
    bestSoFar = None
    stagnation = 0
    generation = 0

    hasReachedStagnationThreshold1 = False
    hasReachedStagnationThreshold2 = False
    hasReachedGenerationThreshold1 = False
    hasReachedGenerationThreshold2 = False

    mutationRate = MUTATION_RATE_1

    time0 = time.time()
    population = generatePopulation(SIZE)
    time1 = time.time()

    printInitilaPopulationFitness(population)

    sortedPopulation = sorted(
        population, key=lambda schedule: schedule.fitness, reverse=True)

    elite1 = sortedPopulation[:ELITE_SIZE//2]
    elite2 = sortedPopulation[ELITE_SIZE//2:ELITE_SIZE]

    while stagnation <= STAGNATION_LIMIT and generation <= GENERATION_LIMIT:

        population = selection(population, SIZE - ELITE_SIZE, elite2)
        population = crossover(population, SIZE - ELITE_SIZE//2)
        population = mutation(population, mutationRate)

        bestNonElite = sorted(
            population, key=lambda schedule: schedule.fitness, reverse=True)[0]

        population.extend(elite1)

        sortedPopulation = sorted(
            population, key=lambda schedule: schedule.fitness, reverse=True)

        elite1 = sortedPopulation[:ELITE_SIZE//2]
        elite2 = sortedPopulation[ELITE_SIZE//2:ELITE_SIZE]

        bestOfGeneration = sortedPopulation[0]

        if bestOfGeneration.fitness > bestScore:
            bestScore = bestOfGeneration.fitness
            bestSoFar = copy.deepcopy(bestOfGeneration)
            stagnation = 0

        if not hasReachedStagnationThreshold1 and stagnation >= STAGNATION_THRESHOLD_1:
            hasReachedStagnationThreshold1 = True
            mutationRate = MUTATION_RATE_2

        if not hasReachedStagnationThreshold2 and stagnation >= STAGNATION_THRESHOLD_2:
            hasReachedStagnationThreshold1 = True
            mutationRate = MUTATION_RATE_3

        if not hasReachedGenerationThreshold1 and generation >= GENERATION_THRESHOLD_1:
            hasReachedGenerationThreshold1 = True
            mutationRate = MUTATION_RATE_2

        if not hasReachedGenerationThreshold2 and generation >= GENERATION_THRESHOLD_2:
            hasReachedGenerationThreshold2 = True
            mutationRate = MUTATION_RATE_3

        printPopulationFitness(
            sortedPopulation, generation, stagnation, bestNonElite, bestSoFar, mutationRate, showAll=PRINT_GENERATION)

        stagnation += 1
        generation += 1

    time2 = time.time()

    exportSchedule(
        bestSoFar, name=f'{round(bestSoFar.fitness, 2)}, {STAGNATION_LIMIT}, {SIZE}')
    bestSoFar.printInfo()

    print(
        f'\nPopulation initialisation:\t{time1-time0}\nEvoluton total time:\t\t{time2-time1}')
    print(
        f'Time per generation:\t\t{(time2-time1)/generation}')

    return bestSoFar


constants = importEvolutionConstants()

SIZE = constants.get('SIZE', 100)
STAGNATION_LIMIT = constants.get('STAGNATION_LIMIT', 75)
ELITE_SIZE = constants.get('ELITE_SIZE', 12)

# 0: random / 1: corrective / 2: hybrid / 3: smart
MUTATION_TYPE = constants.get('MUTATION_TYPE', 3)

MUTATION_RATE_1 = constants.get('MUTATION_RATE_1', 0.1)
MUTATION_RATE_2 = constants.get('MUTATION_RATE_2', 0.2)
MUTATION_RATE_3 = constants.get('MUTATION_RATE_3', 0.3)

STAGNATION_THRESHOLD_1 = constants.get('STAGNATION_THRESHOLD_1', 15)
STAGNATION_THRESHOLD_2 = constants.get('STAGNATION_THRESHOLD_2', 35)

GENERATION_THRESHOLD_1 = constants.get('GENERATION_THRESHOLD_1', 50)
GENERATION_THRESHOLD_2 = constants.get('GENERATION_THRESHOLD_2', 100)
CROSSOVER_RATE = constants.get('CROSSOVER_RATE', 0.5)

GENERATION_LIMIT = constants.get('GENERATION_LIMIT', 1000)

# 1: greedy / 2: hybrid
INITIALISATION_METHOD = 2
