from flask import Flask, render_template, redirect, url_for, flash, request, abort, make_response, session
from flask_migrate import Migrate
from models import db, UserModel, HomeworkModel
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from forms import LoginForm, RegistrationForm, HomeWorkForm
from datetime import datetime, timedelta, date

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

app.config['SECRET_KEY'] = 'a really really really really long secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = ""
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


day = str(date.today())
dt = datetime.strptime(day, '%Y-%m-%d')
start_date = dt - timedelta(days=dt.weekday())
end_date = start_date + timedelta(days=6)

print("Week Start Date:" + str(start_date))
print("Week End Date:" + str(end_date))


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(UserModel).get(user_id)


# general Flask Code
@app.route('/')
@app.route('/<move>')
def index(move=None):
    global start_date, end_date
    if move is None:
        session['start_date'] = start_date
        session['end_date'] = end_date
    elif move == 'next':
        session['start_date'] += timedelta(days=7)
        session['end_date'] = session['start_date'] + timedelta(days=6)
        move = None
    elif move == 'back':
        session['start_date'] -= timedelta(days=7)
        session['end_date'] = session['start_date'] + timedelta(days=6)
        move = None
    print(session['start_date'], session['end_date'])
    homeworks = HomeworkModel.query.filter(HomeworkModel.date >= session['start_date'], HomeworkModel.date <= session['end_date']).all()
    results = [
        {
            "id": homework.id,
            "date": homework.date.weekday(),
            "subject": homework.subject,
            "task": homework.task,
        } for homework in homeworks]
    return render_template('main.html', tasks=results, start_date=session['start_date'].strftime('%Y-%m-%d'), end_date=session['end_date'].strftime('%Y-%m-%d'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = UserModel(username=form.username.data)
        user.set_password(form.password1.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('admin'))
    return render_template('registration.html', form=form)


@app.route('/login/', methods=['post', 'get'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(UserModel).filter(UserModel.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('admin'))
        flash("Invalid username/password", 'error')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/admin/')
@login_required
def admin():
    return render_template('admin.html')


@app.route('/add_homework/', methods=['post', 'get'])
@login_required
def add_homework():
    form = HomeWorkForm()
    if form.validate_on_submit():
        homework = HomeworkModel(date=form.date.data, subject=form.subject.data, task=form.task.data,
                                 username=current_user.username)
        db.session.add(homework)
        db.session.commit()
        flash("Домашнее задание добавлено", 'info')
        return redirect(url_for('index'))
    return render_template('add_homework.html', form=form)


@app.route('/homework/<int:homework_id>', methods=['get', 'post'])
@login_required
def get_homework(homework_id):
    homework = db.session.query(HomeworkModel).filter(HomeworkModel.id == homework_id).first()
    if homework is None:
        return abort(404)
    if request.method == "POST":
        db.session.delete(homework)
        db.session.commit()
        flash("Homework was successfully deleted", 'info')
        return redirect(url_for('index'))
    return render_template('homework.html', homework=homework)


@app.route('/update_homework/<int:homework_id>', methods=['get', 'post'])
@login_required
def update_homework(homework_id):
    homework = db.session.query(HomeworkModel).filter(HomeworkModel.id == homework_id).first()
    form = HomeWorkForm()
    if homework is None:
        return abort(404)
    if request.method == "POST":
        if form.validate_on_submit():
            homework.date = form.date.data
            homework.task = form.task.data
            homework.subject = form.subject.data
            db.session.add(homework)
            db.session.commit()
            flash("Homework was successfully updated", 'info')
            return redirect(url_for('index'))
    return render_template('update_homework.html', homework=homework, form=form)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
