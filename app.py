from flask import Flask,render_template,request,session,redirect
from mysql import connector
import random
import os
from datetime import datetime
from flask_mail import Mail, Message
from pyngrok import ngrok
# import requests
# from twilio.rest import Client

app = Flask(__name__)
app.secret_key = os.urandom(24)
conn = connector.connect(
    host="localhost",
    user="root",
    password="soham",
    database="loan"
)
# ----------------------------home--------------------------------------
cursor = conn.cursor()
@app.route('/')
def lg():
    return render_template("log.html")

@app.route('/home')
def home():
    return render_template("home.html")


@app.route('/reg', methods = ['GET'])
def reg():
    return render_template('reg.html')    

@app.route('/login', methods = ['GET'])
def log():
    return render_template('web.html')



# ----------------------------login--------------------------------------

@app.route('/login',methods=['POST'])
def login():

    mobile = request.form['mobile']
    id = request.form['id']
    password = request.form['password']

    cursor.execute("SELECT * FROM us WHERE mobile_no=%s AND id=%s AND password=%s",(mobile,id,password))
    result = cursor.fetchone()

    if result:
        session['user_id']=id
        return render_template('dashboard.html',user=id)
    else:
        error = "Check id,phone no,password"
        return render_template('web.html',error = error)

# ----------------------------register--------------------------------------

@app.route('/register',methods=['POST'])
def register():

    name = request.form['name']
    mobile = request.form['mobile']
    password = request.form['password']

    id = random.randint(1,1000)
    cursor.execute("SELECT * FROM us WHERE mobile_no=%s",(mobile,))
    result = cursor.fetchone()

    if result:
        return "Mobile no already exist"
        
    else:
        sql="INSERT INTO us(name,mobile_no,password,id) VALUES(%s,%s,%s,%s)"
        cursor.execute(sql,(name,mobile,password,id))

        conn.commit()
        
    session['user_id']=id
    return render_template("success.html",user_id = id)

# ----------------------------form template--------------------------------------
    
@app.route('/form', methods=['GET'])
def form():
    return render_template("form.html")

# ----------------------------dashboard--------------------------------------

@app.route('/dashboard')
def loan1():
    user = session.get('user_id')
    return render_template("dashboard.html",user=user)

# ----------------------------loan template--------------------------------------

@app.route('/loan', methods=['GET'])
def loan_page():
    return render_template("loan.html")

# ----------------------------bank template--------------------------------------

@app.route('/bankp')
def bank1():
    user_id = request.args.get('user')
    return render_template("bankp.html")

# ----------------------------appication form--------------------------------------

