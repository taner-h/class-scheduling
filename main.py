import json
import time
import numpy as np
import random
import copy
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
        self.freeDays = results[3]
        self.singleSessionDays = results[4]
        self.multipleCourseSessions = results[5]
        self.teacherAvailabilityViolations = results[6]

        self.f = None
        self.isValid = None

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
            f'\n\n-----Donem Cakismalari ({len(self.semesterCollisions)}) -----\n')
        for collision in self.semesterCollisions:
            for session in collision:
                print(
                    f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name}')
            print()

    def printTeacherCollisions(self):
        print(
            f'\n\n-----Ogretmen Cakismalari ({len(self.teacherCollisions) + len(self.multiTeacherCollisions)}) -----\n')

        for collision in self.teacherCollisions:
            print(
                f'\n{collision[0].teacher.firstName} {collision[0].teacher.lastName}\n')
            for session in collision:
                print(
                    f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name} ({getDepartmentShortName(session.course.department)})')
            print()
        for collision in self.multiTeacherCollisions:
            print(
                f'\n{collision[0].teacher.firstName} {collision[0].teacher.lastName}\n')
            for session in collision:
                print(
                    f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name} ({getDepartmentShortName(session.course.department)})')
            print()

    def printAvailabilityCollisions(self):
        print(
            f'\n\n----- Uygunluk Cakismalari ({len(self.teacherAvailabilityViolations)}) -----\n')
        for collision in self.teacherAvailabilityViolations:
            for session in collision:
                print(f'{session.teacher.firstName} {session.teacher.lastName}')
                print(
                    f'{getDayName(session.day)}: {session.hour}.00 - {session.hour + session.length}.00 - {session.name}')
            print()

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

        for index, semester in enumerate(self.semesters):
            semesterSlotSpan = []
            for day in range(5):
                sessionsOfDay = list(filter(
                    lambda session: session.day == day, semester))
                usedSlots = []
                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))
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
        # print(totalSlotSpan)
        # print(sum([sum(semesterSlotSpan)
        #       for semesterSlotSpan in totalSlotSpan]))

        # for course in multipleSessions:
        #     for session in course:
        #         print(
        #             f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name}')
        violations = [breakViolations, meetingViolations,
                      fridayViolations, freeDays, singleSessionDays, multipleSessions, totalSlotSpan]
        # for violation in violations:
        #     print(violation)
        return violations


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


with open('./data/teachers.json', encoding='utf-8') as json_file:
    teachers_json = json.load(json_file)

with open('./data/courses.json', encoding='utf-8') as json_file:
    courses_json = json.load(json_file)

with open('./data/fixedSlots.json', encoding='utf-8') as json_file:
    fixedSlots = json.load(json_file)

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

allSlots = [list(range(9, 18))] * 5

availableSlots = []
for i in range(5):
    availableSlots.append([x for x in allSlots[i] if x not in fixedSlots[i]])

multiTeacherCourseId, multiTeachers = next(
    (course['id'], course['teachers']) for course in courses_json if course.get("hasMultiTeachers", False) == True)
multiTeacherSessionId = next(
    session.id for session in sessions if session.course.id == multiTeacherCourseId)

schedule = generateRandomSchedule()
# schedule.printTeacherSessions()
schedule.print()
schedule.printSemesterCollisions()
schedule.printTeacherCollisions()
schedule.printAvailabilityCollisions()

# * Checking multi-teacher session
# print(multiTeacherCourseId)
# print(multiTeachers)

# * Checking for collisions
# schedule.state[0].day = 0
# schedule.state[0].hour = 9
# schedule.state[0].length = 9
# schedule.print()
# schedule.semesterCollisions = schedule.calculateSemesterCollisions()
# schedule.printSemesterCollisions()
