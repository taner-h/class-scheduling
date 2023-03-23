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
        self.breakHourViolations = self.calculateBreakHourViolations()
        self.departmentMeetingViolations = self.calculateDepartmentMeetingViolations()
        self.fridayBreakViolations = self.calculateFridayBreakViolations()

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

    def calculateSemesterCollisions(self):
        totalCollisions = 0
        for semester in self.semesters:
            for day in range(5):
                sessionsOfDay = list(filter(
                    lambda session: session.day == day, semester))
                usedSlots = []
                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))
                    # sessionIds.extend([session.id] * session.length)
                collisionCount = [
                    count - 1 for item, count in Counter(usedSlots).items() if count > 1]
                totalCollisions += sum(collisionCount)
                # seen = set()
                # collisions = [x for x in usedSlots if x in seen or seen.add(x)]
                # for collision in collisions:
                #     collisionIndex = [i for i, slot in enumerate(usedSlots) if slot == collision]
                #     for i in collisionIndex:
                #         totalCollisions.append(sessionIds[i])
        return totalCollisions

    def calculateTeacherCollisions(self):
        totalCollisions = 0

        for sessionsOfTeacher in self.teacherSessions:
            for day in range(5):
                sessionsOfDay = list(filter(
                    lambda session: session.day == day, sessionsOfTeacher))
                usedSlots = []
                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))

                collisionCount = [
                    count - 1 for item, count in Counter(usedSlots).items() if count > 1]
                # if sum(collisionCount) > 0:
                #     print(collisionCount)
                #     print(sessionsOfTeacher[0].teacher.id)
                totalCollisions += sum(collisionCount)
        return totalCollisions

    def calculateMultiTeacherSessionCollisions(self):
        totalCollisions = 0

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
                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))
                collisionCount = [
                    count - 1 for item, count in Counter(usedSlots).items() if count > 1]
                # if sum(collisionCount) > 0:
                #     print(collisionCount)
                #     print(sessionsOfTeacher[0].teacher.id)
        return totalCollisions

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
            semester = filter(lambda session: session.course.department ==
                              department and session.course.year == year, sessions)
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


# * Checking multi-teacher session
# print(multiTeacherCourseId)
# print(multiTeachers)

# * Checking for collisions
# schedule.state[0].day = 0
# schedule.state[0].hour = 9
# schedule.state[0].length = 9
# schedule.print()
# schedule.calculateSemesterCollisions()
