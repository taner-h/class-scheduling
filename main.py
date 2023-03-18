import json
import time
import numpy as np


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


class Schedule:
    def __init__(self, state):
        self.state = state

        self.f = None
        self.isValid = None


with open('./data/teachers.json', encoding='utf-8') as json_file:
    teachers_json = json.load(json_file)

with open('./data/courses.json', encoding='utf-8') as json_file:
    courses_json = json.load(json_file)

with open('./data/fixedSlots.json', encoding='utf-8') as json_file:
    fixedSlots = json.load(json_file)

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

for department in range(2):
    for year in range(1, 5):
        semester = filter(lambda session: session.course.department ==
                          department and session.course.year == year, sessions)
        print(f'Department: {department}, year: {year}')
        for session in semester:
            session.print()
