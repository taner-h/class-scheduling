import json


# courseIds = [101, 102, 103]

# print([courses[courseId]['name'] for courseId in courseIds])

# bmCourses = {k: v for k, v in courses.items() if v['departmant'] == 'EM'}
# print(bmCourses)

# for k, v in courses.items():
#     print(v['name'])

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


with open('teachers.json', encoding='utf-8') as json_file:
    teachers_json = json.load(json_file)

with open('courses.json', encoding='utf-8') as json_file:
    courses_json = json.load(json_file)


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

for session in sessions:
    session.print()
