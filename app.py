from flask import Flask, flash,render_template,request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from flask_cors import CORS
from dotenv import load_dotenv # Import load_dotenv

# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS # Required for cross-origin requests if frontend is separate
import requests # <--- IMPORTANT: This line ensures the 'requests' library is available.
import os
import json # Import json module for parsing structured responses

matplotlib.use('Agg')
from werkzeug.security import generate_password_hash,check_password_hash
def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY']='vm123'
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///quizinfo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    app.config['PASSWORD_HASH']='vm123'
    app.config['Chart_IMAGE']=os.path.join('static','charts')
    os.makedirs(app.config['Chart_IMAGE'],exist_ok=True)
    db.init_app(app)
    return app



#database 
db=SQLAlchemy()
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(150),nullable=False,unique=True)
    password=db.Column(db.String(150),nullable=False)
    full_name=db.Column(db.String(150),nullable=False)
    qualification=db.Column(db.String(150),nullable=False)
    dob=db.Column(db.Date,nullable=False)
    gender = db.Column(db.String(50), nullable=False)  # New field for gender
    email = db.Column(db.String(150), nullable=False, unique=True)  # New field for email
    phone = db.Column(db.String(15), nullable=False)  # New field for phone number
    address = db.Column(db.String(255), nullable=False)  # New field for address
    status=db.Column(db.String(50),default='Active')
    created_on=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    
    scores=db.relationship('Scores',back_populates='user',cascade='all,delete')

class Subject(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(150),nullable=False)
    description=db.Column(db.Text,nullable=False)
    code=db.Column(db.String(150),nullable=False)
    chapters=db.relationship('Chapter',back_populates='subject',cascade='all,delete')

class Chapter(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(150),nullable=False)
    description=db.Column(db.Text,nullable=False)
    subject_id=db.Column(db.Integer,db.ForeignKey('subject.id'),nullable=False)
    
    subject=db.relationship('Subject',back_populates='chapters')
    quizzes=db.relationship('Quiz',back_populates='chapter',cascade='all,delete')

class Question(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(150),nullable=False)
    question_statement=db.Column(db.Text,nullable=False)
    option1=db.Column(db.String(150),nullable=False)
    option2=db.Column(db.String(150),nullable=False)
    option3=db.Column(db.String(150),nullable=False)
    option4=db.Column(db.String(150),nullable=False)
    answer=db.Column(db.String(150),nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)
    
    quiz=db.relationship('Quiz',back_populates='questions')
    
class Quiz(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(150),nullable=False)
    date_of_quiz=db.Column(db.Date,nullable=False)
    time_of_quiz=db.Column(db.Integer,nullable=False)
    remarks=db.Column(db.Text,nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)   
    questions = db.relationship('Question', back_populates='quiz', cascade="all, delete")
    scores = db.relationship('Scores', back_populates='quiz', cascade="all, delete")
    chapter=db.relationship('Chapter',back_populates='quizzes')

