from classes import Teacher, Session, Course, Schedule, teachers, courses, sessions
from utils import *
from export import *
import copy
import random
import time

PRINT_GENERATION = False
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.2


def generateInitialSemesterSchedule(semester):
    semester = copy.deepcopy(semester)
    # available = copy.deepcopy(availableSlots)
    available = calculateAvailableSlots()
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
            return False, False


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


def selection(population, size):
    scores = [max(schedule.fitness, 0) for schedule in population]
    return random.choices(population, scores, k=size)


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


def performMutation(schedule):
    mutation = random.choice(range(5))
    if mutation == 0:
        return mutateByMovingPeriod(schedule)
    if mutation == 1:
        return mutateBySwapingSessions(schedule)
    if mutation == 2:
        return mutateByMovingSession(schedule)
    if mutation == 3:
        return mutateBySwapingSessionsOfCourse(schedule)
    if mutation == 4:
        return mutateBySwapingSessionsThatCannotCollide(schedule)


def mutateByMovingPeriod(schedule):
    if schedule.breakHourViolations:
        semester, day = random.choice(schedule.breakHourViolations)
    else:
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


def mutateBySwapingSessions(schedule):
    if schedule.teacherCollisions:
        collision = random.choice(schedule.teacherCollisions)
    else:
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


def mutateByMovingSession(schedule):

    if schedule.singleSessionDays:
        semesterIndex, day = random.choice(schedule.singleSessionDays)
    else:
        return schedule

    semester = schedule.semesters[semesterIndex]
    if day in [1, 2]:
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


def mutation(population):
    newPopulation = []
    for schedule in population:
        willMutate = random.choices(
            [True, False], [MUTATION_RATE, 1-MUTATION_RATE], k=1)
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


def printPopulationFitness(population, generation, stagnation, bestSoFar, showAll=False):

    print(f'\nGENERATION {generation + 1}')
    if showAll:
        for schedule in population:
            schedule.printFitness()

    average = sum([schedule.fitness for schedule in population]
                  ) / len(population)
    print(f'Average: {round(average, 2)}')
    print(f'Best of Generation: {round(population[0].fitness, 2)}')
    print(f'Best So Far: {round(bestSoFar.fitness, 2)}', end=' ')
    print('VALID') if bestSoFar.isValid else print('INVALID')
    print(f'stagnation = {stagnation}')


def evolution(size, limit, population):
    bestScore = 0
    bestSoFar = None
    stagnation = 0
    generation = 0

    time0 = time.time()
    printInitilaPopulationFitness(population)
    time1 = time.time()

    mutateBySwapingSessionsOfCourse(population[0])

    while stagnation <= limit:
        population = selection(population, size)
        # population = crossover(population, size)
        population = mutation(population)

        sortedPopulation = sorted(
            population, key=lambda schedule: schedule.fitness, reverse=True)

        bestOfGeneration = sortedPopulation[0]

        if bestOfGeneration.fitness > bestScore:
            bestScore = bestOfGeneration.fitness
            bestSoFar = bestOfGeneration
            stagnation = 0

        printPopulationFitness(
            sortedPopulation, generation, stagnation, bestSoFar, showAll=PRINT_GENERATION)

        stagnation += 1
        generation += 1

    time2 = time.time()

    exportSchedule(
        bestSoFar, name=f'{round(bestSoFar.fitness, 2)}, {limit}, {size}')
    bestSoFar.printInfo()

    print(f'init: {time1-time0}, evol: {time2-time1}')
    print(
        f'init per schedule: {(time1-time0)/64}, evol per schedule: {(time2-time1)/generation}')

    return bestSoFar
