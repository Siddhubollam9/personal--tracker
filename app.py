from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database setup
def get_db_connection():
    conn = sqlite3.connect('progress.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
def init_db():
    conn = get_db_connection()
    conn.execute('DROP TABLE IF EXISTS tasks')  # Drop the table if it exists
    conn.execute('''
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            deadline DATETIME,
            priority TEXT NOT NULL DEFAULT 'Medium'
        )
    ''')
    conn.commit()
    conn.close()

# Homepage - Display all tasks
@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

# Add a new task
@app.route('/add', methods=['POST'])
def add_task():
    task = request.form['task']
    deadline = request.form['deadline']
    priority = request.form['priority']
    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (task, deadline, priority) VALUES (?, ?, ?)', (task, deadline, priority))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Edit a task
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    conn = get_db_connection()
    if request.method == 'POST':
        task = request.form['task']
        deadline = request.form['deadline']
        priority = request.form['priority']
        conn.execute('UPDATE tasks SET task = ?, deadline = ?, priority = ? WHERE id = ?', (task, deadline, priority, task_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        conn.close()
        return render_template('edit.html', task=task)

# Mark a task as complete
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Delete a task
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Track progress
@app.route('/progress')
def progress():
    conn = get_db_connection()
    total_tasks = conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
    completed_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE completed = 1').fetchone()[0]
    conn.close()
    progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    return render_template('progress.html', progress=progress_percentage)

if __name__ == '__main__':
    init_db()
    app.run(debug=False)