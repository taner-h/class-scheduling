import json


# courseIds = [101, 102, 103]

# print([courses[courseId]['name'] for courseId in courseIds])

# bmCourses = {k: v for k, v in courses.items() if v['departmant'] == 'EM'}
# print(bmCourses)

# for k, v in courses.items():
#     print(v['name'])

class Course:
    def __init__(self, name, code, department, year):
        self.name = name
        self.code = code
        self.department = department
        self.year = year


class Teacher:
    def __init__(self, id, firstName, lastName, unavailable):
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.unavailable = unavailable


class Session:
    def __init__(self, course, teacher,):
        self.course = course
        self.teacher = teacher

        self.day = null
        self.hour = null
        self.length = null


class Schedule:
    def __init__(self, state):
        self.state = state

        self.f = null
        self.isValid = null


def printTeacher(teacher):
    print(f"{teacher.id}: {teacher.firstName} {teacher.lastName}")


with open('teachers.json', encoding='utf-8') as json_file:
    teachers_json = json.load(json_file)


teachers = []
for index, teacher in enumerate(teachers_json):
    teachers.append(Teacher(
        index, teacher['firstName'], teacher['lastName'], teacher['unavailable']))
