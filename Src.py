from flask import Flask,flash,render_template, Response, request, redirect, url_for,session
import random as rd
import smtplib as sp
from twilio.rest import Client
import mysql.connector
mydb=mysql.connector.connect(
host='localhost',
user='root',
password='',
database='rewards')

global i
mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM mails_phno")
myresult = mycursor.fetchall()
mycursor.execute("SELECT count(*) FROM mails_phno")
counts = mycursor.fetchall()
for (i,) in counts:
    print(i)


app=Flask(__name__)
app.secret_key = "super secret key"

otp=''
email=''
other=''
admin=0
@app.route('/')
def index():
    return render_template('login.html')
    
@app.route('/verify',methods=["post"])
def send_Eotp():
        global email
        global mob
        global other
        global admin
        global status
        email=request.form['email']
        mob=request.form['mob_no']
        if(email):
            other=email
            for (emails,phones,admin,status,eid) in myresult:
                if(emails==email):
                    global otp
                    otp=''.join([str(rd.randint(0,9)) for x in range(6)])
                    text='verification code is '+otp
                    print(text)
                    message = 'Subject: {}\n\n{}'.format('Your Single-use code ', text)
                    other=email
                    server=sp.SMTP('smtp.gmail.com',587)
                    server.starttls()
                    server.login('atulsharma7357@gmail.com','uzgmxtenubxjromw')
                    server.sendmail('atulsharma7357@gmail.com',email,message)
                    server.quit()
                    return render_template('ver.html',otp=otp,other=other,an=admin)
            return render_template('login_fail.html',other=other)
        else:
            global account_sid
            global auth_token
            global client
            global verify_sid
            other=mob
            for (emails,phones,admin,status,eid) in myresult:
                if(phones==mob):
                    account_sid = "AC36fbd0a320536e64fe66706f23262a15"
                    auth_token = "10723d18b6d918b4c690b43a0265172a"
                    verify_sid = "VAe36e41c78e5a79392856872f891f705a"
                    client = Client(account_sid, auth_token)
                    verification = client.verify.v2.services(verify_sid) \
                    .verifications \
                    .create(to='+91'+mob, channel="sms")
                    return render_template('veri1.html',verified_number ='+91'+'-'+mob)
            return render_template('login_fail.html',other=other)
@app.route('/mob_ver',methods=["post"])
def mob_no():
    otp=request.form['gt_otp']
    hel='+91'+mob
    verification_check = client.verify.v2.services(verify_sid) \
    .verification_checks\
        .create(to=hel, code=otp)
    print(verification_check.status)
    return render_template('veri2.html',vc=verification_check.status,verified_number ='+91'+'-'+mob,otp=otp)


@app.route('/back',methods=["post"])
def ind():
    return render_template('login.html')
        
        
@app.route('/rewards',methods=["post"])
def rewards_pg():
                if(admin):
                    return render_template('admin.html',other=other)
                else:
                    print(status)
                    return render_template('reward.html',email=other,status=status)

@app.route('/emp_admin',methods=["post"])
def admin_emp():
    return render_template('emp.html',other=other,mre=myresult,i=i)

@app.route('/update',methods=["post"])
def update_emp():
    newph=str(request.form['mobno'])
    mail=request.form['mail']
    role=request.form['role']
    sts=request.form['sts']
    if(newph):
        # normal role
        if(role!=1):
            mycursor.execute("UPDATE mails_phno SET phone=%s,status=%s,admin=%d WHERE email=%s;",(newph,sts,role,mail))
        else:
            sts='a'
            mycursor.execute("UPDATE mails_phno SET phone=%s, admin=%s,status=%s, WHERE email=%s;",(newph,role,sts,mail))
    else:
        if(role!=1):
            mycursor.execute("UPDATE mails_phno SET status=%s,admin=%d WHERE email=%s;",(sts,role,mail))
        else:
            sts='a'
            mycursor.execute("UPDATE mails_phno SET admin=%s,status=%s, WHERE email=%s;",(role,sts,mail))
    mydb.commit()
    mycursor.execute("SELECT * FROM mails_phno")
    myresult = mycursor.fetchall()
    flash(mail+' updated successfully')
    return render_template('emp.html',other=other,mre=myresult,i=i)

@app.route('/new_emp',methods=["post"])
def new_emp():
    newph=str(request.form['mobno'])
    mail=request.form['mail']
    role=request.form['role']
    sts=request.form['status']
    mycursor.execute("insert into mails_phno(email,phone,admin,status) values(%s, %s, %s, %s)",(mail,newph,role,sts))
    mydb.commit()
    mycursor.execute("SELECT * FROM mails_phno")
    myresult = mycursor.fetchall()
    mycursor.execute("SELECT count(*) FROM mails_phno")
    counts = mycursor.fetchall()
    for (i,) in counts:
        print(i)
    flash(mail+' inserted successfully')
    return render_template('emp.html',other=other,mre=myresult,i=i)


@app.route('/delete/<int:id_data>', methods = ['GET'])
def delete(id_data):
    data_user=id_data
    add_user = '''DELETE FROM mails_phno WHERE emp_id=%d'''%data_user
    mycursor.execute(add_user)
    mydb.commit()
    mycursor.execute("SELECT * FROM mails_phno")
    myresult = mycursor.fetchall()
    mycursor.execute("SELECT count(*) FROM mails_phno")
    counts = mycursor.fetchall()
    for (i,) in counts:
        print(i)
    flash("Record Has Been Deleted Successfully")
    return render_template('emp.html',other=other,mre=myresult,i=i)
    
    

if __name__ == "__main__":
    app.run(debug=True,port=8150)