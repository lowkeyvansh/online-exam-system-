from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///onlineexam.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    exams = db.relationship('Exam', backref='user', lazy=True)

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    questions = db.relationship('Question', backref='exam', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    option_d = db.Column(db.String(100), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)

db.create_all()

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    exams = Exam.query.all() if user.is_admin else Exam.query.filter_by(user_id=user_id).all()
    return render_template('index.html', exams=exams, is_admin=user.is_admin)

@app.route('/exam/<int:exam_id>')
def take_exam(exam_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    exam = Exam.query.get_or_404(exam_id)
    return render_template('take_exam.html', exam=exam)

@app.route('/submit_exam/<int:exam_id>', methods=['POST'])
def submit_exam(exam_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    exam = Exam.query.get_or_404(exam_id)
    user_answers = request.form.to_dict()
    score = 0
    for question in exam.questions:
        if user_answers.get(str(question.id)) == question.correct_option:
            score += 1
    flash(f'You scored {score}/{len(exam.questions)}', 'success')
    return redirect(url_for('home'))

@app.route('/add_exam', methods=['GET', 'POST'])
def add_exam():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        user_id = session['user_id']
        new_exam = Exam(title=title, user_id=user_id)
        db.session.add(new_exam)
        db.session.commit()
        flash('Exam created successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_exam.html')

@app.route('/add_question/<int:exam_id>', methods=['GET', 'POST'])
def add_question(exam_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        question_text = request.form['question_text']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_option = request.form['correct_option']
        new_question = Question(
            question_text=question_text, option_a=option_a, option_b=option_b, 
            option_c=option_c, option_d=option_d, correct_option=correct_option, exam_id=exam_id
        )
        db.session.add(new_question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_question.html', exam_id=exam_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
