from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# SQLite database file
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Database model for Student
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, default=0.0)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Student {self.name}>'


# Create database tables
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    students = Student.query.order_by(Student.roll_number).all()  # READ
    total_students = Student.query.count()
    avg_cgpa = db.session.query(db.func.avg(Student.cgpa)).scalar() or 0
    return render_template('dashboard.html',
                           students=students,
                           total_students=total_students,
                           avg_cgpa=round(avg_cgpa, 2))


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        try:
            new_student = Student(
                roll_number=request.form['roll_number'],
                name=request.form['name'],
                email=request.form['email'],
                phone=request.form['phone'],
                department=request.form['department'],
                year=int(request.form['year']),
                cgpa=float(request.form['cgpa'])
            )  # CREATE
            db.session.add(new_student)
            db.session.commit()
            flash(f'Student {new_student.name} added successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            db.session.rollback()

    return render_template('create.html')


@app.route('/view/<int:id>')
def view(id):
    student = Student.query.get_or_404(id)
    return render_template('view.html', student=student)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        try:
            student.roll_number = request.form['roll_number']
            student.name = request.form['name']
            student.email = request.form['email']
            student.phone = request.form['phone']
            student.department = request.form['department']
            student.year = int(request.form['year'])
            student.cgpa = float(request.form['cgpa'])  # UPDATE
            db.session.commit()
            flash(f'Student {student.name} updated successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            db.session.rollback()

    return render_template('edit.html', student=student)


@app.route('/delete/<int:id>')
def delete(id):
    student = Student.query.get_or_404(id)
    name = student.name
    db.session.delete(student)  # DELETE
    db.session.commit()
    flash(f'Student {name} deleted successfully!', 'success')
    return redirect(url_for('home'))


@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        students = Student.query.filter(
            (Student.name.contains(query)) |
            (Student.roll_number.contains(query)) |
            (Student.department.contains(query))
        ).all()
    else:
        students = []
    return render_template('search.html', students=students, query=query)


if __name__ == '__main__':
    app.run(debug=True)