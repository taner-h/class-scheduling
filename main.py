import json
import time
import numpy as np
import random
import copy
import pickle
from collections import Counter


class Course:
    def __init__(self, id, name, code, department, year):
        self.id = id
        self.name = name
        self.code = code
        self.department = department
        self.year = year

    def print(self):
        print(f"{self.id}: {self.name} ({self.code}), {self.department}/{self.year}")


class Teacher:
    def __init__(self, id, firstName, lastName, unavailable):
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.unavailable = unavailable

    def print(self):
        print(f"{self.id}: {self.firstName} {self.lastName}")


class Session:
    def __init__(self, id, course, teacher, length, isLab=False, suffix=None):
        self.id = id
        self.course = course
        self.teacher = teacher
        self.length = length

        self.name = self.course.name if not isLab else self.course.name + ' - ' + suffix

        self.day = None
        self.hour = None

    def print(self):
        print(
            f"{self.id}: {self.name} ({self.length}), {self.teacher.firstName} {self.teacher.lastName}")

    def printSchedule(self):
        print(f"{self.id}: {self.name}, {getDayName(self.day)} {self.hour}.00 - {session.hour + session.length}.00")


class Schedule:
    def __init__(self, state):
        self.state = state

        self.semesters = self.filterSemesters()
        self.teacherSessions = self.filterByTeachers()

        self.semesterCollisions = self.calculateSemesterCollisions()
        self.teacherCollisions = self.calculateTeacherCollisions()
        self.multiTeacherCollisions = self.calculateMultiTeacherSessionCollisions()
        self.teacherAvailabilityViolations = self.calculateTeacherAvailabilityViolations()

        results = self.calculateConstraints()

        self.breakHourViolations = results[0]
        self.departmentMeetingViolations = results[1]
        self.fridayBreakViolations = results[2]
        self.languageSessionViolations = results[3]
        self.freeDays = results[4]
        self.singleSessionDays = results[5]
        self.multipleCourseSessions = results[6]
        self.slotSpan = results[7]
        self.availableSlots = results[8]

        isValid, fitness = self.calculateFitness()
        self.fitness = fitness
        self.isValid = isValid

    def filterSemesters(self):
        semesters = []
        for department in range(2):
            for year in range(1, 5):
                semester = list(filter(lambda session: session.course.department ==
                                       department and session.course.year == year, self.state))
                semesters.append(semester)

        return semesters

    def filterByTeachers(self):
        filtered = []
        for teacher in teachers:
            teacherSessions = list(
                filter(lambda session: session.teacher.id == teacher.id, self.state))
            filtered.append(teacherSessions)
        return filtered

    def print(self):
        for index, semester in enumerate(self.semesters):
            print(
                f"\n\n----- {getSemesterName(index // 4, index % 4 + 1)} -----\n\n")
            for day in range(5):
                semesterCopy = copy.deepcopy(semester)
                sessionsOfDay = list(filter(
                    lambda session: session.day == day, semesterCopy))
                ordered = sorted(
                    sessionsOfDay, key=lambda session: session.hour)
                print(f'\n{getDayName(day)}\n')
                for session in ordered:
                    print(
                        f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name}')
                if day in [1, 2]:
                    print('16.00 - 18.00 - Yabancı Dil')

    def printTeacherSessions(self):
        for sessionsOfTeacher in self.teacherSessions:
            if sessionsOfTeacher[0].teacher.firstName != "":
                print(
                    f'\n\n----- {sessionsOfTeacher[0].teacher.firstName} {sessionsOfTeacher[0].teacher.lastName} -----\n')
                for day in range(5):
                    sessionsOfDay = list(filter(
                        lambda session: session.day == day, sessionsOfTeacher))
                    if len(sessionsOfDay) != 0:
                        ordered = sorted(
                            sessionsOfDay, key=lambda session: session.hour)
                        print(f'\n{getDayName(day)}\n')
                        for session in ordered:
                            print(
                                f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name} ({getDepartmentShortName(session.course.department)}-{session.course.year})')

    def printSemesterCollisions(self):
        print(
            f'\n\n----- Donem Cakismalari ({len(self.semesterCollisions) + len(self.languageSessionViolations)}) -----\n')
        for collision in self.semesterCollisions:
            for session in collision:
                print(
                    f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name}')
            print()

        for collision in self.languageSessionViolations:
            for index, day in collision:
                print(
                    f'{getDayName(day)}: 16.00 - 18.00 - Yabancı Dil ({index})')
            print()

    def printTeacherCollisions(self):
        print(
            f'\n\n----- Ogretmen Cakismalari ({len(self.teacherCollisions) + len(self.multiTeacherCollisions)}) -----\n')

        for collision in self.teacherCollisions:
            print(
                f'{collision[0].teacher.firstName} {collision[0].teacher.lastName}')
            for session in collision:
                print(
                    f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name} ({getDepartmentShortName(session.course.department)})')
            print()
        for collision in self.multiTeacherCollisions:
            print(
                f'{collision[0].teacher.firstName} {collision[0].teacher.lastName}')
            for session in collision:
                print(
                    f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name} ({getDepartmentShortName(session.course.department)})')
            print()

    def printBreakHourViolations(self):
        print(
            f'\n\n----- Öğle Arası İhlalleri ({len(self.fridayBreakViolations) + len(self.breakHourViolations) + len(self.departmentMeetingViolations)}) -----\n')
        for index, day in self.breakHourViolations:
            print(f'Öğle Arası İhlali: {index}, {getDayName(day)}')

        for index in self.fridayBreakViolations:
            print(f'Cuma Arası İhlali: {index}')

        for index in self.departmentMeetingViolations:
            print(f'Bölüm Toplantısı İhlali: {index}')

    def printAvailabilityCollisions(self):
        print(
            f'\n\n----- Uygunluk Cakismalari ({len(self.teacherAvailabilityViolations)}) -----\n')
        for collision in self.teacherAvailabilityViolations:
            for session in collision:
                print(f'{session.teacher.firstName} {session.teacher.lastName}')
                print(
                    f'{getDayName(session.day)}: {session.hour}.00 - {session.hour + session.length}.00 - {session.name}')
            print()

    def printAvailableSlots(self):
        print('\n\n----- Uygun Slotlar -----\n')
        for index, semester in enumerate(self.availableSlots):
            print(f'\n\n{index}:', end=' ')
            for index, day in enumerate(semester):
                print(f'{getDayName(index)}: {day}', end=', ')

    def printScore(self):
        print(f'fitness: {round(self.fitness, 2)} (isValid: {self.isValid})')

    def calculateSemesterCollisions(self):
        collisions = []
        for semester in self.semesters:
            for day in range(5):
                sessionsOfDay = list(filter(
                    lambda session: session.day == day, semester))
                usedSlots = []
                sessionIds = []
                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))
                    sessionIds.extend([session.id] * session.length)
                collisionSlots = [
                    item for item, count in Counter(usedSlots).items() if count > 1]
                for collisionSlot in collisionSlots:
                    indices = [index for index, slot in enumerate(
                        usedSlots) if slot == collisionSlot]
                    collisionSessions = []
                    for index in indices:
                        collisionSession = list(filter(
                            lambda session: session.id == sessionIds[index], sessionsOfDay))[0]
                        collisionSessions.append(collisionSession)
                    collisions.append(collisionSessions)
        return collisions

    def calculateTeacherCollisions(self):
        collisions = []
        for sessionsOfTeacher in self.teacherSessions:
            for day in range(5):
                sessionsOfDay = list(filter(
                    lambda session: session.day == day, sessionsOfTeacher))
                usedSlots = []
                sessionIds = []

                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))
                    sessionIds.extend([session.id] * session.length)
                collisionSlots = [
                    item for item, count in Counter(usedSlots).items() if count > 1]
                for collisionSlot in collisionSlots:
                    indices = [index for index, slot in enumerate(
                        usedSlots) if slot == collisionSlot]
                    collisionSessions = []
                    for index in indices:
                        collisionSession = list(filter(
                            lambda session: session.id == sessionIds[index], sessionsOfDay))[0]
                        collisionSessions.append(collisionSession)
                    collisions.append(collisionSessions)
        return collisions

    def calculateMultiTeacherSessionCollisions(self):
        collisions = []

        for teacherId in multiTeachers:
            sessionsOfTeacher = list(
                filter(lambda session: session.teacher.id == teacherId, self.state))
            multiTeacherSession = [
                session for session in self.state if session.course.id == multiTeacherCourseId][0]
            sessionsOfTeacher.append(multiTeacherSession)
            # for session in sessionsOfTeacher:
            #     print(f'{session.name}, {session.day}, {session.hour}')

            for day in range(5):
                sessionsOfDay = list(filter(
                    lambda session: session.day == day, sessionsOfTeacher))
                usedSlots = []
                sessionIds = []

                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))
                    sessionIds.extend([session.id] * session.length)
                collisionSlots = [
                    item for item, count in Counter(usedSlots).items() if count > 1]
                for collisionSlot in collisionSlots:
                    indices = [index for index, slot in enumerate(
                        usedSlots) if slot == collisionSlot]
                    collisionSessions = []
                    for index in indices:
                        collisionSession = list(filter(
                            lambda session: session.id == sessionIds[index], sessionsOfDay))[0]
                        collisionSessions.append(collisionSession)
                    collisions.append(collisionSessions)

                # if sum(collisionCount) > 0:
                #     print(collisionCount)
                #     print(sessionsOfTeacher[0].teacher.id)
        return collisions

    def calculateTeacherAvailabilityViolations(self):
        collisions = []
        for sessionsOfTeacher in self.teacherSessions:
            teacher = sessionsOfTeacher[0].teacher
            for day in range(5):
                sessionsOfDay = list(filter(
                    lambda session: session.day == day, sessionsOfTeacher))

                usedSlots = []
                sessionIds = []
                unavailableSlotsOfDay = teacher.unavailable[day]

                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))
                    sessionIds.extend([session.id] * session.length)

                collisionSlots = [
                    slot for slot in usedSlots if slot in unavailableSlotsOfDay]
                # collisionSlots = [
                #     item for item, count in Counter(usedSlots).items() if count > 1]
                for collisionSlot in collisionSlots:
                    indices = [index for index, slot in enumerate(
                        usedSlots) if slot == collisionSlot]
                    collisionSessions = []
                    for index in indices:
                        collisionSession = list(filter(
                            lambda session: session.id == sessionIds[index], sessionsOfDay))[0]
                        collisionSessions.append(collisionSession)
                    collisions.append(collisionSessions)
        return collisions

    def calculateBreakHourViolations(self):
        totalViolations = []
        semesterIndex = 0
        for semester in self.semesters:
            for day in [0, 1, 3]:
                sessionsOfDay = list(filter(
                    lambda session: session.day == day, semester))
                usedSlots = []
                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))
                if 12 in usedSlots and 13 in usedSlots:
                    totalViolations.append((semesterIndex, day))
                    # print(f'VIOLATION = {semesterIndex}, {getDayName(day)}')
            semesterIndex += 1
        return totalViolations

    def calculateDepartmentMeetingViolations(self):
        totalViolations = []
        semesterIndex = 0
        day = 2
        for semester in self.semesters:
            sessionsOfDay = list(filter(
                lambda session: session.day == day, semester))
            usedSlots = []
            for session in sessionsOfDay:
                usedSlots.extend(
                    list(range(session.hour, session.hour + session.length)))
            if 13 in usedSlots:
                totalViolations.append(semesterIndex)
            semesterIndex += 1
        return totalViolations

    def calculateFridayBreakViolations(self):
        totalViolations = []
        semesterIndex = 0
        day = 4
        for semester in self.semesters:
            sessionsOfDay = list(filter(
                lambda session: session.day == day, semester))
            usedSlots = []
            for session in sessionsOfDay:
                usedSlots.extend(
                    list(range(session.hour, session.hour + session.length)))
            if 12 in usedSlots or 13 in usedSlots:
                totalViolations.append(semesterIndex)
            semesterIndex += 1
        return totalViolations

    def hasAllSessions(self):
        return len(self.state) == 87

    def calculateFreeDays(self):
        totalFreeDays = []
        for index, semester in enumerate(self.semesters):
            for day in range(5):
                sessionsOfDay = list(filter(
                    lambda session: session.day == day, semester))
                usedSlots = []
                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))
                if len(usedSlots) == 0 and day not in [1, 2]:
                    totalFreeDays.append(index)
        return totalFreeDays

    def calculateConstraints(self):
        breakViolations = []
        meetingViolations = []
        fridayViolations = []
        freeDays = []
        singleSessionDays = []
        multipleSessions = []
        totalSlotSpan = []
        languageSessionViolations = []
        allAvailableSlots = []

        for index, semester in enumerate(self.semesters):
            semesterSlotSpan = []
            semesterAvailableSlots = calculateAvailableSlots()
            for day in range(5):
                sessionsOfDay = list(filter(
                    lambda session: session.day == day, semester))
                usedSlots = []
                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))

                semesterAvailableSlots[day] = [
                    slot for slot in semesterAvailableSlots[day] if slot not in usedSlots]
                # Check for break violations:
                if day in [0, 1, 4] and (12 in usedSlots and 13 in usedSlots):
                    breakViolations.append((index, day))
                # Check for free days
                if len(usedSlots) == 0 and day not in [1, 2]:
                    freeDays.append((index, day))
                # Check for friday violations
                if day == 4 and (12 in usedSlots or 13 in usedSlots):
                    fridayViolations.append(index)
                # Check for meeting violations
                if day == 2 and 13 in usedSlots:
                    meetingViolations.append(index)
                # Check for language session violations
                if day in [1, 2] and (16 in usedSlots or 17 in usedSlots):
                    languageSessionViolations.append((index, day))
                # Check for single-session days
                if len(sessionsOfDay) == 1 and day in [0, 3, 4]:
                    singleSessionDays.append((index, day))
                if len(sessionsOfDay) == 0 and day in [1, 2]:
                    singleSessionDays.append((index, day))
                # Check for multiple sessions of same course in the same day
                courseIds = [session.course.id for session in sessionsOfDay]
                multipleSessionCourseIds = [
                    item for item, count in Counter(courseIds).items() if count > 1]
                for multipleSessionCourseId in multipleSessionCourseIds:
                    sessionsOfCourse = list(filter(
                        lambda session: session.course.id == multipleSessionCourseId, sessionsOfDay))
                    multipleSessions.append(sessionsOfCourse)
                # Calculate the slot span
                if len(usedSlots) != 0:
                    earliestSlot = min(usedSlots)
                    latestSlot = max(usedSlots)
                    slotSpan = latestSlot - earliestSlot + 1
                    semesterSlotSpan.append(slotSpan)
                else:
                    semesterSlotSpan.append(0)
            totalSlotSpan.append(semesterSlotSpan)
            allAvailableSlots.append(semesterAvailableSlots)
        # print(totalSlotSpan)
        # print(sum([sum(semesterSlotSpan)
        #       for semesterSlotSpan in totalSlotSpan]))

        # for course in multipleSessions:
        #     for session in course:
        #         print(
        #             f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name}')
        violations = [breakViolations, meetingViolations, fridayViolations, languageSessionViolations,
                      freeDays, singleSessionDays, multipleSessions, totalSlotSpan, allAvailableSlots]

        return violations

    def calculateAvailableSlots():
        allAvailableSlots = []
        for semester in self.semesters:
            for day in range(5):
                sessionsOfDay = list(filter(
                    lambda session: session.day == day, semester))
                usedSlots = []
                allSlots = [list(range(9, 18))] * 5
                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))

    def calculateFitness(self):
        #! Hard Constraints
        semesterCollisionCount = len(self.semesterCollisions)
        languageSessionViolationCount = len(self.languageSessionViolations)
        teacherCollisionCount = len(self.teacherCollisions)
        multiTeacherCollisionCount = len(self.multiTeacherCollisions)
        breakHourViolationCount = len(self.breakHourViolations)
        fridayBreakViolationCount = len(self.fridayBreakViolations)
        departmentMeetingViolationCount = len(self.departmentMeetingViolations)

        # ? Soft Constraints
        teacherAvailabilityViolationCount = len(
            self.teacherAvailabilityViolations)
        freeDayCount = len(self.freeDays)
        singleSessionDayCount = len(self.singleSessionDays)
        multipleCourseSessionCount = len(self.multipleCourseSessions)
        slotSpan = sum([sum(semesterSlotSpan)
                       for semesterSlotSpan in self.slotSpan])

        score = 50.0
        isValid = False

        score -= 2 * (semesterCollisionCount + teacherCollisionCount +
                      multiTeacherCollisionCount + languageSessionViolationCount)
        score -= 3 * (fridayBreakViolationCount +
                      departmentMeetingViolationCount + departmentMeetingViolationCount)

        hardConstraintsTotal = semesterCollisionCount + teacherCollisionCount + multiTeacherCollisionCount + fridayBreakViolationCount + \
            breakHourViolationCount + departmentMeetingViolationCount + \
            languageSessionViolationCount

        score -= 0.5 * teacherAvailabilityViolationCount
        score += 2 * freeDayCount
        score -= 0.3 * singleSessionDayCount
        score -= 0.5 * multipleCourseSessionCount
        score -= 0.1 * (slotSpan - 210)

        if (hardConstraintsTotal):
            score -= 0.1 * score
            isValid = False
        else:
            score += 10
            isValid = True

        return isValid, score


