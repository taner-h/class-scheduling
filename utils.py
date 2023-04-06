import json


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


def getSlotsOfFixedSessionsOfSemester(semester, fixedSessions):
    slots = [[], [], [], [], []]
    for fixedSession in fixedSessions:
        slots[fixedSession.day].extend(
            list(range(fixedSession.hour, fixedSession.hour + fixedSession.length)))
    return slots


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


def calculateAvailableSlots():
    fixedSlots = importFixed()
    allSlots = [list(range(9, 18))] * 5
    availableSlots = []
    for i in range(5):
        availableSlots.append(
            [x for x in allSlots[i] if x not in fixedSlots[i]])
    return availableSlots


def getMultiTeacherCourse():
    courses_json = importData()[1]
    return next(
        (course['id'], course['teachers']) for course in courses_json if course.get("hasMultiTeachers", False) == True)
