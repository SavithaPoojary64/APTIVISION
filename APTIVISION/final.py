import smtplib
from flask import Flask, render_template, request, redirect, session,send_file, url_for, send_from_directory,jsonify,json
from flask_mail import Mail, Message
import mysql.connector
import re
from datetime import date
import os
import pyttsx3
from datetime import datetime
from fuzzywuzzy import fuzz
from werkzeug.utils import secure_filename
import psycopg2
import random
import string
from mysql.connector import pooling


app = Flask(__name__)
engine = pyttsx3.init()

db = None

#images
name1='name1.png'
search='search-icon.png'
background = 'back.png'
abouticon='abouticon.png'
logo1='logo1.png'
icon='icon.png'
icon1 = 'passport.jpg'
image = 'images.png'
bg1='bg.png'

app = Flask(__name__, static_folder='static')
app.secret_key = '1234'  # Set a secret key for session
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'aptivision',
    'raise_on_warnings': True
}
# Establish a database connection
mydb = mysql.connector.connect(**db_config)
cursor = mydb.cursor()
#connecting to database
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="aptivision2"
    )
def get_database2():
    global db
    if db is None or not db.is_connected():
        db = connect_to_database()
    return db

def send_email(recipient, subject, message_body):
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient])
    msg.body = message_body

    mail.send(msg)

def send_email2(email, name, subject, password):
    # Email configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'prathvisalian893@gmail.com'
    sender_password = 'zeaeopfuzirfjsws'

    # Email content
    recipient_email = email
    message = f"Dear {name},\n\nYou have been chosen as an incharge for the subject {subject}. Please login using the credentials given to you:\n\nYour password is: {password}\n\nBest regards,\nAptiVision"

    try:
        # Create a secure connection to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, message)
        server.quit()

        print("Email sent successfully.")
    except smtplib.SMTPException as e:
        print("An error occurred while sending the email.")
        print(str(e))


# Create a connection pool
cnx_pool = pooling.MySQLConnectionPool(pool_name='aptivision_pool', pool_size=5, **db_config)
# Define and initialize the db variable
db = None

# Create a cursor to execute SQL queries
cursor = None
cnx = cnx_pool.get_connection()
cursor = cnx.cursor()

def get_database():
    return cnx_pool.get_connection()


# Configuration for the Flask-Mail extension
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'harshithabhandary03@gmail.com'  # Replace with your Gmail address
app.config['MAIL_PASSWORD'] = 'felzykhikebjbbzj'  # Replace with your Gmail password

mail = Mail(app)

#home page
@app.route("/")
def homepage():
    return render_template('home.html',name1=name1,bg=background,logo1=logo1,icon=icon)

#signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_type = request.form['user_type']
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        profile_picture = request.form.get('profile_picture', '')  # Use get() with a default value

        # Check if the username is valid
        valid_usernames = ['savithapoojary64@gmail.com', 'savithapoojary193@gmail.com', 'savithapoojary6@gmail.com', 'prathvisalian893@gmail.com','harshithabhandary03@gmail.com']
        if username not in valid_usernames:
            return render_template('signup.html', bg=background, name2=logo1,icon1=icon1, profile1=abouticon, message='Invalid username')

        # Check if the username (email ID) is already registered
        cursor = cnx.cursor()
        check_query = "SELECT * FROM user_credentials WHERE username = %s"
        cursor.execute(check_query, (username,))

        # Consume unread result
        cursor.fetchall()

        if cursor.rowcount > 0:
            cursor.close()
            message = "Email already registered. Please login."
            return render_template('signup.html', bg=background,name2=logo1, icon1=icon1, profile1=abouticon, message=message)

        # Save the user credentials to the database
        insert_query = "INSERT INTO user_credentials(user_type, username, first_name, last_name, password, confirm_password, profile_picture) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (user_type, username, first_name, last_name, password, confirm_password, profile_picture))
        cnx.commit()
        cursor.close()
        # Store the values in the session
        session['username'] = username
        session['profile_picture'] = profile_picture
        session['first_name'] = first_name
        session['last_name'] = last_name
        print(username,first_name,last_name)
    
        # Redirect to the placement head page after successful signup
        # Generate a random 4-digit OTP
        otp = ''.join(random.choices(string.digits, k=4))

            # Send the OTP to the placement head's email address
        subject = 'OTP for Placement Head'
        message_body = f'Your OTP is: {otp}'
        send_email(username, subject, message_body)

        session['otp'] = otp  # Store the OTP in the session

        return redirect('/verify-otp')


    return render_template('signup.html',name2=logo1, bg=background, image2=image)  