def getSemesterName(department, year):
    departmentName = 'Bilgisayar Mühendisliği' if department == 0 else 'Endüstri Mühendisliği'
    return f"{departmentName} - {year}. Sınıf"


def getDepartmentName(department):
    return 'Bilgisayar Mühendisliği' if department == 0 else 'Endüstri Mühendisliği'


def getDepartmentShortName(department):
    return 'BM' if department == 0 else 'EM'


def getDayName(day):
    days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']
    return days[day]


def generateInitialSemesterSchedule(semester):
    semester = copy.deepcopy(semester)
    available = copy.deepcopy(availableSlots)
    availableDays = [i for (i, x) in enumerate(available) if x]
    scheduledSessions = []
    shuffledSemester = random.sample(semester, len(semester))
    for session in semester:
        day, hour = selectAvailableDayAndHour(
            available, availableDays, session)
        if day is not False:
            session.day = day
            session.hour = hour
            available[day] = [x for x in available[day]
                              if x not in list(range(hour, hour + session.length))]
            availableDays = [i for (i, x) in enumerate(available) if x]

            scheduledSessions.append(session)

            # if 12 in available[day] or 13 in available[day]:
            #     scheduledSessions.append(session)
            # else:
            #     return False
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


def importData():
    with open('./data/teachers.json', encoding='utf-8') as json_file:
        teachers_json = json.load(json_file)

    with open('./data/courses.json', encoding='utf-8') as json_file:
        courses_json = json.load(json_file)

    with open('./data/fixedSlots.json', encoding='utf-8') as json_file:
        fixedSlots = json.load(json_file)
    return teachers_json, courses_json, fixedSlots