class Scores(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    time_taken=db.Column(db.Time,nullable=False)
    total_score=db.Column(db.Integer,nullable=False)   
    user=db.relationship('User',back_populates='scores')
    quiz=db.relationship('Quiz',back_populates='scores')
    
def create_admin():
    admin=User.query.filter_by(username='admin').first()
    if admin is None:
        admin=User(username='admin',password=generate_password_hash(app.config['PASSWORD_HASH']),full_name='admin',qualification='admin',gender='admin',email='admin',phone='admin',address='admin',dob=datetime.strptime('01-01-2000','%d-%m-%Y').date())
        db.session.add(admin)
        db.session.commit()   
         
app=create_app()
app.app_context().push()        
with app.app_context():
    db.create_all()
    create_admin()
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method =='POST':
        username=request.form['username']
        password=request.form['password']
        print(username,password)
        # if username=='admin' and password=='admin':
        user=User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):
            if user.username=='admin':
                session['username']='admin'
                return redirect(url_for('admin_dashboard'))
            if user.status=='Inactive':
                flash('Your account is blocked','danger')
                return redirect(url_for('login'))
            session['username']=user.username
            session['user_id']=user.id    
            return redirect(url_for('user_dashboard'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/admin_dashboard',methods=['GET','POST'])
def admin_dashboard():
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')
# 01:05hrs
@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if session.get('username') is None:
        return redirect(url_for('login'))
    user_id = session['user_id']
    quizzes = Quiz.query.all()
    
    scores = Scores.query.filter_by(user_id=user_id).all()
    scores_dict = {score.quiz_id: score.total_score for score in scores}
    return render_template('user_dashboard.html', quizes=quizzes, scores=scores_dict)

@app.route('/manage_users',methods=['GET','POST'])
def manage_users():
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    users=User.query.filter(User.username!='admin').all()
    return render_template('manage_user.html',users=users)
@app.route('/search_user', methods=['GET'])
def search_user():
    query_username = request.args.get('user_username', '').strip()
    query_full_name = request.args.get('user_full_name', '').strip()
    query_status = request.args.get('user_status', '').strip()

    users_query = User.query.filter(User.username != 'admin')  # Exclude admin users
    
    if query_username:
        users_query = users_query.filter(User.username.contains(query_username))
    if query_full_name:
        users_query = users_query.filter(User.full_name.contains(query_full_name))
    if query_status:
        users_query = users_query.filter(User.status.contains(query_status))
    
    users = users_query.all()

    return render_template('manage_user.html', users=users)

@app.route('/block_user/<int:user_id>', methods=['GET', 'POST'])
def block_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('manage_users'))
    
    if user.status != "Inactive":  # Assuming status is a string field
        user.status = "Inactive"
        db.session.commit()
        flash('User has been blocked successfully!', 'success')
        return redirect(url_for('manage_users'))
    
    return redirect(url_for('manage_users'))

@app.route('/unblock_user/<int:user_id>', methods=['GET', 'POST'])
def unblock_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('manage_users'))
    
    if user.status != "Active":  # Assuming status is a string field
        user.status = "Active"
        db.session.commit()
        flash('User has been unblocked successfully!', 'success')
        return redirect(url_for('manage_users'))
    
    return redirect(url_for('manage_users'))
# signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob = request.form['dob']
        gender = request.form['gender']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        # Check if email or username already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please use a different email.", "danger")
            return redirect(url_for('signup'))

        if User.query.filter_by(username=username).first():
            flash("Username already taken. Please choose a different username.", "danger")
            return redirect(url_for('signup'))

        # If no duplicates, create and insert the user
        user = User(
            username=username,
            password=generate_password_hash(password),
            full_name=full_name,
            qualification=qualification,
            dob=datetime.strptime(dob, '%Y-%m-%d').date(),
            gender=gender,
            email=email,
            phone=phone,
            address=address
        )

        db.session.add(user)
        db.session.commit()
        flash("Signup successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/subjects_management',methods=['GET','POST'])
def subjects_management():
    subjects=Subject.query.all()
    print(subjects)  # This will log the subjects in the Flask console

    return render_template('subject.html',subjects=subjects)
@app.route('/add_subject',methods=['GET','POST'])
def add_subject():
    if request.method=='POST':
        name=request.form['name']
        description=request.form['description']
        code=request.form['code']
        subject=Subject(name=name,description=description,code=code)
        db.session.add(subject)
        db.session.commit()
        return redirect(url_for('subjects_management'))
    return render_template('subject.html')
@app.route('/edit_subject/<int:subject_id>',methods=['GET','POST'])
def edit_subject(subject_id):
    subject=Subject.query.get(subject_id)
    if request.method=='POST':
        subject.name=request.form['name']
        subject.description=request.form['description']
        subject.code=request.form['code']
        db.session.commit()
        return redirect(url_for('subjects_management'))
    return render_template('subject.html',subject=subject)

@app.route('/delete_subject/<int:subject_id>',methods=['GET','POST'])
def delete_subject(subject_id):
    subject=Subject.query.get(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('subjects_management'))      
@app.route('/search_subject', methods=['GET'])
def search_subject():
    query_name = request.args.get('subject_name', '').strip()
    query_code = request.args.get('subject_code', '').strip()

    subjects_query = Subject.query  # Start with the base query
    
    if query_name:
        subjects_query = subjects_query.filter(Subject.name.contains(query_name))
    if query_code:
        subjects_query = subjects_query.filter(Subject.code.contains(query_code))
    
    subjects = subjects_query.all()

    return render_template('subject.html', subjects=subjects)

@app.route('/add_chapter/<int:subject_id>', methods=['GET', 'POST'])
def add_chapter(subject_id):
    subject = Subject.query.get(subject_id)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
        return redirect(url_for('subjects_management'))
    subjects = Subject.query.all()
    return render_template('subject.html', subjects=subjects)
@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.description = request.form['description']
        db.session.commit()
        return redirect(url_for('subjects_management'))
    return render_template('subject.html', chapter=chapter)
@app.route('/delete_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('subjects_management'))


@app.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    if request.method == 'POST':
        chapter_id = request.form['chapter_id']
        name = request.form['name']
        date_of_quiz = datetime.strptime(request.form['date_of_quiz'], '%Y-%m-%d').date()
        
        try:
            time_of_quiz = int(request.form['time_of_quiz'])  # Expect duration in minutes
        except ValueError:
            flash("Invalid quiz duration. Please enter a number in minutes.", "error")
            return redirect(url_for('add_quiz'))

        remarks = request.form['remarks']

        quiz = Quiz(
            name=name,
            date_of_quiz=date_of_quiz,
            time_of_quiz=time_of_quiz, 
            remarks=remarks,
            chapter_id=chapter_id
        )

        db.session.add(quiz)
        db.session.commit()
        return redirect(url_for('quiz_management'))

    return render_template('quiz.html', quizzes=[])

@app.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz not found!', 'error')
        return redirect(url_for('quiz_management'))

    if request.method == 'POST':
        quiz.chapter_id = request.form['chapter_id']
        quiz.name = request.form['name']
        quiz.date_of_quiz = datetime.strptime(request.form['date_of_quiz'], '%Y-%m-%d').date()

        try:
            quiz.time_of_quiz = int(request.form['time_of_quiz'])  # Expect duration in minutes
        except ValueError:
            flash("Invalid quiz duration. Please enter a number in minutes.", "error")
            return redirect(url_for('edit_quiz', quiz_id=quiz.id))

        quiz.remarks = request.form['remarks']

        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('quiz_management'))

    quizzes = Quiz.query.all()
    return render_template('quiz.html', quizzes=quizzes, quiz=quiz)

@app.route('/delete_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for('quiz_management'))
@app.route('/search_quiz', methods=['GET'])
def search_quiz():
    query = request.args.get('quiz_name')
    if query:
        quizzes = Quiz.query.filter(Quiz.name.contains(query)).all()
    else:
        quizzes = Quiz.query.all()
    return render_template('quiz.html', quizzes=quizzes)
@app.route('/search_user_quiz', methods=['GET'])
def search_user_quiz():
    query = request.args.get('quiz_name', '').strip()

    # If a query is provided, filter quizzes, else return all quizzes
    if query:
        quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{query}%")).all()
    else:
        quizzes = Quiz.query.all()

    return render_template('user_dashboard.html', quizes=quizzes, search_query=query)

@app.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
def add_question(quiz_id):
    if request.method == 'POST':
        quiz_id = request.form['quiz_id']
        name = request.form['name']
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']
        question = Question(name=name, 
                            question_statement=question_statement, 
                            option1=option1, 
                            option2=option2, 
                            option3=option3, 
                            option4=option4, 
                            answer=answer, 
                            quiz_id=quiz_id)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('quiz_management'))
    return render_template('quiz.html', quizzes=[])
@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get(question_id)
    if request.method == 'POST':
        question.name = request.form['name']
        question.question_statement = request.form['question_statement']
        question.option1 = request.form['option1']
        question.option2 = request.form['option2']
        question.option3 = request.form['option3']
        question.option4 = request.form['option4']
        question.answer = request.form['answer']
        db.session.commit()
        return redirect(url_for('quiz_management'))
    return render_template('quiz.html', question=question)

@app.route('/delete_question/<int:question_id>', methods=['GET', 'POST'])
def delete_question(question_id):
    question = Question.query.get(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('quiz_management'))    
    
@app.route('/quiz_management', methods=['GET'])
def quiz_management():
    quizzes = Quiz.query.all()  # Fetch all quizzes
    return render_template('quiz.html', quizzes=quizzes)

@app.route('/start_quiz/<int:quiz_id>',methods=['GET','POST'])
def start_quiz(quiz_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    quiz=Quiz.query.get(quiz_id)
    questions=Question.query.filter_by(quiz_id=quiz_id).all()
    time = quiz.time_of_quiz * 60  # Convert minutes to seconds
    if request.method == 'POST':
        score=0
        for question in questions:
            user_answer=request.form[f'question-{question.id}']
            if user_answer==question.answer:
                score +=1
        score=Scores(quiz_id=quiz_id,user_id=session['user_id'],time_taken=datetime.now().time(),total_score=score,)        
        db.session.add(score)
        db.session.commit()
        return redirect(url_for('user_dashboard'))
    return render_template('start_quiz.html',quiz=quiz,questions=questions,time=time) 
       
@app.route('/scores',methods=['GET'])
def scores():
    if session.get('username') is None:
        return redirect(url_for('login'))
    scores=Scores.query.filter_by(user_id=session['user_id']).all()
    time_taken=[score.time_taken for score in scores]
    return render_template('scores.html',scores=scores,time_taken=time_taken)    
@app.route('/admin_summary',methods=['GET','POST'])
def admin_summary():
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    Subjects_attempt=db.session.query(Subject.name,db.func.count(Scores.user_id)).join(Quiz,Scores.quiz_id==Quiz.id).join(Chapter,Quiz.chapter_id==Chapter.id).join(Subject,Chapter.subject_id==Subject.id).group_by(Subject.name).all()
    print(Subjects_attempt)

    Subject_dict=dict(Subjects_attempt)
    top_scorer=db.session.query(Subject.name,db.func.max(Scores.total_score)).join(Quiz,Scores.quiz_id==Quiz.id).join(Chapter,Quiz.chapter_id==Chapter.id).join(Subject,Chapter.subject_id==Subject.id).group_by(Subject.name).all()
    top_scorer_dict=dict(top_scorer)
    pie_labels=[]
    pie_values=[]
    for key,value in Subject_dict.items():
        pie_labels.append(key)
        pie_values.append(value)
    bar_labels=list(top_scorer_dict.keys())
    bar_values=list(top_scorer_dict.values())
    
    plt.figure(figsize=(8,8))
    sns.barplot(x=bar_labels,y=bar_values)
    plt.xlabel('Subjects')
    plt.ylabel('Top Score')
    plt.title('Top Scorers')
    bar_chart=os.path.join(app.config['Chart_IMAGE'],'bar_chart.png')
    plt.savefig(bar_chart)
    
    
    bar_chart_url=url_for('static',filename='charts/bar_chart.png')
    plt.figure(figsize=(8,8))
    plt.pie(pie_values,labels=pie_labels,autopct='%1.1f%%')
    plt.title('Subjects Attempted')
    pie_chart=os.path.join(app.config['Chart_IMAGE'],'pie_chart.png')
    plt.savefig(pie_chart)
    plt.close()
    pie_chart_url=url_for('static',filename='charts/pie_chart.png')
    
    avg_scores = db.session.query(Subject.name, db.func.avg(Scores.total_score)) \
        .join(Quiz, Scores.quiz_id == Quiz.id) \
        .join(Chapter, Quiz.chapter_id == Chapter.id) \
        .join(Subject, Chapter.subject_id == Subject.id) \
        .group_by(Subject.name).all()
    line_labels=[]
    line_values=[]
    for avg_score in avg_scores:
        line_labels.append(avg_score[0])  # Subject name
        line_values.append(avg_score[1])  # Average score

    plt.figure(figsize=(8,8))
    sns.lineplot(x=line_labels,y=line_values)
    plt.xlabel('Subjects')
    plt.ylabel('Average Score')
    plt.title('Average Scores')
    line_chart=os.path.join(app.config['Chart_IMAGE'],'line_chart.png')
    plt.savefig(line_chart)
    plt.close()
    line_chart_url=url_for('static',filename='charts/line_chart.png')
    return render_template('admin_summary.html',bar_chart_url=bar_chart_url,pie_chart_url=pie_chart_url,line_chart_url=line_chart_url)
@app.route('/profile',methods=['GET','POST'])
def profile():
    if session.get('username') is None:
        return redirect(url_for('login'))
    user=User.query.get(session['user_id'])
    if request.method=='POST':
        user.full_name=request.form['full_name']
        user.qualification=request.form['qualification']
        user.dob=datetime.strptime(request.form['dob'],'%Y-%m-%d').date()
        user.gender=request.form['gender']
        user.email=request.form['email']
        user.phone=request.form['phone']
        user.address=request.form['address']
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('profile.html',user=user)

@app.route('/edit_profile',methods=['GET','POST'])
def edit_profile():
    if session.get('username') is None:
        return redirect(url_for('login'))
    user=User.query.get(session['user_id'])
    if request.method=='POST':
        user.full_name=request.form['full_name']
        user.qualification=request.form['qualification']
        user.dob=datetime.strptime(request.form['dob'],'%Y-%m-%d').date()
        user.gender=request.form['gender']
        user.email=request.form['email']
        user.phone=request.form['phone']
        user.address=request.form['address']
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('edit_profile.html',user=user)

load_dotenv()
CORS(app) # Enable CORS for all routes

# IMPORTANT: Retrieve your Gemini API Key from environment variables
# This is secure for deployment and works well with python-dotenv for local development.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Add a check to ensure the API key is set
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in a .env file or your system environment.")

# Gemini API endpoint for gemini-2.0-flash
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    """
    Generates 5 multiple-choice questions (MCQs) on a given subject
    using the Gemini API.
    """
    subject = request.json.get('subject')
    if not subject:
        return jsonify({"error": "No subject provided"}), 400

    # Define a list of allowed educational subjects
    # You can expand this list as needed
    allowed_subjects = [
        "history", "science", "mathematics", "maths", "literature", "geography",
        "physics", "chemistry", "biology", "computer science", "art history",
        "economics", "political science", "psychology", "sociology", "philosophy",
        "dbms", "sst", "social studies"
    ]

    # Convert the requested subject to lowercase for case-insensitive comparison
    normalized_subject = subject.lower()

    # Check if the requested subject is in the allowed list
    if normalized_subject not in allowed_subjects:
        return jsonify({
            "error": f"I can only generate quizzes on educational subjects. '{subject}' is not an allowed subject. Please try a topic like History, Science, or Mathematics."
        }), 400 # Use 400 Bad Request for client-side input validation failure

    # Modified Prompt: Explicitly ask for educational subjects (removed conditional error message instruction as it's handled by backend now)
    prompt = f"""Generate 5 multiple-choice questions about {subject}.
    For each question, provide:
    1. The question text.
    2. Four options (A, B, C, D).
    3. The correct answer among the options.

    Format the output as a JSON array of objects, where each object has:
    - "question": string
    - "options": array of strings (4 options)
    - "correct_answer": string (the correct option text)

    Example of valid format:
    [
      {{
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "correct_answer": "Paris"
      }},
      {{
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "correct_answer": "Mars"
      }}
    ]
    """

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
            "responseMimeType": "application/json", # Request JSON output
            "responseSchema": { # Only define the successful quiz response schema
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "question": {"type": "STRING"},
                        "options": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"}
                        },
                        "correct_answer": {"type": "STRING"}
                    },
                    "required": ["question", "options", "correct_answer"]
                }
            }
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # This is a comment to force Flask reloader to pick up changes
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        gemini_response = response.json()
        
        if gemini_response and 'candidates' in gemini_response and \
           len(gemini_response['candidates']) > 0 and \
           'content' in gemini_response['candidates'][0] and \
           'parts' in gemini_response['candidates'][0]['content'] and \
           len(gemini_response['candidates'][0]['content']['parts']) > 0 and \
           'text' in gemini_response['candidates'][0]['content']['parts'][0]:
            
            quiz_data_str = gemini_response['candidates'][0]['content']['parts'][0]['text']
            try:
                parsed_response = json.loads(quiz_data_str)
                
                # Now, we only expect a list of questions. If it's not, it's an AI generation issue.
                if isinstance(parsed_response, list) and len(parsed_response) >= 5:
                    return jsonify({"questions": parsed_response[:5]}) # Return only 5 questions
                else:
                    print(f"Generated quiz data is not a list of 5+ questions: {parsed_response}")
                    return jsonify({"error": "Failed to generate enough questions or invalid format from AI. Please try again or a different subject."}), 500
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e} - Raw response: {quiz_data_str}")
                return jsonify({"error": "Failed to parse quiz data from AI. Invalid JSON format."}), 500
        else:
            print(f"Unexpected Gemini response structure for quiz generation: {gemini_response}")
            return jsonify({"error": "Could not generate quiz. AI response format unexpected."}), 500

    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API for quiz generation: {e}")
        return jsonify({"error": "Failed to connect to AI service for quiz generation. Check API key or network."}), 500
    except Exception as e:
        print(f"An unexpected error occurred during quiz generation: {e}")
        return jsonify({"error": "An internal server error occurred during quiz generation."}), 500

