import json
from operator import itemgetter
from itertools import groupby


def getConsecutiveSlots(slots):
    consecutive = [[], [], [], [], []]
    for index, day in enumerate(slots):
        for k, g in groupby(enumerate(day), lambda i: i[0]-i[1]):
            group = list(map(itemgetter(1), g))
            if len(group) > 1:
                consecutive[index].append(group)
    return consecutive


def calculateAvailableSlots():
    fixedSlots = importFixed()
    allSlots = [list(range(9, 18))] * 5
    availableSlots = []
    for i in range(5):
        availableSlots.append(
            [x for x in allSlots[i] if x not in fixedSlots[i]])
    return availableSlots


def getSlotsOfFixedSessionsOfSemester(semester, fixedSessions):
    slots = [[], [], [], [], []]
    for fixedSession in fixedSessions:
        slots[fixedSession.day].extend(
            list(range(fixedSession.hour, fixedSession.hour + fixedSession.length)))
    return slots


def getSemesterIndex(department, year):
    return (4 * department) + year - 1


def getSemesterSlotsOfSession(session, schedule):
    index = getSemesterIndex(session.course.department, session.course.year)
    return schedule.availableSlots[index]


def getSemesterName(department, year):
    departmentName = 'Bilgisayar Mühendisliği' if department == 0 else 'Endüstri Mühendisliği'
    return f"{departmentName} - {year}. Sınıf"


def getSemesterShortName(semester):
    department = 'BM' if semester // 4 == 0 else 'EM'
    year = semester % 4 + 1
    return f'{department}-{year}'


def getDepartmentName(department):
    return 'Bilgisayar Mühendisliği' if department == 0 else 'Endüstri Mühendisliği'


def getDepartmentShortName(department):
    return 'BM' if department == 0 else 'EM'


def getDayName(day):
    days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']
    return days[day]


def getStateFromSemesters(schedule):
    sessions = []
    for semester in schedule.semesters:
        for session in semester:
            sessions.append(session)
    return sessions


def importData():
    with open('./data/teachers.json', encoding='utf-8') as json_file:
        teachers_json = json.load(json_file)

    with open('./data/courses.json', encoding='utf-8') as json_file:
        courses_json = json.load(json_file)

    return teachers_json, courses_json


def importFixed():
    with open('./data/fixedSlots.json', encoding='utf-8') as json_file:
        fixedSlots = json.load(json_file)

    return fixedSlots


def getMultiTeacherCourse():
    courses_json = importData()[1]
    return next(
        (course['id'], course['teachers']) for course in courses_json if course.get("hasMultiTeachers", False) == True)
