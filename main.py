import datetime

from flask import Flask, render_template, flash, redirect, session, request, url_for
from forms import SignUpForm, SignInForm, TaskForm, ProjectForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import models
from flask_msearch import  Search
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AnhLang iz da boet'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "app.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
search = Search()
search.init_app(app)

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
    status_query = models.Status.query.all()
    if len(priority_query) == 0:
        priorities = ['1st', '2nd', '3rd', '4th']
        for item in priorities:
            priority = models.Priority(description = item)
            db.session.add(priority)
            db.session.commit()
    if len(status_query) == 0:
        statuses = ['Pending', 'In progress', 'Outdated', 'Completed']
        for item in statuses:
            status = models.Status(desc = item)
            db.session.add(status)
            db.session.commit()

    if _user_id:
        priorities = models.Priority.query.all()
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        projects = db.session.query(models.Project).filter_by(user_id = _user_id).all()
        for project in projects:
            tasks = db.session.query(models.Task).filter_by(project_id = project.project_id).all()
            pendingTasks = db.session.query(models.Task).filter_by(project_id = project.project_id, status_id = 1).all()
            progressTasks = db.session.query(models.Task).filter_by(project_id = project.project_id, status_id = 2).all()
            completedTasks = db.session.query(models.Task).filter_by(project_id = project.project_id, status_id = 4).all()
            statuses = db.session.query(models.Status).all()

            if project.deadline.date() < datetime.datetime.now().date():
                project.status_id = 3
                db.session.commit()

            if tasks:
                if len(pendingTasks) == len(tasks):
                    project.status_id = 1
                    db.session.commit()
                elif len(progressTasks) > 0:
                    project.status_id = 2
                    db.session.commit()
                elif len(completedTasks) == len(tasks):
                    project.status_id = 4
                    db.session.commit()
                elif completedTasks and pendingTasks:
                    project.status_id = 2

        return render_template('userhome.html', user = user, priorities = priorities, projects =projects, statuses = statuses)
    else:
        return redirect('/')

@app.route('/tasks/<int:id>', methods=['GET', 'POST'])
def tasks(id):
    priorities = models.Priority.query.all()
    project = db.session.query(models.Project).filter_by(project_id = id).first()
    statuses = db.session.query(models.Status).all()
    tasks = db.session.query(models.Task).filter_by(project_id = id)
    for task in tasks:
        if task.deadline.date() < datetime.datetime.now().date():
            task.status_id = 3
            db.session.commit()
    return render_template('tasks.html', priorities =priorities, project = project, statuses=statuses, tasks = tasks)
@app.route('/addTask/<int:id>', methods=['GET', 'POST'])
def addTask(id):

    if 'user' not in session:
        flash('Please login first', 'danger')
        return redirect('signIn')
    else:
        form = TaskForm()
        priorities = models.Priority.query.all()
        project = db.session.query(models.Project).filter_by(project_id=id).first()
        if request.method == "POST":
            deadline = form.inputTaskDeadline.data
            projectDeadline = project.deadline.date()
            if deadline <= projectDeadline:
                _tname = form.inputTask.data
                _tpriority = request.form.get('priority')
                status = db.session.query(models.Status).filter_by(desc="Pending").first()
                task = models.Task(description = _tname, project_id =id, priority_id = _tpriority, deadline=form.inputTaskDeadline.data, status=status)
                db.session.add(task)
                db.session.commit()
                flash('Your task {} has been added'.format(_tname), 'success')
                return redirect(url_for('tasks', id = id))
            else:
                flash('Deadline must be earlier than {}'.format(project.deadline), 'danger')
                return redirect(url_for('addTask', id=id))
        return render_template('addtask.html', form = form, priorities = priorities, project = project)

@app.route('/editTask/<int:id>', methods=['GET','POST'])
def editTask(id):
    statuses = models.Status.query.all()
    task = db.session.query(models.Task).filter_by(task_id = id).first()
    priorities = models.Priority.query.all()
    project = db.session.query(models.Project).filter_by(project_id = task.project_id).first()

    if request.method == 'POST':
        deadline = datetime.datetime.strptime(request.form.get('deadline'),'%Y-%m-%d').date()
        projectDeadline = project.deadline.date()
        if deadline <= projectDeadline:
            task.description = request.form.get('description')
            task.priority_id = request.form.get('priority')
            task.deadline = deadline
            task.status_id = request.form.get('status')
            db.session.commit()
            flash('Your task has been changed to {}'.format(task.description), 'success')

            return redirect(url_for('tasks', id = project.project_id))
        else:
            flash('Deadline must be earlier than {}'.format(project.deadline), 'danger')
            return redirect(url_for('addTask', id=id))

    return render_template('addtask.html', priorities = priorities, task = task, project=project, statuses=statuses)