@app.route('/evaluate_answer', methods=['POST'])
def evaluate_answer():
    """
    Evaluates a user's answer for an MCQ and provides a 2-line explanation
    using the Gemini API.
    """
    data = request.json
    user_answer = data.get('user_answer')
    correct_answer = data.get('correct_answer')
    question = data.get('question')
    subject = data.get('subject')

    if not all([user_answer, correct_answer, question, subject]):
        return jsonify({"error": "Missing data for evaluation"}), 400

    is_correct = (user_answer == correct_answer)

    # Prompt for evaluation and explanation
    prompt = f"""The user answered the following question about {subject}:
    Question: "{question}"
    User's answer: "{user_answer}"
    Correct answer: "{correct_answer}"

    Based on whether the user's answer is correct or wrong, provide a concise 2-line explanation.
    If the answer is correct, explain why it's correct.
    If the answer is wrong, explain why it's wrong and briefly elaborate on the correct answer.
    Do NOT explicitly state "Correct!" or "Wrong!" in the explanation itself.
    """

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 100 # Keep explanation concise
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        gemini_response = response.json()
        
        explanation_text = "No explanation available."
        if gemini_response and 'candidates' in gemini_response and \
           len(gemini_response['candidates']) > 0 and \
           'content' in gemini_response['candidates'][0] and \
           'parts' in gemini_response['candidates'][0]['content'] and \
           len(gemini_response['candidates'][0]['content']['parts']) > 0 and \
           'text' in gemini_response['candidates'][0]['content']['parts'][0]:
            
            explanation_text = gemini_response['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"Unexpected Gemini response structure for explanation: {gemini_response}")

        return jsonify({
            "is_correct": is_correct,
            "explanation": explanation_text
        })

    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API for evaluation: {e}")
        return jsonify({"error": "Failed to connect to AI service for evaluation"}), 500
    except Exception as e:
        print(f"An unexpected error occurred during evaluation: {e}")
        return jsonify({"error": "An internal server error occurred during evaluation."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets this environment variable
    app.run(host="0.0.0.0", port=port, debug=True)