def generateObjects():
    teachers = []
    for teacher in teachers_json:
        teachers.append(Teacher(
            teacher['id'], teacher['firstName'], teacher['lastName'], teacher['unavailable']))

    courses = []
    for course in courses_json:
        courses.append(Course(course['id'], course['name'],
                              course['code'], course['department'], course['year']))

    sessions = []
    index = 0
    for course in courses_json:
        for session in course['sessions']:
            sessions.append(
                Session(index, courses[course['id']], teachers[session['teacherId']],
                        session['length'], isLab=session.get("isLab", False), suffix=session.get("suffix", None)))
            index += 1

    return teachers, courses, sessions


def calculateAvailableSlots():
    allSlots = [list(range(9, 18))] * 5
    availableSlots = []
    for i in range(5):
        availableSlots.append(
            [x for x in allSlots[i] if x not in fixedSlots[i]])
    return availableSlots


def getMultiTeacherCourse():
    return next(
        (course['id'], course['teachers']) for course in courses_json if course.get("hasMultiTeachers", False) == True)


def performCrossover(schedule1, schedule2):
    index = random.choice(range(8))
    schedule1.semesters[index], schedule2.semesters[index] = schedule2.semesters[index], schedule1.semesters[index]

    # schedule1.print()
    # schedule2.print()

    newSchedule1 = Schedule(getStateFromSemesters(schedule1))
    newSchedule2 = Schedule(getStateFromSemesters(schedule2))

    return [newSchedule1, newSchedule2]


