from flask import Flask, render_template

#create a flask instance
app = Flask(__name__)

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

