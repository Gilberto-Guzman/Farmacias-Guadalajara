from flask import render_template, request, redirect, url_for, session
from mysqlconnection import *
import MySQLdb.cursors
import re


@app.route("/")
def index():
    return render_template("views/home/home.html")


@app.route("/home")
def home():
    return render_template("views/home/home.html")


@app.route("/contact")
def contact():
    return render_template("views/contact/contact.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = '¡Ha iniciado sesión correctamente!'
            return redirect('/home')
        else:
            msg = 'Usuario o contraseña incorrectos...'
    return render_template('views/login/login.html', msg=msg)


@app.route("/register", methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Esta cuenta ya esta en uso...'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Correo electronico invalido...'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'El nombre de usuario debe contener solo caracteres y numeros...'
        elif not username or not password or not email:
            msg = '¡Porfavor rellene el formulario!'
        else:
            cursor.execute(
                'INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = '¡Se ha registrado correctamente!'
    elif request.method == 'POST':
        msg = '¡Porfavor rellene el formulario!'
    return render_template('views/register/register.html', msg=msg)


@app.route('/logout')
def logout():

    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/dashboard')
def dashboard():
    return render_template('views/dashboard/dashboard.html')


# ---CUENTAS---
@app.route('/account')
def account():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts')
    accounts = cursor.fetchall()
    cursor.close()

    return render_template('views/account/account.html', accounts=accounts)


@app.route('/deleteaccount', methods=['POST'])
def deleteaccount():
    user_id = request.form['user_id']

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM accounts WHERE id = %s", (user_id,))
    mysql.connection.commit()

    return redirect('/account')


@app.route('/onclickeditaccount', methods=['POST'])
def onclickeditaccount():
    session['user_id'] = request.form['user_id']
    session['editform'] = True
    return redirect('/account')


@app.route('/editaccount', methods=['POST'])
def editaccount():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE accounts SET username=%s, password=%s, email=%s WHERE id=%s",
                   (username, password, email, session['user_id'],))
    mysql.connection.commit()

    session.pop('editform', None)

    return redirect('/account')


@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    msg = ''
    if session.get('loggedin') == True:
        if request.method == 'POST' and 'name' in request.form and 'address' in request.form and 'phonenumber' in request.form and 'reasonofthevisit' in request.form and 'dateandtime' in request.form:

            username = session['username']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT email FROM accounts WHERE username = % s', (username, ))
            email = cursor.fetchone()['email']
            name = request.form['name']
            address = request.form['address']
            phonenumber = request.form['phonenumber']
            reasonofthevisit = request.form['reasonofthevisit']
            dateandtime = request.form['dateandtime']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'INSERT INTO appointments VALUES (NULL, % s, % s, % s, % s, % s, % s, % s)', (username, email, name, address, phonenumber, reasonofthevisit, dateandtime, ))
            mysql.connection.commit()
            msg = '¡Se ha registrado su cita correctamente!'
        return render_template('views/appointment/appointment.html', msg=msg)
    else:
        return redirect('/login')


# if __name__ == '__main__':
#    app.run(host='0.0.0.0')


if __name__ == '__main__':
    app.run(debug=True)