#login
@app.route('/login')
def login():
    # Create a cursor to execute SQL queries

    # Execute the SQL query to fetch the timetable data
    
    return render_template('login1.html',name2=logo1,bg=background)


@app.route('/submit-placement-head', methods=['POST'])
def submit_placement_head():
    email = request.form['email']
    password = request.form['password']
    

    # Validate credentials against the database
    cursor = mydb.cursor()
    query = "SELECT * FROM user_credentials WHERE username= %s AND password = %s"
    session['email1'] = email
    session['password1'] = password
    
    
    cursor.execute(query, (email, password))
    result = cursor.fetchone()
    if result:
        return redirect("/place_head")
    
    cursor.close()

    return render_template("login1.html",name2=logo1,bg=background,msg="email or password does not exist")

@app.route("/submit-inchargelogin",methods=['POST'])
def submit_in_charge():
    email = request.form['email']
    subject = request.form['subject']
    class_name= request.form.get('class')
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']

    session['email'] = email
    session['password'] = password
    session['subject'] = subject
    session['class_name'] = class_name
    session['firstname'] = firstname
    session['lastname'] = lastname
    cursor = mydb.cursor()
    query="SELECT *FROM incharge WHERE email=%s AND subject=%s AND pass=%s"
    cursor.execute(query,(email,subject,password,))
    res=cursor.fetchone()
    if res:
        return redirect("/student_in_charge")
    cursor.close()

    return render_template("login1.html",name2=logo1,bg=background,msg="email or password does not exist",)


@app.route("/submit-student", methods=['POST'])
def submit_student():
    email = request.form['email']
    rollno = request.form['rollno']
    class_name = request.form.get('class')
    password = request.form['password']
    name = request.form['name']
    print(email, rollno, class_name, password, name)

    # Establish database connection
    cursor = mydb.cursor()
    print(class_name,password)
    # Execute the query
    query = "SELECT * FROM student WHERE class=%s AND pass=%s"
    cursor.execute(query, (class_name, password,))
    res = cursor.fetchone()
    print(res)  # Print the query result for debugging purposes

    if res:
        # Store session data
        session['email'] = email
        session['password'] = password
        session['rollno'] = rollno
        session['class_name'] = class_name
        session['name'] = name

        return redirect("/student")
    else:
        cursor.close()
        return render_template("login1.html", name2=logo1, bg=background, msg="Email or password does not exist")


#otp generation
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = ''.join(request.form.getlist('otp'))  # Concatenate the values from all four OTP fields
        stored_otp = session.get('otp')

        if entered_otp == stored_otp:
            return redirect('/place_head')
        else:
            otp_error = "Invalid OTP! Please try again."
            return render_template('otp.html', otp_error=otp_error,bg=background)

    return render_template('otp.html',name2=logo1,bg=background)

#placement head
@app.route('/place_head')
def place_head():
    #signup data
    username = session.get('username')
    profile_pic = session.get('profile_picture')
    firstname = session.get('first_name')
    lastname = session.get('last_name')

    #login data
    firstname1=session.get('firstname1')
    lastname1=session.get('lastname1')
    username1=session.get('email1')

    if username is None and firstname is None and lastname is None:
        username = username1
        firstname = firstname1
        lastname = lastname1
    # Create a cursor to execute SQL queries
    
    # Execute the SQL query to fetch the timetable data
    db = get_database2()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    
    action = request.form.get('action')
    weeks = cursor.fetchall()
    weeklen=len(weeks)
    weekval=[]
    weeks_subjects = {}

    for i in range(1,weeklen+1):
        weekval.append('week'+str(i))
 #get class
    if len(weekval)!=0:
        cursor.execute("select class from week1")
        classval=[row[0] for row in cursor.fetchall()]
        for i in range(1,weeklen+1):
            table_name = f"week{i}"            
            cursor.execute("select subject from "+table_name)
            subjectval=[row[0] for row in cursor.fetchall()]
            weeks_subjects[table_name] = subjectval

    
    class_count=len(classval)
            
    db=get_database2()
    cursor = db.cursor()
    # Assuming the table name is "week1"
    cursor.execute("SELECT * FROM week1")
    sessions = cursor.fetchall()

    cursor.close()
    print(username,firstname,lastname,00)
    # Close the cursor and MySQL connection
    

    # Render the HTML template and pass the retrieved data
    return render_template('place2.html', bg=background, about=abouticon, weeks=weekval, classval=classval, weeks_subjects=weeks_subjects, class_count=class_count, sessions=sessions, icon1=icon1, username=username, profile_pic=profile_pic, firstname=firstname, lastname=lastname)

