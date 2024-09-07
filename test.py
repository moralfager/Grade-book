import pandas as pd
import random

# Список уроков на русском языке
subjects = [
    "Математика", "География", "История", "Наука", "Русский язык",
    "Физическая культура", "Литература", "Информатика", "Иностранный язык",
    "Химия", "Биология", "Обществознание"
]

# Временные слоты для первой и второй смены
time_slots_first_shift = ["08:00-08:45", "09:00-09:45", "10:00-10:45", "11:00-11:45", "12:00-12:45"]
time_slots_second_shift = ["14:00-14:45", "15:00-15:45", "16:00-16:45", "17:00-17:45", "18:00-18:45"]

# Дни недели
days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]

# Чтение существующего файла расписания
file_path = 'data/class_schedules_download.xlsx'
df = pd.read_excel(file_path, sheet_name=None)

# Создаем расписание
schedule = {day: {'Время': time_slots_first_shift + time_slots_second_shift} for day in days_of_week}

# Инициализация расписания для каждого дня
for day in days_of_week:
    for grade in range(8, 12):
        for section in ['A', 'B', 'C']:
            schedule[day][f'{grade}{section}'] = []

# Функция для заполнения расписания с рандомизацией предметов и проверкой на уникальность
def fill_schedule():
    for day in days_of_week:
        # Первая смена (8-9 классы)
        for time_slot in range(5):
            used_subjects = set()
            for grade in range(8, 10):
                for section in ['A', 'B', 'C']:
                    available_subjects = [subject for subject in subjects if subject not in used_subjects]
                    if available_subjects:
                        subject = random.choice(available_subjects)
                        schedule[day][f'{grade}{section}'].append(subject)
                        used_subjects.add(subject)
                    else:
                        schedule[day][f'{grade}{section}'].append("Свободный период")

        # Вторая смена (10-11 классы)
        for time_slot in range(5, 10):
            used_subjects = set()
            for grade in range(10, 12):
                for section in ['A', 'B', 'C']:
                    available_subjects = [subject for subject in subjects if subject not in used_subjects]
                    if available_subjects:
                        subject = random.choice(available_subjects)
                        schedule[day][f'{grade}{section}'].append(subject)
                        used_subjects.add(subject)
                    else:
                        schedule[day][f'{grade}{section}'].append("Свободный период")

# Заполняем расписание
fill_schedule()

# Проверка и заполнение списков до одинаковой длины
max_length = len(time_slots_first_shift + time_slots_second_shift)
for day in days_of_week:
    for key in schedule[day]:
        while len(schedule[day][key]) < max_length:
            schedule[day][key].append("Свободный период")

# Создаем DataFrame и записываем в Excel
with pd.ExcelWriter('data/schedule.xlsx') as writer:
    for day in days_of_week:
        df = pd.DataFrame(schedule[day])
        df.to_excel(writer, sheet_name=day, index=False)

print("Schedule created successfully and saved to data/schedule.xlsx")