@app.route('/removeTask', methods=['GET','POST'])
def removeTask():
    task_id = request.form.get('id')
    task = db.session.query(models.Task).filter_by(task_id = task_id).first()
    if request.method == "POST":
        db.session.delete(task)
        db.session.commit()
        flash('Your task has been deleted', 'success')
    return redirect((url_for('tasks', id = task.project_id)))

@app.route('/addProject', methods=['GET','POST'])
def addProject():
    _user_id = session.get('user')
    form = ProjectForm()
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        if form.validate_on_submit():
            _project_name = form.inputProjectName.data
            _project_deadline = form.inputProjectDeadline.data

            status = db.session.query(models.Status).filter_by(desc="Pending").first()
            _project_id = request.form['id']
            _description = form.inputProjectDesc.data
            if (_project_id == "0"):
                project = models.Project(
                    name=_project_name,
                    deadline=_project_deadline,
                    status=status,
                    desc = _description,
                    user=user,
                )
                db.session.add(project)
            else:
                project = db.session.query(models.Project).filter_by(project_id=_project_id).first()
                project.name = _project_name
                project.deadline = _project_deadline
                project.status = status
            db.session.commit()
            flash("{} has been added".format(project.name), "success")
            return redirect('/userHome')
        return render_template('addproject.html', form=form, user=user)
    return redirect('/')
@app.route('/editProject', methods=['GET', 'POST'])
def editProject():
    _user_id = session.get('user')
    form = ProjectForm()
    if _user_id:
        user = db.session.query(models.Project).filter_by(user_id = _user_id).first()
        _project_id = request.form['id']
        project = db.session.query(models.Project).filter_by(project_id=_project_id).first()
        form.inputProjectName.default = project.name
        form.inputProjectDeadline.default = project.deadline
        form.inputProjectDesc.default = project.desc
        form.process()

        if form.validate_on_submit():
            project.name = form.inputProjectName.data
            project.deadline = form.inputProjectDeadline.data
            db.session.commit()
            return redirect('/userHome')

        return render_template('/addproject.html',
                                        form = form,
                                        user = user,
                                        project = project)
@app.route('/removeProject', methods=['GET', 'POST'])
def removeProject():
    _user_id = session.get('user')
    if _user_id:
        _project_id = request.form['id']
        if _project_id:
            project = db.session.query(models.Project).filter_by(project_id = _project_id).first()
            tasks = db.session.query(models.Task).filter_by(project_id = _project_id).delete()
            db.session.commit()
            db.session.delete(project)
            db.session.commit()
            flash("{} has been removed ".format(project.name),"success")
        return redirect('/userHome')
    return redirect('/')

@app.route('/searchProject', methods=['GET', 'POST'])
def searchProject():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        searchword = request.form.get('name')
        status = request.form.get('options')
        if status != '0':
            projects = db.session.query(models.Project).filter_by(user_id=_user_id, status_id = status).filter(models.Project.name.contains(searchword))
        else:
            projects = db.session.query(models.Project).filter_by(user_id=_user_id).filter(models.Project.name.contains(searchword))

        priorities = models.Priority.query.all()
        statuses = db.session.query(models.Status).all()
        return render_template('userHome.html', user =user, projects=projects, priorities =priorities, statuses=statuses)
    else:
        return redirect('/signIn')

@app.route('/searchTask/<int:id>', methods=['GET', 'POST'])
def searchTask(id):
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        searchword = request.form.get('name')
        status = request.form.get('options')
        if status != '0':
            tasks = db.session.query(models.Task).filter_by(project_id = id, status_id=status).filter(
                models.Task.description.contains(searchword))
        else:
            tasks = db.session.query(models.Task).filter_by(project_id = id).filter(
                models.Task.description.contains(searchword))

        priorities = models.Priority.query.all()
        statuses = db.session.query(models.Status).all()
        project = db.session.query(models.Project).filter_by(project_id = id).first()
        return render_template('tasks.html', user=user, tasks=tasks, priorities=priorities, project=project,
                               statuses=statuses)
    else:
        return redirect('/signIn')
if __name__ == '__main__':
    app.run(host='127.0.0.1', port='6060', debug=True)
