# School Journal System

## Overview

This project is a **School Journal System** built using the Flask web framework. It allows teachers to manage student attendance, homework, and other performance metrics, such as criteria-based evaluations. The system also provides a dashboard for teachers to view their weekly schedules.

## Features

- **Login and Registration System**: Teachers can log in or register with their email, password, and subject they teach.
- **Dashboard**: After logging in, teachers can view their personal teaching schedule, divided into two shifts (morning and afternoon).
- **Journal Management**: Teachers can access a journal for each class where they can:
  - Mark student attendance.
  - Input homework grades.
  - Assign points for various evaluation criteria (e.g., understanding concepts, active participation).
  - Leave comments for each student.
- **Quarterly Summary**: Teachers can calculate the total points for each student based on their lesson performance across multiple lessons.
- **API Endpoints**: JSON-based API to retrieve student data for specific lessons.
- **Student Profile View**: Teachers can view individual student profiles to check their detailed performance.

## How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/school-journal-system.git
cd school-journal-system

### 2. Running the Application
Start the Flask development server with the following command:

```bash
python app.py

Once the server is running, you can access the application by visiting:

http://127.0.0.1:5000/
