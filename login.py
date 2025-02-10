from flask import Flask, request, render_template, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '301011'
app.config['MYSQL_DB'] = 'marena'

mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('login_page.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        # Insert data into MySQL
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_email = cur.fetchone()
        if existing_email:
            return render_template('login_page.html', alert_message="Email already exists")
        
        cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        mysql.connection.commit()
        cur.close()
        session['email'] = email #saves the email value so it can be used later



        return redirect(url_for('time_input'))
    
@app.route('/time_input')
def time_input():
   email = session.get('email')
   if not email:
    return "Error: Email not found in session!"
   
   cur = mysql.connection.cursor()
   cur.execute('SELECT entry_time FROM users WHERE email = %s',(email,))
   user = cur.fetchone()
   cur.close()

   

   entry_time_submitted = user[0] is not None
   total_count = session.get('total_count', None)
   one_hour = session.get('one_hour' , None)
   least_hour = session.get('least_hour',None)
   least_count = session.get('least_count',None)
   return render_template('index.html', entry_time_submitted=entry_time_submitted,total_count=total_count ,least_count=least_count,least_hour=least_hour)

@app.route('/submit_time' , methods = ['POST'])
def submit_time():
    if request.method=='POST':
        entry_time = request.form['entry_time']
        email = session.get('email')

        cur = mysql.connection.cursor()
        cur.execute("""UPDATE users 
                    SET entry_time = %s
                    WHERE email = %s  
                    """,(entry_time,email))
        mysql.connection.commit()
        cur.execute('SELECT COUNT(id) as total_count from users')
        result = cur.fetchone()
        total_count = result[0]
        session['total_count'] = total_count




        #cur.execute("""
        #    SELECT COUNT(id)
        #    FROM users
        #   WHERE entry_time BETWEEN DATE_SUB(%s , INTERVAL 1 HOUR) AND %s
        #            """,(entry_time,entry_time,))
        #one_hour = cur.fetchone()[0]
        #session['one_hour'] = one_hour




        cur.execute("""
            SELECT HOUR(entry_time) AS hour, COUNT(*) AS user_count
            FROM users
            GROUP BY HOUR(entry_time)
            ORDER BY user_count ASC
            LIMIT 1
                    """)
        result = cur.fetchone()
        if result:
            least_hour, least_count = result
            session['least_hour'] = least_hour
            session['least_count'] = least_count
        else:
            session['least_hour'] = least_hour
            session['least_count'] = least_count
        cur.close()
    return redirect(url_for('time_input'))
if __name__ == "__main__":
    app.run(debug=True)