@app.route('/incharge/<action>')
def incharge(action):
    if action == 'add':
        return redirect(url_for('add_incharge'))
    elif action == 'view':
        return redirect(url_for('view_incharge'))
    elif action == 'delete':
        return redirect(url_for('delete_incharge'))
    elif action == 'view-atd':
        return redirect(url_for('view_attendance'))
    elif action=='edit':
        return redirect(url_for('edit_timetable'))
    elif action=='add-pass':
        return redirect(url_for('add_pass'))
    elif action=='notify-std':
        return redirect(url_for('notify'))

@app.route('/add_incharge')
def add_incharge():
    return redirect(url_for('addinch'))

@app.route('/addinch')
def addinch():
    return render_template('addinch.html', bg=background)
#when i click submit button in add incharge
@app.route('/submit_incharge', methods=['POST'])
def submit_incharge():
    
        cursor = mydb.cursor()

         # Retrieve form data
        subject = request.form['subject']
        name = request.form['name']
        role = request.form.get('role')
        cls = request.form.get('class_name')
        rollno = request.form.get('rollno', '')  # Get value or default to empty string
        email = request.form['email']
        password = request.form['password']

        print(email,subject,name,role,cls,rollno,password)
        if role == 'student':
            if not cls or not rollno:
                msg = "Class and Roll no are required for students."
                return render_template('addinch.html', msg=msg,bg=background)
        #check if roll no alreadu exist
        check_roll="SELECT COUNT(*) FROM incharge WHERE rollno=%s"
        cursor.execute(check_roll,(rollno,))
        roll_count=cursor.fetchone()[0]

        if role!="lecturer":
            if roll_count>0:
                msg3="This Rollno is already been selected as an incharge"
                return render_template('addinch.html',msg3=msg3,bg=background)
        

         # Check if the email already exists in the table
        check_email_query = "SELECT COUNT(*) FROM incharge WHERE email = %s"
        cursor.execute(check_email_query, (email,))
        email_count = cursor.fetchone()[0]

        if email_count > 0:
            msg2 = "This email is already in use."
            return render_template('addinch.html', msg2=msg2, bg=background)
        
        # Insert the incharge details into the database
        sql = "INSERT INTO incharge (subject, name, cls, rollno, email, pass, user) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (subject, name, cls, rollno, email, password, role)
        cursor.execute(sql, values)
        mydb.commit()
        # Send email to the incharge
        send_email2(email, name, subject, password)

        return redirect('/place_head')
    

@app.route('/view_incharge')
def view_incharge():
	# Retrieve the incharge data from the 'incharge' table
	cursor = mydb.cursor()
	sql = "SELECT * FROM incharge"
	cursor.execute(sql)
	incharge_data = cursor.fetchall()
        

	return render_template('viewinch.html', incharge_data=incharge_data,bg=background)

@app.route('/delete_incharge', methods=['GET', 'POST'])
def delete_incharge():
    warning=""
    cursor = mydb.cursor()
    sql = "SELECT * FROM incharge"
    cursor.execute(sql)
    incharge_data = cursor.fetchall()
    sql2="SELECT rollno FROM incharge"
    cursor.execute(sql2)
    incharge_data2=cursor.fetchall()
    if request.method == 'POST':
        subject = request.form['subject']
        rollno = request.form['rollno']
        email=request.form['emailid']
        # Connect to MySQL database
        cursor = mydb.cursor()

        # Delete the incharge
        query = 'DELETE FROM incharge WHERE subject = %s AND rollno = %s AND email=%s'
        cursor.execute(query, (subject, rollno,email))
        rows_deleted = cursor.rowcount

        
        # Commit the changes
        mydb.commit()

        # Close the cursor
        cursor.close()
        if rows_deleted > 0:
            return redirect(url_for('place_head'))
        else:
            warning= '**No matching incharge found for the selected subject and name'
        

    return render_template('deleteinch.html',incharge_data=incharge_data,incharge_data2=incharge_data2,warning=warning,bg=background)

@app.route('/view_attendance', methods=['GET', 'POST'])
def view_attendance():
    if request.method == 'POST':
        search_value = request.form.get('search')  # Get the entered search value from the form

        # Fetch attendance data for the selected week from the "attendance" table
        cursor = mydb.cursor()
        query = "SELECT * FROM attendance"
        
        if search_value:  # Check if a week value is entered
            query += " WHERE week = %s OR Class_name = %s"
            cursor.execute(query, (search_value,search_value))
        else:
            cursor.execute(query)

        attendance_data = cursor.fetchall()
        
        # Close the cursor
        cursor.close()
        
        return render_template('viewattendance.html', attendance_data=attendance_data, bg=background, search=search)
    
    return render_template('viewattendance.html', attendance_data=[], bg=background, search=search)


