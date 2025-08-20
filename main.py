from flask import Flask, render_template, request, redirect, flash, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Function to establish MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        user='root', password='bhoomika',
        host='localhost', database='student_db'
    )

# Route to handle GET and POST requests for inserting data
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        usn = request.form['usn']
        name = request.form['name']
        branch = request.form['branch']
        sem = request.form['sem']
        total_marks = request.form['total_marks']

        # Validation
        if len(usn) != 10:
            flash("USN must be of 10 characters", "error")
            return redirect(url_for('index'))
        if not sem.isdigit() or not (1 <= int(sem) <= 8):
            flash("Semester must be a number between 1 and 8", "error")
            return redirect(url_for('index'))
        if not total_marks.isdigit() or int(total_marks) > 1000:
            flash("Total marks must be a number less than or equal to 1000", "error")
            return redirect(url_for('index'))

        # Insert data into MySQL table
        cnx = get_db_connection()
        cursor = cnx.cursor()
        try:
            cursor.execute("INSERT INTO website (usn, name, branch, sem, total_marks) VALUES (%s, %s, %s, %s, %s)",
                           (usn, name, branch, sem, total_marks))
            cnx.commit()
            flash("Student information inserted successfully", "success")
        except mysql.connector.IntegrityError:
            flash("USN already exists", "error")
        finally:
            cursor.close()
            cnx.close()

        return redirect(url_for('index'))

    return render_template('insert.html')

# Route to handle GET and POST requests for displaying data
@app.route("/display", methods=['GET', 'POST'])
def display():
    if request.method == 'POST':
        usn = request.form['usn']

        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM website WHERE usn = %s", (usn,))
        student = cursor.fetchone()
        cursor.close()
        cnx.close()

        if student:
            return render_template('display.html', student=student)
        else:
            flash("USN not available", "error")
            return render_template('display.html')

    return render_template('display.html')

# Route to handle GET and POST requests for updating data
@app.route("/update", methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        usn = request.form['usn']
        field = request.form['field']
        new_value = request.form['new_value']

        # Validation
        if field == "sem":
            if not new_value.isdigit() or not (1 <= int(new_value) <= 8):
                flash("Semester must be a number between 1 and 8", "error")
                return redirect(url_for('update'))
        if field == "usn" and len(new_value) != 10:
            flash("USN must be of 10 characters", "error")
            return redirect(url_for('update'))

        # Update data in MySQL table
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM website WHERE usn = %s", (usn,))
        result = cursor.fetchone()
        if result:
            cursor.execute(f"UPDATE website SET {field} = %s WHERE usn = %s", (new_value, usn))
            cnx.commit()
            flash("Student information updated successfully", "success")
        else:
            flash("USN does not exist", "error")

        cursor.close()
        cnx.close()

        return redirect(url_for('update'))

    return render_template('update.html')


# Route to handle GET and POST requests for deleting data
@app.route("/delete", methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        usn = request.form['usn']

        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM website WHERE usn = %s", (usn,))
        result = cursor.fetchone()
        if result:
            cursor.execute("DELETE FROM website WHERE usn = %s", (usn,))
            cnx.commit()
            flash(f"USN {usn} deleted successfully", "success")
        else:
            flash("USN does not exist", "error")

        cursor.close()
        cnx.close()

        return redirect(url_for('delete'))

    return render_template('delete.html')

if __name__ == "__main__":
    app.run(debug=True)
