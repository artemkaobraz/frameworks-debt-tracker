students_debts = {
    "Иванов": ["Математика", "Физика"],
    "Петрова": ["История"],
    "Сидоров": ["Математика", "Физика", "Информатика"]
}


def count_debts(name):
    if name not in students_debts:
        return 0
    return len(students_debts[name])


def has_more_than(name, num):
    return count_debts(name) > num


def get_students_with_debts_more_than(num):
    return [name for name in students_debts.keys() if has_more_than(name, num)]


def get_worst_student():
    return max(students_debts.keys(), key=lambda name: count_debts(name))


def add_debt(name, discipline):
    if name not in students_debts:
        students_debts[name] = []
    students_debts[name].append(discipline)


def close_debt(name, discipline):
    if name in students_debts and discipline in students_debts[name]:
        students_debts[name].remove(discipline)
        return True
    return False


print(get_students_with_debts_more_than(1))
print(count_debts("Иванов"))
print(get_worst_student())
print(close_debt("Иванов", "Физика"))
print(students_debts["Иванов"])