@app.route("/add_pass")
def add_pass():
    cursor = mydb.cursor()
    cursor.execute("SELECT class, pass FROM student")
    student_data = cursor.fetchall()
    cursor.close()

    return render_template('add_pass.html', student_data=student_data,bg=background)

@app.route('/submit_pass', methods=['POST'])
def submit_pass():
    class_name = request.form['class']
    password = request.form['password']

    cursor = mydb.cursor()

    # Check if the class already exists
    cursor.execute("SELECT * FROM student WHERE class = %s", (class_name,))
    existing_data = cursor.fetchone()

    if existing_data:
        # Update the existing row
        cursor.nextset()  # Move to the next result set
        cursor.execute("UPDATE student SET pass = %s WHERE class = %s", (password, class_name))
        mydb.commit()
        msg = "Password updated successfully"
    else:
        # Insert a new row
        cursor.execute("INSERT INTO student (class, pass) VALUES (%s, %s)", (class_name, password))
        mydb.commit()
        msg = "Password stored successfully"

    # Retrieve updated student data
    cursor.execute("SELECT class, pass FROM student")
    student_data = cursor.fetchall()
    cursor.close()

    return render_template("add_pass.html", msg=msg, student_data=student_data,bg=background)

@app.route('/notify', methods=['GET', 'POST'])
def notify():
    cursor = mydb.cursor()  # Initialize cursor outside the if statement
    
    if request.method == 'POST':
        notification = request.form['notification']
        current_date = date.today().strftime("%d/%m/%Y")
        cursor.execute("INSERT INTO notification (content, date) VALUES (%s, %s)", (notification, current_date))
        mydb.commit()
    
    cursor.execute("SELECT * FROM notification")
    notifications = cursor.fetchall()
    cursor.close()
    
    return render_template('notify.html', notifications=notifications)

@app.route('/delete/<int:notify_id>', methods=['POST'])
def delete_notification(notify_id):
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM notification WHERE id = %s", (notify_id,))
    mydb.commit()
    cursor.close()
    return redirect('/notify')


#for create time table option
@app.route('/create_timetable',methods=['GET', 'POST'])
def create_table():
    class_names = []
    weeks_subjects = {}
    sessls = []
    newls = []
    error_msg = None  # Initialize error message
    error_message=""

    if request.method == 'POST':
        week_count = int(request.form['week_count'])
        current_weeks = get_existing_weeks()
        if week_count < current_weeks:
            drop_tables(current_weeks - week_count)
        elif week_count > current_weeks:
            create_tables(week_count - current_weeks)

        class_count = int(request.form['class_count'])
        for i in range(1, class_count + 1):
            class_name = request.form.get(f'class_name_{i}')
            if class_name:
                if class_name in class_names:
                    error_msg = f"Duplicate class name '{class_name}' found."
                    break  # Exit the loop and display the error message
                class_names.append(class_name)


        # Store subject values in the respective week tables and subject columns
        for i in range(1, week_count + 1):
            table_name = f"week{i}"
            db = get_database2()
            cursor = db.cursor()

            # Delete previous subject values
            delete_query = f"DELETE FROM {table_name}"
            cursor.execute(delete_query)

            # Insert subject values into the table
            insert_query = f"INSERT INTO {table_name} (class, subject) VALUES (%s, %s)"
            if len(class_names) >= class_count:
                for j in range(1, class_count + 1):
                    subject_value = request.form.get(f'week_{i}_class_{j}')
                    if subject_value:
                        cursor.execute(insert_query, (class_names[j - 1], subject_value))
                        db.commit()  # Commit after each subject insertion
            


            cursor.close()

            # Fetch subjects for the current week
            select_query = f"SELECT subject FROM {table_name}"
            cursor = db.cursor()
            cursor.execute(select_query)
            subjects = [row[0] for row in cursor.fetchall()]
            cursor.close()

            # Store the subjects in the dictionary
            weeks_subjects[table_name] = subjects
            
            #fromhere
            if len(class_names) >= class_count:

            # Store session days in the respective week tables and day columns
                for i in range(1, week_count + 1):
                    table_name = f"week{i}"
                    db = get_database2()
                    cursor = db.cursor()

                    # Delete previous session day values
                    delete_query = f"UPDATE {table_name} SET monday='no class', tuesday='no class', wednesday='no class', thursday='no class', friday='no class', saturday='no class'"
                    cursor.execute(delete_query)
                    # Insert session day values into the table
                    for j in range(1, class_count + 1):
                        count = int(request.form.get(f'session_count_{j}', 0))  # Add this line
                        sessls.append(count)
                        print(count)
                        for k in range(1, count + 1):
                            session_day = request.form.get(f'class_{j}_session_{k}')
                            if session_day:
                                update_query = f"UPDATE {table_name} SET {session_day}='session{k}' WHERE class='{class_names[j - 1]}'"
                                cursor.execute(update_query)
                                db.commit()  # Commit after each session day insertion
                    newls=sessls[:class_count]
                    cursor.close()
            else:
                error_message="re-enter all the details"
        #tillhere
        print(sessls)
        print(newls)

    weeks = get_weeks()
    class_count = int(request.form.get('class_count', 0))
    db=get_database2()
    cursor = db.cursor()
    # Assuming the table name is "week1"
    cursor.execute("SELECT * FROM week1")
    sessions = cursor.fetchall()
    
    # Pass the `weeks_subjects` dictionary to the template
    return render_template('createTT.html', weeks=weeks, class_names=class_names, weeks_subjects=weeks_subjects, class_count=class_count, sessions=sessions, sessls=newls, bg=background, error_msg=error_msg,error_message=error_message)