@app.route('/application', methods=['POST'])
def application():
    error = None
    id = request.form['id']
    addhar_no = request.form['addhar_no']
    
    # ✅ VALIDATION HERE
    if not addhar_no or len(addhar_no) != 12 or not addhar_no.isdigit():
        error="Invalid Aadhar Number"
        return render_template("form.html", error=error)

    # rest of your code
    F_name = request.form['F_name']
    M_name = request.form['M_name']
    L_name = request.form['L_name']
    age = request.form['age']
    gender = request.form['gender']
    Email = request.form['Email']
    Village = request.form['Village']
    taluka = request.form['taluka']
    district = request.form['district']
    state = request.form['state']
    pincode = request.form['pincode']
    occupation = "FARMER"
    mobile_no = request.form['mobile_no']
    annual_income = request.form['annual_income']

    sql = """INSERT INTO application(user_id,F_name,M_name,L_name,age,gender,Email,
            Village,taluka,district,state,pincode,addhar_no,occupation,mobile_no,annual_income)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    cursor.execute(sql,(id,F_name,M_name,L_name,age,gender,Email,
                        Village,taluka,district,state,pincode,addhar_no,
                        occupation,mobile_no,annual_income))

    conn.commit()

    return render_template("dashboard.html", user=id)

    
# ----------------------------loan form--------------------------------------

# @app.route("/application_form")
# def appli():
#     return render_template('.html')

@app.route("/application_form", methods = ['GET','POST'])
def application_from():
    id = session.get('user_id')
    sql = "select a.user_id,a.F_name,a.M_name,a.L_name,a.age,a.gender,a.Email,a.Village,a.taluka,a.district,a.state,a.pincode,a.addhar_no,a.occupation,a.mobile_no,a.annual_income from application a where user_id=%s"
    cursor.execute(sql,(id,))
    result = cursor.fetchone()
    return render_template('application_form.html',data=result)
    
# ----------------------------bank form--------------------------------------    

@app.route('/dbank', methods = ['POST'])
def dbank():
    id = session.get('user_id')
    if not id:
        return "Login first"
    account_no = request.form['account_no']
    con_account_no = request.form['con_account_no']
    ifsc = request.form['ifsc']
    bank_name = request.form['bank_name']
    
    cursor.execute("select id from us where id=%s",(id,))
    result = cursor.fetchone()
    if con_account_no==account_no and len(ifsc)==11 and result :
        
        sql = "INSERT INTO bank(Account_number,IFSC,bank_name,id) VALUES(%s,%s,%s,%s)"
        cursor.execute(sql,(con_account_no,ifsc,bank_name,id))
        conn.commit()
        return render_template('dashboard.html',user = id)
    # else:
    #     return "check account no and other details"

# ----------------------------loan form--------------------------------------

@app.route('/loan',methods=['POST'])
def loan():
    id = request.form['id']
    loan_type = request.form['loan_type']
    amount = request.form['amount']
    duration = request.form['duration']
    pay = request.form['pay']
    date = datetime.now().strftime('%d-%m-%Y')
    address = request.form['upi_id']
    address2 = request.form['wallet_address']
    
    cursor.execute('select id from us where id=%s',(id,))
    result = cursor.fetchone()
    
    if not result:
        print("Incorrect id please check id")
    # else:
    sql = "INSERT INTO loan_t(id,loan_type,amount,duration,payment_method,date,upi,digital_wallet) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql,(id,loan_type,amount,duration,pay,date,address,address2))
    conn.commit()
    return render_template("dashboard.html",user=id)

# ----------------------------pending loan--------------------------------------

@app.route('/ploan')
def table():
    id = session.get('user_id')
    if not id:
        return redirect('/')
    sql = "select l.id,l.amount,l.duration,l.payment_method,l.date from loan_t l join us u on l.id=u.id where l.id=%s"
    cursor.execute(sql,(id,))
    fetch = cursor.fetchall()
    return render_template('ploan.html', loans=fetch,userid = id)
    
# -----------------------------status part------------------------------------
@app.route('/status_s')
def status():
    id = session.get('user_id')
    if not id:
        return redirect('/')
    sql = "select l.id,l.amount,l.duration,l.payment_method,l.date,l.status from loan_t l join us u on l.id=u.id where l.id=%s"
    cursor.execute(sql,(id,))
    fetch = cursor.fetchall()
    return render_template('status_s.html', loans=fetch,userid = id)


from datetime import datetime

@app.route('/pay')
def pay():
    id = session.get('user_id')

    if not id:
        return redirect('/')
    sql = """
    SELECT l.id,l.amount,l.duration,l.payment_method,
    l.date,l.status
    FROM loan_t l
    JOIN us u ON l.id=u.id
    WHERE l.id=%s
    """

    cursor.execute(sql,(id,))
    result = cursor.fetchall()

    updated_data = []

    for row in result:

        loan_id = row[0]
        amount = int(row[1])
        duration = int(row[2])
        method = row[3]
        loan_date = row[4]
        status = row[5]

        interest = amount * (5/100)*duration


        start_date = datetime.strptime(loan_date, "%d-%m-%Y")
        print(start_date)

        current_date = datetime.now()

        months_passed = (
            (current_date.year - start_date.year) * 12
            + (current_date.month - start_date.month)
        )

        
        remaining_months = duration - months_passed

        if remaining_months < 0:
            remaining_months = 0

        updated_data.append((
            loan_id,
            amount,
            remaining_months,
            method,
            loan_date,
            status,
            interest
        ))

    return render_template('pay.html',data=updated_data)

@app.route('/payloan')
def payloan():
    return render_template('payloan.html')

# -----------------------------Admin part------------------------------------

@app.route('/admin_login', methods = ['GET'])
def log1():
    return render_template('web2.html')

#---------------------------------------login-----------------------------------------

@app.route('/admin_login',methods = ['POST'])
def login1():
    mobile = request.form['mobile']
    id = request.form['id']
    password = request.form['password']
    
    if mobile!=9834425593 and id!=9556 and password!='Soham@999':
        error = "Admin Details Are Wrong"
        return render_template("web2.html",error = error)
    else:
        return redirect('/Admin')
    
# --------------------------------------admin route-----------------------------------

@app.route('/Admin')
def admin_dashboard():
    query = """
    SELECT l.loan_id,l.id, u.name, l.loan_type, l.amount, l.duration, l.status 
    FROM loan_t l 
    JOIN us u ON l.id = u.id
    """
    cursor.execute(query)
    loans = cursor.fetchall()  

    return render_template('Admin.html', loans=loans)

# --------------------------------------status route-----------------------------------

@app.route('/update_status/<int:loan_id>/<string:status>')
def update_status(loan_id, status):
    sql = "UPDATE loan_t SET status=%s WHERE loan_id=%s"
    cursor.execute(sql, (status, loan_id))
    conn.commit()
    return redirect('/Admin')

# --------------------------------------pending loan table route-----------------------------------

@app.route("/table")
def check_pending():
    sql = "select l.id,l.loan_type,l.amount,l.duration,l.payment_method,status from loan_t l join us u on u.id=l.id"
    cursor.execute(sql)
    result = cursor.fetchall()
    return render_template("table.html",data=result)


# ----------------------------mail otp server run--------------------------------------


app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='sohamsalunkhe615@gmail.com',
    MAIL_PASSWORD='umsg ineb hkeh vxcl'
)
mail = Mail(app)


def generate_otp():
    return str(random.randint(100000, 999999))

@app.route('/verification',methods = ['GET'])
def send_otp_page():
    return render_template("verification.html")

@app.route('/verification',methods = ['POST'])
def send_otp():
    email = request.form['email']   
    otp = generate_otp()

    session['otp'] = otp
    session['email'] = email

    msg = Message(
        'Your OTP Code',
        sender='sohamsalunkhe615@gmail.com',
        recipients=[email]
    )

    msg.body = f'Your OTP is: {otp}'
    mail.send(msg)

    return render_template('send.html', email=email)



@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    user_otp = request.form['otp']
    email = session.get('email')
    us_id = request.form['id']
    sql = "select password from us where id=%s"
    cursor.execute(sql,(us_id,))
    result = cursor.fetchone()
    if user_otp == session.get('otp'):
        msg = Message(
            "YOUR PASSWORD IS",
            sender='sohamsalunkhe615@gmail.com',
            recipients=[email]
        )
        msg.body = f'Your Password is: {result[0]}'
        mail.send(msg)
        
        return "OTP Verified "
    else:
        return "Invalid OTP "

# -----------------------------------id mail server------------------------------------    
    
@app.route('/showid',methods = ['GET'])
def send():
    return render_template("shoid.html")

@app.route('/showid',methods = ['POST'])
def otp():
    email = request.form['email']   
    otp = generate_otp()

    session['otp'] = otp
    session['email'] = email

    msg = Message(
        'Your OTP Code',
        sender='sohamsalunkhe615@gmail.com',
        recipients=[email]
    )

    msg.body = f'Your OTP is: {otp}'
    mail.send(msg)

    return render_template('verify.html', email=email)



@app.route('/verify', methods=['POST'])
def verify():
    user_otp = request.form['otp']
    email = session.get('email')
    mobile = request.form['mobile']
    sql = "select id from us where mobile_no=%s"
    cursor.execute(sql,(mobile,))
    result = cursor.fetchone()
    if user_otp == session.get('otp'):
        msg = Message(
            "YOUR PASSWORD IS",
            sender='sohamsalunkhe615@gmail.com',
            recipients=[email]
        )
        res = result[0]
        msg.body = f'Your ID is: {res}'
        mail.send(msg)
        
        return render_template("web.html") 
    else:
        return "Invalid OTP ❌"
    
# -----------------------------------delete loans------------------------------------    
    
    
@app.route('/delete_loan/<int:loan_id>')
def delete_loan(loan_id):
    cursor.execute("DELETE FROM loan_t WHERE loan_id=%s", (loan_id,))
    conn.commit()
    return redirect('/Admin')

# -----------------------------------app run server------------------------------------    
    
if __name__ == "__main__":
    

    ngrok.set_auth_token("2MurYZqkx7p63nJQ6D5Tfugg65I_58L9zuQhmuyRrN4njnbuu")
    public_url = ngrok.connect(5000)
    print("Public URL:", public_url)

    app.run(host="0.0.0.0", port=5000,debug=True)