def getStateFromSemesters(schedule):
    sessions = []
    for semester in schedule.semesters:
        for session in semester:
            sessions.append(session)
    return sessions


def selection(population):
    scores = [schedule.fitness for schedule in population]
    return random.choices(population, scores, k=SIZE)


def crossover(population):
    newPopulation = []
    for index in range(SIZE//2):
        newSchedules = performCrossover(
            population[index * 2], population[index * 2 + 1])
        newPopulation.extend(newSchedules)
    return newPopulation


SIZE = 32

teachers_json, courses_json, fixedSlots = importData()
teachers, courses, sessions = generateObjects()
multiTeacherCourseId, multiTeachers = getMultiTeacherCourse()
availableSlots = calculateAvailableSlots()


# schedule = generateRandomSchedule()
# # schedule.printTeacherSessions()
# schedule.print()
# schedule.printSemesterCollisions()
# schedule.printTeacherCollisions()
# schedule.printAvailabilityCollisions()
# schedule.printScore()

# * Checking multi-teacher session
# print(multiTeacherCourseId)
# print(multiTeachers)

# * Checking for collisions
# schedule.state[0].day = 0
# schedule.state[0].hour = 9
# schedule.state[0].length = 8
# schedule.print()
# schedule.semesterCollisions = schedule.calculateSemesterCollisions()
# schedule.languageSessionViolations = schedule.calculateConstraints()[3]
# schedule.printSemesterCollisions()

population = generatePopulation(SIZE)
for i in range(10):
    sortedPopulation = sorted(
        population, key=lambda schedule: schedule.fitness, reverse=True)
    print(f'\n ITERATION {i + 1}')
    for schedule in sortedPopulation:
        schedule.printScore()

    average = sum([schedule.fitness for schedule in sortedPopulation]
                  ) / len(sortedPopulation)
    print(f'\nAverage: {average}\n')

    selected = selection(population)
    population = crossover(selected)

sortedPopulation = sorted(
    population, key=lambda schedule: schedule.fitness, reverse=True)

best = sortedPopulation[0]

best.print()
best.printAvailableSlots()
best.printSemesterCollisions()
best.printTeacherCollisions()
best.printBreakHourViolations()
best.printAvailabilityCollisions()
best.printScore()

# ? Export to file
# dbfile = open('output/best', 'ab')
# pickle.dump(sortedPopulation[0], dbfile)
# dbfile.close()

# * Import from file
# dbfile = open('best2', 'rb')
# schedules = pickle.load(dbfile)
# dbfile.close()

# s1, s2 = performCrossover(schedules[0], schedules[1])


# schedule = schedules[1]

# # s1.print()
# s1.printSemesterCollisions()
# s1.printTeacherCollisions()
# s1.printAvailabilityCollisions()
# s1.printScore()

# # s2.print()
# s2.printSemesterCollisions()
# s2.printTeacherCollisions()
# s2.printAvailabilityCollisions()
# s1.printScore()
# s2.printScore()