def get_subjects(selected_class):
    cursor = mydb.cursor()
    cursor.execute("SELECT class, due_date, subject FROM test WHERE class = %s", (selected_class,))
    subjects = cursor.fetchall()
    cursor.close()
    return subjects

#creates dynamic tables
def create_tables(week_count):
    db = get_database2()
    cursor = db.cursor()
    table_columns = ['class', 'subject', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    existing_weeks = get_existing_weeks()
    for i in range(existing_weeks + 1, existing_weeks + week_count + 1):
        table_name = f"week{i}"
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        create_table_query += "class VARCHAR(255) PRIMARY KEY,"
        create_table_query += ", ".join(f"{col} VARCHAR(255)" for col in table_columns if col != 'class')
        create_table_query += ")"
        cursor.execute(create_table_query)
    cursor.close()


#deleted old tables
def drop_tables(count):
    db = get_database2()
    cursor = db.cursor()
    existing_weeks = get_existing_weeks()
    for i in range(existing_weeks, existing_weeks - count, -1):
        table_name = f"week{i}"
        drop_table_query = f"DROP TABLE IF EXISTS {table_name}"
        cursor.execute(drop_table_query)
    cursor.close()

def get_existing_weeks():
    db = get_database2()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    existing_weeks = len(cursor.fetchall())
    cursor.close()
    return existing_weeks

def get_weeks():
    db = get_database2()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    weeks = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return weeks

#for edit timetable option
@app.route('/edit_timetable')
def edit_timetable():
    db = get_database2()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    
    action = request.form.get('action')
    weeks = cursor.fetchall()
    weeklen=len(weeks)
    weekval=[]
    weeks_subjects = {}

    for i in range(1,weeklen+1):
        weekval.append('week'+str(i))
 #get class
    if len(weekval)!=0:
        cursor.execute("select class from week1")
        classval=[row[0] for row in cursor.fetchall()]
        for i in range(1,weeklen+1):
            table_name = f"week{i}"            
            cursor.execute("select subject from "+table_name)
            subjectval=[row[0] for row in cursor.fetchall()]
            weeks_subjects[table_name] = subjectval

    
    class_count=len(classval)
            
    db=get_database2()
    cursor = db.cursor()
    # Assuming the table name is "week1"
    cursor.execute("SELECT * FROM week1")
    sessions = cursor.fetchall()

    cursor.close()
    
    return render_template('editTT.html',weeks=weekval,classval=classval,weeks_subjects=weeks_subjects,class_count=class_count,sessions=sessions,bg=background)

#for deleting class
@app.route('/processform', methods=['POST'])
def process_form():
    classval = request.form.get('clsdrpdwn')
    action = request.form.get('action')
    
    if classval is None or action is None:
        return "Invalid form data."
    
    db = get_database2()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    tablelen=len(tables)
    
    if action == 'remove':
        for table in tables:
            table_name = table[0]
            del_query = f"DELETE FROM `{table_name}` WHERE class = '{classval}'"
            cursor.execute(del_query)
        
    
        
    # Commit the changes to the database
    db.commit()
    
    # Close the cursor and database connection
    cursor.close()
    db.close()
    
    return redirect(url_for('edit_timetable'))

#for change functionality in edit timetable
@app.route("/changefun", methods=['POST'])
def changefun():
    classval = request.form.get('clsdrpdwn2')
    action = request.form.get('action')
    db = get_database2()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    tablelen = len(tables)
    
    if action == 'change':
        for i in range(1, tablelen + 1):
            subval = request.form.get(f'subdrpdwn2{i}')
            sess1 = request.form.get(f'session1')
            sess2 = request.form.get(f'session2')
            sess3 = request.form.get(f'session3')
            sess4 = request.form.get(f'session4')
            sess5 = request.form.get(f'session5')
            sess6 = request.form.get(f'session6')
            

            update_query = f"UPDATE week{i} SET subject = %s, monday = %s, tuesday = %s, wednesday = %s, thursday = %s, friday = %s, saturday = %s WHERE class = %s"
            cursor.execute(update_query, (subval, sess1, sess2, sess3, sess4, sess5, sess6, classval))
        
    # Commit the changes to the database
    db.commit()
    
    # Close the cursor and database connection
    cursor.close()
    db.close()
    return redirect(url_for("edit_timetable"))


@app.route('/student_in_charge')
def student_in_charge():
    
    username = session.get('email')  # Retrieve the username from the session
    firstname = session.get('firstname') 
    lastname = session.get('lastname')
    subject=session.get('subject')
    db = get_database2()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    
    action = request.form.get('action')
    weeks = cursor.fetchall()
    weeklen=len(weeks)
    weekval=[]
    weeks_subjects = {}

    for i in range(1,weeklen+1):
        weekval.append('week'+str(i))
 #get class
    if len(weekval)!=0:
        cursor.execute("select class from week1")
        classval=[row[0] for row in cursor.fetchall()]
        for i in range(1,weeklen+1):
            table_name = f"week{i}"            
            cursor.execute("select subject from "+table_name)
            subjectval=[row[0] for row in cursor.fetchall()]
            weeks_subjects[table_name] = subjectval

    
    class_count=len(classval)
            
    db=get_database2()
    cursor = db.cursor()
    # Assuming the table name is "week1"
    cursor.execute("SELECT * FROM week1")
    sessions = cursor.fetchall()

    cursor.close()
    print(username,firstname,lastname)
    # Close the cursor and MySQL connection
    

    return render_template('student-incharge.html', icon1=icon1, username=username, firstname=firstname, lastname=lastname,subject=subject, weeks=weekval, classval=classval, weeks_subjects=weeks_subjects, class_count=class_count, sessions=sessions,bg=background)


@app.route('/student')
def student():
    
    username = session.get('email')  # Retrieve the username from the session
    name = session.get('name') 
    rollno = session.get('rollno')
    class_name=session.get('class_name')

    # Execute the SQL query to fetch the timetable data
    db = get_database2()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    
    action = request.form.get('action')
    weeks = cursor.fetchall()
    weeklen=len(weeks)
    weekval=[]
    weeks_subjects = {}

    for i in range(1,weeklen+1):
        weekval.append('week'+str(i))
 #get class
    if len(weekval)!=0:
        cursor.execute("select class from week1")
        classval=[row[0] for row in cursor.fetchall()]
        for i in range(1,weeklen+1):
            table_name = f"week{i}"            
            cursor.execute("select subject from "+table_name)
            subjectval=[row[0] for row in cursor.fetchall()]
            weeks_subjects[table_name] = subjectval

    
    class_count=len(classval)
            
    db=get_database2()
    cursor = db.cursor()
    # Assuming the table name is "week1"
    cursor.execute("SELECT * FROM week1")
    sessions = cursor.fetchall()

    cursor.close()
    # Close the cursor and MySQL connection
    


    return render_template('student.html', icon=icon1, username=username,  firstname=name, rollno=rollno,class_name=class_name,weeks=weekval, classval=classval, weeks_subjects=weeks_subjects, class_count=class_count, sessions=sessions,bg=background)



#add attendance
@app.route('/add-attendance', methods=['GET', 'POST'])
def add_attendance():
    if request.method == 'POST':
        Class_name= request.form["Class_name"]
        session_count = request.form["session_count"]
        session1_attendance = request.form["session1_attendance"]
        session2_attendance = request.form["session2_attendance"]
        session3_attendance = request.form["session3_attendance"]
        test_above80 = request.form["test_above80"]
        test_above50 = request.form["test_above50"]
        test_above30 = request.form["test_above30"]
        test_below30 = request.form["test_below30"]
        test_below20 = request.form["test_below20"]
        weekval=request.form["week_name"]
        cnx = cnx_pool.get_connection()

        cursor = cnx.cursor()
        sql = "INSERT INTO attendance (Class_name, session_count, session1_attendance, session2_attendance, session3_attendance, test_above80,test_above50,test_above30, test_below30, test_below20,week) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
        val = (Class_name, session_count, session1_attendance, session2_attendance, session3_attendance, test_above80,test_above50,test_above30, test_below30, test_below20,weekval)
        cursor.execute(sql, val)
        cnx.commit()
        return redirect('/student_in_charge')

    return render_template('addattendance.html')



#FOR UPLOADING PPT

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        ppt = request.files['ppt']
        description = request.form['description']
        class_name = request.form['class_name']
        dir='COURSE/'
        subdir=dir+class_name+'/'
        if not os.path.exists(subdir):
            os.makedirs(subdir)
            ppt.save(subdir + ppt.filename)

            print("Directory  created successfully.")
        else:
            ppt.save(subdir + ppt.filename)
            print("Directory ' already exists.")
        # Save the file to the database
        cnx = cnx_pool.get_connection()
        cursor = cnx.cursor()
        cursor.execute('INSERT INTO ppt_table (ppt, description, class_name ) VALUES (%s, %s, %s)', (ppt.filename, description, class_name))
        cnx.commit()
        return redirect('/student_in_charge')
    return render_template('Ppt-upload.html')   


@app.route('/assignment', methods=['GET', 'POST'])
def assignment():
    # Establish a connection to your MySQL database
    connection = mysql.connector.connect(
        host='localhost',
        database='aptivision2',
        user='root',
        password=''
    )

    cursor = connection.cursor()

    # Execute a query to fetch the data from the database
    cursor.execute("SELECT  ppt, description, class_name FROM ppt_table")

    # Fetch all the rows returned by the query
    assignments = cursor.fetchall()

    # Close the cursor and the database connection
    cursor.close()
    

    # Render the 'assignment.html' template and pass the assignments data
    return render_template('assignment.html', assignments=assignments)


@app.route('/uploads/<path:filename>')
def display_file(filename):
    target_directories = [
        r"C:\Users\asus\OneDrive\Desktop\APTIVISION\COURSE\I BCA A",
        r"C:\Users\asus\OneDrive\Desktop\APTIVISION\COURSE\II BCA A",
        r"C:\Users\asus\OneDrive\Desktop\APTIVISION\COURSE\III BCA A",
        r"C:\Users\asus\OneDrive\Desktop\APTIVISION\COURSE\I BCA B",
        r"C:\Users\asus\OneDrive\Desktop\APTIVISION\COURSE\II BCA B",
        r"C:\Users\asus\OneDrive\Desktop\APTIVISION\COURSE\III BCA B",
        
    ]

    # Iterate over the target directories and find the file
    for target_directory in target_directories:
        file_path = os.path.join(target_directory, filename)
        if os.path.isfile(file_path):
            return send_file(file_path)

    return "File not found"





@app.route('/conduct_test', methods=['GET', 'POST'])
def conduct_test():
    return render_template('Conduct-Test.html',bg=background)


@app.route('/store_test', methods=['POST'])
def store_test():
    if request.method == 'POST':
        class_name = request.form['class']
        subject = request.form['subject']
        due_date=request.form['due_date']

        # Store the data in the MySQL database table
        cur = mydb.cursor()
        cur.execute("INSERT INTO test (class, subject,due_date,count) VALUES (%s, %s,%s,0)", (class_name, subject,due_date))
        mydb.commit()

        return redirect('/student_in_charge')
@app.route("/attend_test", methods=['GET', 'POST'])
def attend_test():
    class_name = request.args.get('class_name')
    rollno = request.args.get('rollno')
    cur = mydb.cursor()
    cur.execute("SELECT roll FROM students WHERE roll = %s", (rollno,))
    existing_rollno = cur.fetchone()
    cur.fetchall()  # Consume and discard unread results
    
    if existing_rollno:
        # Roll number already exists, do not insert a new value
        cur.close()
    else:
        # Roll number does not exist, insert a new value in the students table
        cur.execute("INSERT INTO students (roll) VALUES (%s)", (rollno,))
        mydb.commit()
        cur.close()
    
    print(rollno)
    return render_template("attend_test.html",bg=background,class_name=class_name,rollno=rollno)


@app.route("/questions", methods=['POST'])
def questions():
    
    class_name = request.form['class_name']
    rollno = request.form['rollno']
    # Check if the roll number already exists in the students table
    

    subjects = get_subjects(class_name)
    return render_template("questions.html",class_name=class_name, subjects=subjects,rollno=rollno,bg=background)


@app.route('/submit_test', methods=['POST'])
def submit_test():
    if request.method == 'POST':
        class_name = request.form['class_name']
        subject = request.form['subject']
        rollno=request.form['rollno']
        

        # Update the count column for the specified class and subject
        cur = mydb.cursor()
        cur.execute("UPDATE test SET count = count + 1 WHERE class = %s AND subject = %s", (class_name, subject))
        cur.execute('UPDATE students SET ' + subject + ' = "submitted" WHERE rollno = "' + rollno + '"')
        mydb.commit()
        cur.close()

        return redirect('/student')


@app.route('/practice', methods=['GET', 'POST'])
def practice():
    return render_template('practice.html',bg=background)

@app.route('/praquantitative', methods=['GET', 'POST'])
def praquantitative():
    return render_template('praquantitative.html',bg=background)
@app.route('/pralogical', methods=['GET', 'POST'])
def pralogical():
   
    return render_template('pralogical.html',bg=background)


@app.route('/praenglish', methods=['GET', 'POST'])
def praenglish():
    
    return render_template('praenglish.html',bg=background)

@app.route('/notifications')
def notifications():
    cursor=mydb.cursor()
    cursor.execute("SELECT * from notification")
    res=cursor.fetchall()
    return render_template("notifications.html",res=res,bg=background)

#mock interview
def load_interview_data(file_path):
    with open(file_path, 'r') as file:
        interview_data = json.load(file)
    return interview_data
@app.route('/mock')
def mock():
    interview_data = load_interview_data("interview_data.json")
    # Iterate through each question
    questions = []
    sample_answers = []
    # Iterate through each question
    for question_data in interview_data:
        question = question_data["question"]
        answers = question_data["sample_answers"]

        # Append question to the list of questions
        questions.append(question)

        # Append answers to the list of sample answers
        sample_answers.append(answers)
    questionlen = len(questions)
    return render_template('index.html', questionlen=questionlen, questions=questions, sample_answers=sample_answers,bg=background)


@app.route('/start_interview')
def start_interview():
    return render_template("interview.html")


@app.route('/submit', methods=['POST'])
def submit_answers():
    answers = request.form.getlist('answer[]')
    interview_data = load_interview_data("interview_data.json")
    success_rates = []

    # Compare user's answers with sample answers for each question
    for i, question_data in enumerate(interview_data):
        sample_answers = question_data["sample_answers"]

        if i < len(answers):
            user_answer = answers[i]
        else:
            user_answer = ""

        if len(sample_answers) > 0:
            success_rate = max(fuzz.ratio(user_answer.lower(), sample_answer.lower()) for sample_answer in sample_answers)
        else:
            success_rate = 0

        success_rates.append(success_rate)

    # Calculate the average success rate
    average_success_rate = sum(success_rates) / len(success_rates)

    # Return the average success rate as a response
    response = {'average_success_rate': average_success_rate}
    return jsonify(response)


@app.route('/result')
def result():
    interview_data = load_interview_data("interview_data.json")
    sample_answers = []
    for question_data in interview_data:
        sampleanswer = question_data["sample_answers"]
        sample_answers.append(sampleanswer)
    answers = request.args.get('answers')
    answers = json.loads(answers) if answers else []

    success_rates = []
    # Compare user's answers with sample answers for each question
    for answer, sample_answer_list in zip(answers, sample_answers):
        if len(sample_answer_list) > 0:
            success_rate = max(fuzz.ratio(answer.lower(), sample_answer.lower()) for sample_answer in sample_answer_list)
        else:
            success_rate = 0
        success_rates.append(success_rate)

    # Calculate the average success rate
    success = round(sum(success_rates) / 3,2)

    return render_template('interview.html', answers=answers, success=success,bg=background)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
  return render_template('EditProfile1.html', bg1=icon, back=background, icon1=icon, profile1=logo1)


@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        username2 = request.form['username2']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        # Check if a file was uploaded
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            # Check if the file has a valid extension
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(filename)
            else:
                # Invalid file extension
                return "INVALID FILE FORMAT!!. Only JPG and PNG files are allowed."
        else:
            filename = ''

        # Update the user credentials in the database
        cursor = cnx.cursor()
        try:
            if filename:
                cursor.execute("UPDATE user_credentials SET username=%s, first_name=%s, last_name=%s, profile_picture=%s WHERE username=%s", (username2, first_name, last_name, filename, username2))
            else:
                cursor.execute("UPDATE user_credentials SET username=%s, first_name=%s, last_name=%s WHERE username=%s", (username2, first_name, last_name, username2))
            cnx.commit()
        except:
            print("error")

        # Redirect to the placement head page after profile editing
        return redirect(url_for('student_in_charge', username2=username2, profile_picture=filename, first_name=first_name, last_name=last_name, bg1=icon))

    return render_template('EditProfile1.html', bg1=icon, back=background, icon1=icon, profile1=icon1)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
if __name__ == '__main__':
    app.debug = True
    app.run()
