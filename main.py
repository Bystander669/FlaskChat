from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, InputRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



#create a flask instance
app = Flask(__name__)
#add database/old db
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#mysqldb
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:bystander_669@localhost/users"

#secret key
app.config['SECRET_KEY'] = "password"


#initialize db
db = SQLAlchemy(app)

#create model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    #create string
    def __repr__(self):
        return '<Name %r>' % self.name
with app.app_context():
    db.create_all()

#update record in database
@app.route('update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = AddUserform


#create a route decorator
@app.route('/')
def index():
    sentence = 'teach <strong>me</strong> something'
    fruits = ['apple','banana','durian','mango',69]
    return render_template('index.html',sentence=sentence,fruits=fruits)


#http://127.0.0.1:5000/user/(custom name)
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


#error handler for error 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

#error handler for error 500
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

#create a form class
class Nameform(FlaskForm):
    name = StringField("Enter your name: ", validators=[DataRequired()])
    submit= SubmitField("Submit")

#create a name page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = Nameform()
    #Validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
    return render_template('name.html', name=name, form=form)


#create user form with email
class AddUserform(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired(), Email()])
    submit= SubmitField("Submit")

#update record in database
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = AddUserform()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        try:
            db.session.commit()
            flash("User Updated Succ")
            return render_template('update.html', form=form, name_to_update=name_to_update)
        except:
            flash("Update failed....try again")
            return render_template('update.html', form=form, name_to_update=name_to_update)
    else:
        flash("Update failed....try again")
        return render_template('update.html', form=form, name_to_update=name_to_update)

#create route to AddUser
@app.route('/user/add', methods=['GET','POST'])
def add_user():
    name = None
    form = AddUserform()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        flash("User Added Successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)