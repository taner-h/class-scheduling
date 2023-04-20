from utils import *
from collections import Counter
import copy
import random


class Course:
    def __init__(self, id, name, code, department, year, cannotCollideWith):
        self.id = id
        self.name = name
        self.code = code
        self.department = department
        self.year = year
        self.cannotCollideWith = cannotCollideWith

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
    def __init__(self, id, course, teacher, length, isLab=False, suffix=None, isFixed=False, day=None, hour=None):
        self.id = id
        self.course = course
        self.teacher = teacher
        self.length = length

        self.isFixed = isFixed
        self.isLab = isLab
        self.suffix = suffix
        self.name = self.course.name if not self.isLab else self.course.name + ' - ' + self.suffix

        self.day = day
        self.hour = hour

    def print(self):
        print(
            f"{self.id}: {self.name} ({self.length}), {self.teacher.firstName} {self.teacher.lastName}")

    def printSchedule(self):
        print(f"{self.id}: {self.name}, {getDayName(self.day)} {self.hour}.00 - {self.hour + self.length}.00 ({getSemesterShortName((4 * self.course.department + self.course.year) - 1)})")


class Schedule:
    def __init__(self, state):
        self.state = createState(state)

        self.semesters = self.filterSemesters()
        self.teacherSessions = self.filterByTeachers()

        self.semesterCollisions = self.calculateSemesterCollisions()
        self.teacherCollisions = self.calculateTeacherCollisions()
        self.multiTeacherCollisions = self.calculateMultiTeacherSessionCollisions()
        self.teacherAvailabilityViolations = self.calculateTeacherAvailabilityViolations()
        self.cannotCollideViolations = self.calculateCannotCollideViolations()

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
        self.emptySlots = results[9]
        self.allSlotsUsedDays = self.calculateAllSlotsUsedDays()

        isFeasible, fitness = self.calculateFitness()
        self.fitness = fitness
        self.isFeasible = isFeasible
        self.hasAllSessions = self.calculateHasAllSessions()

    def filterSemesters(self):
        semesters = []
        for department in range(2):
            for year in range(1, 5):
                # semester = list(filter(lambda session: session.course.department ==
                #                        department and session.course.year == year, self.state))
                semester = [session for session in self.state if session.course.department ==
                            department and session.course.year == year]
                semesters.append(semester)

        return semesters

    def filterByTeachers(self):
        filtered = []
        for teacher in teachers:
            # teacherSessions = list(
            #     filter(lambda session: session.teacher.id == teacher.id, self.state))
            teacherSessions = [
                session for session in self.state if session.teacher.id == teacher.id]
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
                if day in languageSlots[0]:
                    print(
                        f'{languageSlots[1][0]}.00 - {languageSlots[1][1] + 1}.00 - Yabancı Dil')

    def printTeacherSessions(self):
        for sessionsOfTeacher in self.teacherSessions:
            if sessionsOfTeacher[0].teacher.firstName != "":
                print(
                    f'\n\n----- {sessionsOfTeacher[0].teacher.firstName} {sessionsOfTeacher[0].teacher.lastName} -----\n')
                if sessionsOfTeacher[0].teacher.id in multiTeachers:
                    multiTeacherSession = [
                        session for session in self.state if session.course.id == multiTeacherCourseId][0]
                    sessionsOfTeacher.append(multiTeacherSession)
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
            f'\n----- Donem Cakismalari ({len(self.semesterCollisions) + len(self.languageSessionViolations)}) -----\n')
        for collision in self.semesterCollisions:
            for session in collision:
                print(
                    f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name}')
            print()

        for index, day in self.languageSessionViolations:
            print(
                f'{getDayName(day)}: {languageSlots[1][0]}.00 - {languageSlots[1][1] + 1}.00 - Yabancı Dil ({index})')

    def printTeacherCollisions(self):
        print(
            f'\n----- Ogretmen Cakismalari ({len(self.teacherCollisions) + len(self.multiTeacherCollisions)}) -----\n')

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
            f'\n----- Öğle Arası İhlalleri ({len(self.fridayBreakViolations) + len(self.breakHourViolations) + len(self.departmentMeetingViolations)}) -----\n')
        for index, day in self.breakHourViolations:
            print(f'Öğle Arası İhlali: {index}, {getDayName(day)}')

        for index in self.fridayBreakViolations:
            print(f'Cuma Arası İhlali: {index}')

        for index in self.departmentMeetingViolations:
            print(f'Bölüm Toplantısı İhlali: {index}')

    def printFreeDays(self):
        print(f'\n----- Boş Günler ({len(self.freeDays)}) -----\n')
        for semester, day in self.freeDays:
            print(
                f'{getSemesterShortName(semester)}, {getDayName(day)}')

    def printAllSlotsUsedDays(self):
        print(
            f'\n----- Tüm Slotları Kullanılan Günler ({len(self.allSlotsUsedDays)}) -----\n')
        for semester, day in self.allSlotsUsedDays:
            print(
                f'{getSemesterShortName(semester)}, {getDayName(day)}')

    def printSingleSessionDays(self):
        print(
            f'\n----- Tek Seanslı Günler ({len(self.singleSessionDays)}) -----\n')
        for semester, day in self.singleSessionDays:
            print(
                f'{getSemesterShortName(semester)}, {getDayName(day)}')

    def printMultipleCourseSessions(self):
        print(
            f'\n----- Günde Birden Fazla Seanslı Dersler ({len(self.multipleCourseSessions)}) -----\n')
        for course in self.multipleCourseSessions:
            for session in course:
                print(
                    f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name} ({getSemesterShortName((4 * session.course.department + session.course.year) - 1)})')
            print()

    def printCannotCollideViolations(self):
        print(
            f'\n----- Çakışmaması Gereken Seans Çakışmaları ({len(self.cannotCollideViolations)}) -----\n')

        for collision in self.cannotCollideViolations:
            for session in collision:
                print(
                    f'{session.hour}.00 - {session.hour + session.length}.00 - {session.name}')
            print()

    def printSlotSpan(self):
        print(
            f'\n----- Toplam Slot Açıklığı ({sum([sum(semesterSlotSpan) for semesterSlotSpan in self.slotSpan])})-----\n')

    def printEmptySlots(self):
        print(
            f'\n----- Boş Bırakılan Ara Slotlar ({len(self.emptySlots)}) -----\n')

        for emptySlot in self.emptySlots:
            print(
                f'{getSemesterShortName(emptySlot[0])}, {getDayName(emptySlot[1])}, {emptySlot[2]}')
        print()

    def printHardConstraintViolations(self):
        print('\n\n---------- HARD CONSTRAINT VIOLATIONS ----------')
        self.printSemesterCollisions()
        self.printTeacherCollisions()
        self.printBreakHourViolations()
        self.printAllSlotsUsedDays()

    def printSoftContraints(self):
        print('\n\n---------- SOFT CONSTRAINT VIOLATIONS ----------')
        self.printAvailabilityCollisions()
        self.printFreeDays()
        self.printSingleSessionDays()
        self.printMultipleCourseSessions()
        self.printCannotCollideViolations()
        self.printSlotSpan()
        self.printEmptySlots()

    def printInfo(self):
        self.print()
        self.printTeacherSessions()
        self.printAvailableSlots()
        self.printHardConstraintViolations()
        self.printSoftContraints()
        self.printFitness()

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

    def printFitness(self):
        print(
            f'fitness: {round(self.fitness, 2)} (isFeasible: {self.isFeasible})')

    def calculateSemesterCollisions(self):
        collisions = []
        for semester in self.semesters:
            for day in range(5):
                # sessionsOfDay = list(filter(
                #     lambda session: session.day == day, semester))
                sessionsOfDay = [
                    session for session in semester if session.day == day]
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
                        # collisionSession = list(filter(
                        #     lambda session: session.id == sessionIds[index], sessionsOfDay))[0]
                        collisionSession = [
                            session for session in sessionsOfDay if session.id == sessionIds[index]][0]
                        collisionSessions.append(collisionSession)
                    collisions.append(collisionSessions)
        return collisions

    def calculateTeacherCollisions(self):
        collisions = []
        for sessionsOfTeacher in self.teacherSessions:
            for day in range(5):
                # sessionsOfDay = list(filter(
                #     lambda session: session.day == day, sessionsOfTeacher))
                sessionsOfDay = [
                    session for session in sessionsOfTeacher if session.day == day]
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
                        # collisionSession = list(filter(
                        #     lambda session: session.id == sessionIds[index], sessionsOfDay))[0]
                        collisionSession = [
                            session for session in sessionsOfDay if session.id == sessionIds[index]][0]
                        collisionSessions.append(collisionSession)
                    collisions.append(collisionSessions)
        return collisions

    def calculateMultiTeacherSessionCollisions(self):
        collisions = []

        for teacherId in multiTeachers:
            # sessionsOfTeacher = list(
            #     filter(lambda session: session.teacher.id == teacherId, self.state))
            sessionsOfTeacher = [
                session for session in self.state if session.teacher.id == teacherId]
            multiTeacherSession = [
                session for session in self.state if session.course.id == multiTeacherCourseId][0]
            sessionsOfTeacher.append(multiTeacherSession)

            for day in range(5):
                # sessionsOfDay = list(filter(
                #     lambda session: session.day == day, sessionsOfTeacher))
                sessionsOfDay = [
                    session for session in sessionsOfTeacher if session.day == day]
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
                        # collisionSession = list(filter(
                        #     lambda session: session.id == sessionIds[index], sessionsOfDay))[0]
                        collisionSession = [
                            session for session in sessionsOfDay if session.id == sessionIds[index]][0]
                        collisionSessions.append(collisionSession)
                    collisions.append(collisionSessions)

        return collisions

    def calculateTeacherAvailabilityViolations(self):
        collisions = []
        for sessionsOfTeacher in self.teacherSessions:
            teacher = sessionsOfTeacher[0].teacher
            for day in range(5):
                # sessionsOfDay = list(filter(
                #     lambda session: session.day == day, sessionsOfTeacher))
                sessionsOfDay = [
                    session for session in sessionsOfTeacher if session.day == day]
                usedSlots = []
                sessionIds = []
                unavailableSlotsOfDay = teacher.unavailable[day]

                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))
                    sessionIds.extend([session.id] * session.length)

                collisionSlots = [
                    slot for slot in usedSlots if slot in unavailableSlotsOfDay]

                for collisionSlot in collisionSlots:
                    indices = [index for index, slot in enumerate(
                        usedSlots) if slot == collisionSlot]
                    collisionSessions = []
                    for index in indices:
                        # collisionSession = list(filter(
                        #     lambda session: session.id == sessionIds[index], sessionsOfDay))[0]
                        collisionSession = [
                            session for session in sessionsOfDay if session.id == sessionIds[index]][0]
                        collisionSessions.append(collisionSession)
                    collisions.append(collisionSessions)
        return collisions

    def calculateCannotCollideViolations(self):
        violations = []
        for session in self.state:
            sessionSlots = list(
                range(session.hour, session.hour + session.length))
            sessionsToNotCollide = [
                s for s in self.state if s.course.id in session.course.cannotCollideWith]
            for sessionToNotCollide in sessionsToNotCollide:
                if session.day == sessionToNotCollide.day:
                    sessionToNotCollideSlots = list(range(
                        sessionToNotCollide.hour, sessionToNotCollide.hour + sessionToNotCollide.length))
                    sessionToNotCollideSlots.extend(sessionSlots)
                    collisionSlots = [
                        item for item, count in Counter(sessionToNotCollideSlots).items() if count > 1]
                    if collisionSlots and (sessionToNotCollide, session) not in violations:
                        violations.append((session, sessionToNotCollide))

        return violations

    def calculateHasAllSessions(self):
        return len(self.state) == 87

    def calculateAllSlotsUsedDays(self):
        allSlotsUsedDays = []
        for semesterIndex, semester in enumerate(self.availableSlots):
            for index, day in enumerate(semester):
                if not day and index in [0, 1, 3]:
                    allSlotsUsedDays.append((semesterIndex, index))
        return allSlotsUsedDays

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
        allEmptySlots = []

        for index, semester in enumerate(self.semesters):
            semesterSlotSpan = []
            semesterAvailableSlots = copy.deepcopy(initialAvailableSlots)
            for day in range(5):

                sessionsOfDay = [
                    session for session in semester if session.day == day]
                usedSlots = []
                for session in sessionsOfDay:
                    usedSlots.extend(
                        list(range(session.hour, session.hour + session.length)))

                semesterAvailableSlots[day] = [
                    slot for slot in semesterAvailableSlots[day] if slot not in usedSlots]

                # Check for break violations:
                if day in [0, 1, 3] and (12 in usedSlots and 13 in usedSlots):
                    breakViolations.append((index, day))

                # Check for free days
                if len(usedSlots) == 0 and day not in languageSlots[0]:
                    freeDays.append((index, day))

                # Check for friday violations
                if day == 4 and (12 in usedSlots or 13 in usedSlots):
                    fridayViolations.append(index)

                # Check for meeting violations
                if day == 2 and 13 in usedSlots:
                    meetingViolations.append(index)

                # Check for language session violations
                if day in languageSlots[0] and (languageSlots[1][0] in usedSlots or languageSlots[1][1] in usedSlots):
                    languageSessionViolations.append((index, day))

                # Check for single-session days
                if len(sessionsOfDay) == 1 and day in [0, 3, 4]:
                    singleSessionDays.append([index, day])
                elif len(sessionsOfDay) == 0 and day in languageSlots[0]:
                    singleSessionDays.append([index, day])

                # Check for multiple sessions of same course in the same day
                courseIds = [session.course.id for session in sessionsOfDay]
                multipleSessionCourseIds = [
                    item for item, count in Counter(courseIds).items() if count > 1]
                for multipleSessionCourseId in multipleSessionCourseIds:
                    # sessionsOfCourse = list(filter(
                    #     lambda session: session.course.id == multipleSessionCourseId, sessionsOfDay))
                    sessionsOfCourse = [
                        session for session in sessionsOfDay if session.course.id == multipleSessionCourseId]
                    multipleSessions.append(sessionsOfCourse)

                # Calculate the slot span
                if day in languageSlots[0]:
                    usedSlots.extend(languageSlots[1])

                if len(usedSlots) != 0:
                    earliestSlot = min(usedSlots)
                    latestSlot = max(usedSlots)
                    slotSpan = latestSlot - earliestSlot + 1
                    semesterSlotSpan.append(slotSpan)
                else:
                    semesterSlotSpan.append(0)

                # Calculate empty slots
                if not usedSlots:
                    continue

                usedSlots.sort()
                dayRange = list(range(usedSlots[0], usedSlots[-1] + 1))
                dayRange = [
                    slot for slot in dayRange if slot in semesterAvailableSlots[day]]

                emptySlots = len(dayRange)

                if 12 in dayRange or 13 in dayRange:
                    emptySlots -= 1

                if emptySlots:
                    if 12 in dayRange and 13 in dayRange:
                        # n = random.choice([12, 13])
                        dayRange = [slot for slot in dayRange if slot != 13]
                        for emptySlot in dayRange:
                            allEmptySlots.append([index, day, emptySlot])
                    elif 12 in dayRange:
                        for emptySlot in dayRange:
                            if emptySlot == 12:
                                continue
                            allEmptySlots.append([index, day, emptySlot])
                    elif 13 in dayRange:
                        for emptySlot in dayRange:
                            if emptySlot == 13:
                                continue
                            allEmptySlots.append([index, day, emptySlot])
                    else:
                        for emptySlot in dayRange:
                            allEmptySlots.append([index, day, emptySlot])

            totalSlotSpan.append(semesterSlotSpan)
            allAvailableSlots.append(semesterAvailableSlots)

        violations = [breakViolations, meetingViolations, fridayViolations, languageSessionViolations,
                      freeDays, singleSessionDays, multipleSessions, totalSlotSpan, allAvailableSlots, allEmptySlots]

        return violations

    # def calculateAvailableSlots():
    #     allAvailableSlots = []
    #     for semester in self.semesters:
    #         for day in range(5):

    #             sessionsOfDay = [
    #                 session for session in semester if session.day == day]
    #             usedSlots = []
    #             allSlots = [list(range(9, 18))] * 5
    #             for session in sessionsOfDay:
    #                 usedSlots.extend(
    #                     list(range(session.hour, session.hour + session.length)))

    def calculateFitness(self):
        # ! Hard Constraints
        semesterCollisionCount = len(self.semesterCollisions)
        languageSessionViolationCount = len(self.languageSessionViolations)
        teacherCollisionCount = len(self.teacherCollisions)
        multiTeacherCollisionCount = len(self.multiTeacherCollisions)
        breakHourViolationCount = len(self.breakHourViolations)
        fridayBreakViolationCount = len(self.fridayBreakViolations)
        departmentMeetingViolationCount = len(self.departmentMeetingViolations)
        allSlotsUsedDaysCount = len(self.allSlotsUsedDays)

        # ? Soft Constraints
        teacherAvailabilityViolationCount = len(
            self.teacherAvailabilityViolations)
        freeDayCount = len(self.freeDays)
        singleSessionDayCount = len(self.singleSessionDays)
        multipleCourseSessionCount = len(self.multipleCourseSessions)
        cannotCollideViolationCount = len(self.cannotCollideViolations)
        slotSpan = sum([sum(semesterSlotSpan)
                       for semesterSlotSpan in self.slotSpan])
        emptySlotCount = len(self.emptySlots)

        score = 50.0
        isFeasible = False

        score -= 2 * (semesterCollisionCount + teacherCollisionCount +
                      multiTeacherCollisionCount + languageSessionViolationCount)
        score -= 3 * (fridayBreakViolationCount +
                      breakHourViolationCount + departmentMeetingViolationCount)
        score -= 3 * allSlotsUsedDaysCount

        hardConstraintsTotal = semesterCollisionCount + teacherCollisionCount + multiTeacherCollisionCount + fridayBreakViolationCount + \
            breakHourViolationCount + departmentMeetingViolationCount + \
            languageSessionViolationCount + allSlotsUsedDaysCount

        score -= 0.5 * cannotCollideViolationCount
        score -= 0.4 * singleSessionDayCount
        score -= 0.3 * teacherAvailabilityViolationCount
        score -= 0.2 * multipleCourseSessionCount
        # Total session slots (211) + Total break slots (48) + Language session length (32)
        score -= 0.25 * (slotSpan - (291 - freeDayCount))
        score -= 0.15 * (emptySlotCount - 5)
        score += 1 * freeDayCount

        if (hardConstraintsTotal):
            score -= 0.1 * score
            isFeasible = False
        else:
            score += 0.2 * score
            isFeasible = True

        return isFeasible, score


def duplicateSession(session):
    return Session(session.id, session.course, session.teacher, session.length,
                   isLab=session.isLab, suffix=session.suffix, isFixed=session.isFixed,
                   day=session.day, hour=session.hour)


def createState(state):
    return [duplicateSession(session) for session in state]


def generateObjects():
    teachers_json, courses_json = importData()

    teachers = []
    for teacher in teachers_json:
        teachers.append(Teacher(
            teacher['id'], teacher['firstName'], teacher['lastName'], teacher['unavailable']))

    courses = []
    for course in courses_json:
        courses.append(Course(course['id'], course['name'],
                              course['code'], course['department'], course['year'], course['cannotCollideWith']))

    sessions = []
    index = 0
    for course in courses_json:
        for session in course['sessions']:
            sessions.append(
                Session(index, courses[course['id']], teachers[session['teacherId']],
                        session['length'], isLab=session.get("isLab", False), suffix=session.get("suffix", None), isFixed=session.get("isFixed", False), day=session.get("day", None), hour=session.get("hour", None)))
            index += 1

    return teachers, courses, sessions


teachers_json, courses_json = importData()
multiTeacherCourseId, multiTeachers = getMultiTeacherCourse()
teachers, courses, sessions = generateObjects()
