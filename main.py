from flask import Flask, render_template, flash, redirect, session, request, url_for
from forms import SignUpForm, SignInForm, TaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AnhLang iz da boet'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "app.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

import models
@app.route('/')
def main():
    todoList = [{
        'name':'Buy milk',
        'description':'Buy 2 liters of milk in Coopmart.'
    },{
        'name':'Get money',
        'description':'Get 500k form ATM'
    }]

    return render_template('index.html', todolist = todoList)

@app.route('/signUp', methods=['GET', 'POST'])
def showSignUp():
    form = SignUpForm()
    if form.validate_on_submit():
        print("Validate on submit")
        _fname = form.inputFirstName.data
        _lname = form.inputLastName.data
        _email = form.inputEmail.data
        _password = form.inputPassword.data


        if(db.session.query(models.User).filter_by(email = _email).count()==0):
            user = models.User(first_name = _fname,last_name = _lname, email= _email)
            user.set_password(_password)
            db.session.add(user)
            db.session.commit()

            return render_template('signUpSuccess.html', user = user)
        else:
            flash('Email {} is already exsits'.format(_email), 'danger')

    print ("Not validate on submit")
    return render_template('signup.html', form = form)

@app.route('/signIn', methods=['GET','POST'])
def signIn():

    if 'user' not in session:
        form = SignInForm()

        if form.validate_on_submit():
            _email = form.inputEmail.data
            _password = form.inputPassword.data

            user = db.session.query(models.User).filter_by(email = _email).first()

            if (user is None):
                flash('Wrong email address or password!', 'danger')
            else:
                if (user.check_password(_password)):
                    session['user'] = user.user_id
                    # return render_template('userhome.html')

                    return redirect('/userHome')
                else:
                    flash('Wrong email address or password', 'danger')
        return render_template('signin.html', form = form)
    else:
        flash('Your already logged in', 'success')
        return redirect('userHome')

@app.route('/logOut')
def logOut():
    session.clear()
    return redirect('/')

@app.route('/userHome', methods=['GET', 'POST'])
def userHome():
    _user_id = session.get('user')
    priority_query = models.Priority.query.all()
    if len(priority_query) == 0:
        priorities = ['1st', '2nd', '3rd', '4th']
        for item in priorities:
            priority = models.Priority(description = item)
            db.session.add(priority)
            db.session.commit()


    if _user_id:
        priorities = models.Priority.query.all()
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        return render_template('userhome.html', user = user, priorities = priorities)
    else:
        return redirect('/')

@app.route('/addTask', methods=['GET', 'POST'])
def addTask():
    form = TaskForm()
    priorities = models.Priority.query.all()
    if 'user' not in session:
        flash('Please login first', 'danger')
        return redirect('signIn')
    else:
        if request.method == 'POST':
            print("Validate on submit")
            _tname = form.inputTask.data
            _tpriority = request.form.get('priority')
            task = models.Task(description = unicode(_tname).decode('utf-8'), user_id = session.get('user'), priority_id = _tpriority)
            db.session.add(task)
            db.session.commit()
            flash('Your task {} has been added'.format(_tname), 'success')
            return redirect('/addTask')
        return render_template('addtask.html', form = form, priorities = priorities)

@app.route('/editTask/<int:id>', methods=['GET','POST'])
def editTask(id):
    task = db.session.query(models.Task).filter_by(task_id = id).first()
    priorities = models.Priority.query.all()

    if request.method == 'POST':
        task.description = request.form.get('description')
        task.priority_id = request.form.get('priority')
        db.session.commit()
        flash('Your task has been changed to {}'.format(task.description), 'success')
        return redirect(url_for('userHome'))
    return render_template('addtask.html', priorities = priorities, task = task)

@app.route('/removeTask', methods=['GET','POST'])
def removeTask():
    task_id = request.form.get('id')
    task = db.session.query(models.Task).filter_by(task_id = task_id).first()
    if request.method == "POST":
        db.session.delete(task)
        db.session.commit()
        flash('Your task has been deleted', 'success')
    return redirect((url_for('userHome')))

@app.route('/changeStatus', methods=['GET','POST'])
def changeStatus():
    task_id = request.form.get('id')
    task = db.session.query(models.Task).filter_by(task_id=task_id).first()
    if request.method == 'POST':

        task.status = not task.status
        db.session.commit()
    return redirect((url_for('userHome')))
if __name__ == '__main__':
    app.run(host='127.0.0.1', port='6060', debug=True)
