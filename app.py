from flask import Flask, render_template, request, redirect, url_for, session
import json
import pandas as pd
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load data
with open('data/teachers.json', 'r', encoding='utf-8') as f:
    teachers = json.load(f)["teachers"]

with open('data/students_full.json', 'r', encoding='utf-8') as f:
    full_students = json.load(f)

schedule_df = pd.read_excel('data/class_schedules_download.xlsx', sheet_name=None)


# Helper functions
def get_teacher(email):
    for teacher in teachers:
        if teacher['email'] == email:
            return teacher
    return None


def get_teacher_schedule(subject):
    teacher_schedule = {}
    for class_name, df in schedule_df.items():
        for day in df.columns[1:]:  # Skip the first column which is the time column
            filtered = df[df[day] == subject]
            if not filtered.empty:
                if day not in teacher_schedule:
                    teacher_schedule[day] = []
                for _, row in filtered.iterrows():
                    teacher_schedule[day].append(f'{row[df.columns[0]]} - {class_name}')
    return teacher_schedule


def get_students_for_class(class_name):
    students = full_students.get(class_name, [])
    for student in students:
        if 'id' not in student:
            student['id'] = hashlib.md5((student['name'] + class_name).encode()).hexdigest()
        if 'lessons' not in student:
            student['lessons'] = {}
    return students


def save_students_data():
    with open('data/students_full.json', 'w', encoding='utf-8') as f:
        json.dump(full_students, f, ensure_ascii=False, indent=4)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        teacher = get_teacher(email)
        if teacher and teacher['password'] == password:
            session['user'] = email
            return redirect(url_for('dashboard'))
        return 'Invalid credentials'
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        subject = request.form['subject']
        teachers.append({"email": email, "password": password, "subject": subject})
        with open('data/teachers.json', 'w', encoding='utf-8') as f:
            json.dump({"teachers": teachers}, f)
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        teacher = get_teacher(session['user'])
        if teacher:
            teacher_schedule = get_teacher_schedule(teacher['subject'])
            formatted_schedule_first_shift = format_schedule_for_display(teacher_schedule, shift='first')
            formatted_schedule_second_shift = format_schedule_for_display(teacher_schedule, shift='second')
            return render_template('dashboard.html', schedule_first_shift=formatted_schedule_first_shift,
                                   schedule_second_shift=formatted_schedule_second_shift, subject=teacher['subject'])
    return redirect(url_for('login'))


def format_schedule_for_display(schedule, shift):
    if shift == 'first':
        time_slots = ["08:00-08:45", "09:00-09:45", "10:00-10:45", "11:00-11:45", "12:00-12:45"]
    else:
        time_slots = ["14:00-14:45", "15:00-15:45", "16:00-16:45", "17:00-17:45", "18:00-18:45"]

    formatted_schedule = {day: {time: '' for time in time_slots} for day in
                          ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']}

    for day, classes in schedule.items():
        for class_info in classes:
            time, class_name = class_info.split(' - ')
            if time in time_slots:
                formatted_schedule[day][time] = class_name

    return formatted_schedule


@app.route('/journal/<class_name>', methods=['GET', 'POST'])
def journal(class_name):
    if 'user' in session:
        students = get_students_for_class(class_name)
        if request.method == 'POST':
            lesson_number = request.form['lesson_number']
            for student in students:
                attendance = request.form.get(f"attendance_{student['id']}", 0)
                if attendance == '10':
                    attendance = 10
                else:
                    attendance = 0
                homework = request.form.get(f"homework_{student['id']}", 0)
                criteria1 = request.form.get(f"criteria1_{student['id']}", 0)
                criteria2 = request.form.get(f"criteria2_{student['id']}", 0)
                criteria3 = request.form.get(f"criteria3_{student['id']}", 0)
                criteria4 = request.form.get(f"criteria4_{student['id']}", 0)
                comment = request.form.get(f"comment_{student['id']}", "")
                lesson_data = {
                    "attendance": int(attendance),
                    "homework": int(homework),
                    "criteria1": int(criteria1),
                    "criteria2": int(criteria2),
                    "criteria3": int(criteria3),
                    "criteria4": int(criteria4),
                    "comment": comment
                }
                if 'lessons' not in student:
                    student['lessons'] = {}
                student['lessons'][lesson_number] = lesson_data
            save_students_data()
            return redirect(url_for('journal', class_name=class_name, lesson_number=lesson_number))

        # Передача номера урока и данных о студентах на страницу
        lesson_number = request.args.get('lesson_number', 1)
        return render_template('journal.html', students=students, class_name=class_name,
                               lesson_number=int(lesson_number))
    return redirect(url_for('login'))


@app.route('/quarterly/<class_name>')
def quarterly(class_name):
    students = get_students_for_class(class_name)
    for student in students:
        total_points = 0
        lesson_count = 0
        lesson_data_list = []
        for lesson_number in range(1, 11):
            lesson_data = student.get('lessons', {}).get(str(lesson_number), {})
            attendance = lesson_data.get('attendance', 0)
            homework = lesson_data.get('homework', 0)
            criteria1 = lesson_data.get('criteria1', 0)
            criteria2 = lesson_data.get('criteria2', 0)
            criteria3 = lesson_data.get('criteria3', 0)
            criteria4 = lesson_data.get('criteria4', 0)
            criteria_total = criteria1 + criteria2 + criteria3 + criteria4
            lesson_total = attendance + homework + criteria_total
            lesson_data_list.append({
                "attendance": attendance,
                "homework": homework,
                "criteria1": criteria1,
                "criteria2": criteria2,
                "criteria3": criteria3,
                "criteria4": criteria4,
                "total": lesson_total
            })
            total_points += lesson_total
            if lesson_data:
                lesson_count += 1

        # Calculate final score
        final_score = total_points / (lesson_count if lesson_count > 0 else 1)
        student['final_points'] = final_score
        student['grade'] = calculate_grade(final_score)
        student['lesson_data'] = lesson_data_list

    return render_template('quarterly.html', class_name=class_name, students=students)

def calculate_grade(points):
    if points <= 23:
        return 2
    elif points <= 35:
        return 3
    elif points <= 47:
        return 4
    else:
        return 5


@app.route('/api/students/<class_name>/<lesson_number>')
def api_students(class_name, lesson_number):
    students = get_students_for_class(class_name)
    lesson_number = str(lesson_number)
    data = []
    for student in students:
        lesson_data = student['lessons'].get(lesson_number, {})
        data.append({
            'id': student['id'],
            'name': student['name'],
            'attendance': lesson_data.get('attendance', 0),
            'homework': lesson_data.get('homework', 0),
            'criteria1': lesson_data.get('criteria1', 0),
            'criteria2': lesson_data.get('criteria2', 0),
            'criteria3': lesson_data.get('criteria3', 0),
            'criteria4': lesson_data.get('criteria4', 0),
            'comment': lesson_data.get('comment', '')
        })
    return json.dumps(data, ensure_ascii=False)



@app.route('/student/<student_id>')
def student(student_id):
    if 'user' in session:
        for class_name, students in full_students.items():
            for student in students:
                if student['id'] == student_id:
                    return render_template('student.html', student=student, class_name=class_name)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
