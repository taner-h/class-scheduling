import json

with open('teachers.json') as json_file:
    teachers = json.load(json_file)

for teacher in teachers:
    print(teacher)

# courseIds = [101, 102, 103]

# print([courses[courseId]['name'] for courseId in courseIds])

# bmCourses = {k: v for k, v in courses.items() if v['departmant'] == 'EM'}
# print(bmCourses)

# for k, v in courses.items():
#     print(v['name'])
