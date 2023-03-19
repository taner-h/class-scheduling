import json
import time
import numpy as np
import random
import copy


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
        print(
            f"{self.id}: {self.name} ({self.length}), {self.day} {self.hour}.00 - {self.length } hours")


class Schedule:
    def __init__(self, state):
        self.state = state

        self.f = None
        self.isValid = None

    def print(self):
        for department in range(2):
            for year in range(1, 5):
                print(
                    f"\n\n----- {getSemesterName(department, year)} -----\n\n")
                semester = filter(lambda session: session.course.department ==
                                  department and session.course.year == year, self.state)
                for day in range(5):
                    semesterCopy = copy.deepcopy(semester)
                    sessionsOfDay = filter(
                        lambda session: session.day == day, semesterCopy)
                    ordered = sorted(
                        sessionsOfDay, key=lambda session: session.hour)
                    print(f'\n{getDayName(day)}\n')
                    for session in ordered:
                        print(
                            f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name}')


def getSemesterName(department, year):
    departmentName = 'Bilgisayar Mühendisliği' if department == 0 else 'Endüstri Mühendisliği'
    return f"{departmentName} - {year}. Sınıf"


def getDayName(day):
    days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']
    return days[day]


def generateInitialSemesterSchedule(semester):
    semester = copy.deepcopy(semester)
    available = copy.deepcopy(availableSlots)
    availableDays = [i for (i, x) in enumerate(available) if x]
    scheduledSessions = []
    # print(availableDays)
    for session in semester:
        # session.print()
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
        isAllAvailable = all(x in available[day] for x in list(
            range(hour, hour + session.length)))
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
            while found == False:
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
    availableSlots.append(
        [x for x in allSlots[i] if x not in fixedSlots[i]])

# semesters = []
# for department in range(2):
#     for year in range(1, 5):
#         semester = filter(lambda session: session.course.department ==
#                           department and session.course.year == year, sessions)
#         found = False
#         while found == False:
#             found = generateInitialSemesterSchedule(semester)
#         semesters.extend(found)
    # for day in range(5):
    #     sessionsOfDay = filter(lambda session: session.day == day, found)
    #     ordered = sorted(sessionsOfDay, key=lambda session: session.hour)
    #     print(f'\nDay {day}\n')
    #     for session in ordered:
    #         session.printSchedule()

time1 = time.time()
SIZE = 16
population = generatePopulation(SIZE)
population[0].print()
time2 = time.time()

print((time2-time1)*1000, 'ms')
