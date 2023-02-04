"""
Author: SAHAN KANSAKAR
Runs on an EC2 instance, configured apache server on ubuntu, with sqlite3
Interactive web for:
    1. registration page - registers a new user
    2. user basic -  details can be updated
    3. Home - after user logs in the user information is displayed with uploaded file
    4. if the user is not logged in, the user is prompted to log in
    5. count - a page for uploading a txt file and counting the words in the file
    6. For extra credit the uploaded file is displayed after the user is logged in and can be downloaded
"""
from flask import Flask, render_template, redirect, url_for, request, session, send_from_directory
from collections import Counter
import re
import sqlite3
app = Flask(__name__)
app.secret_key = 'isecret_key'
#DATABASE = '/var/www/html/flaskapp/database.db'
DATABASE = '/var/www/data/database.db'
app.config['DATABASE'] = DATABASE

"""
Creates a database connection
Returns: the database connection
"""
def get_db_connection():
  conn = sqlite3.connect(app.config['DATABASE'])
  #conn = sqlite3.connect(DATABASE)
  conn.row_factory = sqlite3.Row
  return conn

"""
Retrieves the user information from the database
Returns: the user object
"""
def get_user(username):
  conn = get_db_connection()
  user = conn.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
  conn.close()
  return user

"""
Default content display that shows the user information and the extra credit file information
"""
@app.route('/')
@app.route('/home')
def home():
  if session.get('username') is not None:
    user = get_user(session.get('username'))
    return render_template('home.html', user=user)
  else:
    return redirect(url_for('login'))

"""
Form process for logging the user into the web application
"""
@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    user = get_user(request.form['username'])
    if user is None or request.form['password'] != user['password']:
      error = 'Invalid. Please try again.'
    else:
      session.clear()
      session['username'] = user['username']
      return redirect(url_for('home'))
  return render_template('login.html', error=error)

"""
Logs the current user out of the web application
"""
@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('home'))


"""
Registers a new user in the database and creates the User object
"""
@app.route('/registration', methods=['GET', 'POST'])
def registration():
  error = None
  regexp = re.compile('[^0-9a-zA-Z]+')
  if request.method == 'POST':
    if request.form['username'] == '' or request.form['password'] == '':
      error = 'Invalid. Username and Password are both required.'
      return render_template('registration.html', error=error)
    elif (' ' in request.form['username']):
      error = 'Invalid. Username cannot contain a space.'
      return render_template('registration.html', error=error)
    elif regexp.search(request.form['username']):
      error = 'Invalid. Username can only be 0-9 and a-z.'
      return render_template('registration.html', error=error)
    else:
      user = get_user(request.form['username'])
      if user is None:
        session.clear()
        username = request.form['username'].lower()
        session['username'] = username
        conn = get_db_connection()
        conn.execute('INSERT INTO user (username, password) VALUES (?, ?)', (username, request.form['password']))
        conn.commit()
        conn.close()
        return redirect(url_for('details'))
      else:
        error = 'Invalid. Username already exists.'
        return render_template('registration.html', error=error)
  else:
    session.clear()
    return render_template('registration.html', error=error)

"""
Displays and allows the logged in user update the basic information
"""
@app.route('/details', methods=['GET', 'POST'])
def details():
  user = None
  username = session.get('username')
  if request.method == 'POST':
    conn = get_db_connection()
    conn.execute('UPDATE user SET firstname = ?, lastname = ?, email = ? WHERE username = ?', (request.form['firstname'], request.form['lastname'], request.form['email'], username))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))
  user = get_user(username)
  return render_template('details.html', user=user)

"""
Allows the user to upload a file and performs a count of words
"""
@app.route('/count', methods=['GET', 'POST'])
def count():
  message=None
  username = session.get('username')
  if request.method == 'POST' and session.get('username') is not None:
    f = request.files['the_file']
    uploadName = f.filename
    saveFileName = '/var/www/uploads/' + session.get('username') + '.txt'
    f.save(saveFileName)
    with open(saveFileName,'r') as file:
      content = file.read()
      message = 'Uploaded File "' + uploadName + '" has word count ' + str(len(content.split()))
    conn = get_db_connection()
    conn.execute('UPDATE user SET text_file = ? WHERE username = ?', (message, username))
    conn.commit()
    conn.close()
    #message = 'file uploaded successfully'
  return render_template('count.html', message=message)

"""
a link to download the file uploaded bye the logged in user
"""
@app.route('/download')
def download():
  filename = session.get('username') + '.txt'
  return send_from_directory(directory='/var/www/uploads/', filename=filename)

"""
counts the characters in string that is part of the query string
"""
@app.route('/countme/<input_str>')
def count_me(input_str):
  input_counter = Counter(input_str)
  response = []
  for letter, count in input_counter.most_common():
    response.append('"{}": {}'.format(letter, count))
  return '<br>'.join(response)

"""
Start and run the web application
"""
if __name__ == '__main__':
  app.run()
