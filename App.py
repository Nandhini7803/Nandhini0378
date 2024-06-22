from flask import Flask, render_template, flash, request, session, send_file
from flask import render_template, redirect, url_for, request
from werkzeug.utils import secure_filename
import mysql.connector
import sys
from ecies.utils import generate_key
from ecies import encrypt, decrypt
import base64, os
import pickle
import numpy as np
from keras.preprocessing import image

app = Flask(__name__)
app.config['DEBUG']
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


@app.route("/")
def homepage():
    return render_template('index.html')


@app.route("/Home")
def Home():
    return render_template('index.html')


@app.route("/OwnerLogin")
def OwnerLogin():
    return render_template('OwnerLogin.html')


@app.route("/NewDoctor")
def NewDoctor():
    return render_template('NewDoctor.html')


@app.route("/DoctorLogin")
def DoctorLogin():
    return render_template('DoctorLogin.html')


@app.route("/NewOwner")
def NewOwner():
    return render_template('NewOwner.html')


@app.route("/AdminLogin")
def AdminLogin():
    return render_template('AdminLogin.html')


@app.route("/UploadDataSet")
def UploadDataSet():
    return render_template('UploadDataSet.html')


@app.route("/UserLogin")
def UserLogin():
    return render_template('UserLogin.html')


@app.route("/NewUser")
def NewUser():
    return render_template('NewUser.html')


@app.route("/Cancer")
def Cancer():
    return render_template('Cancer.html')


@app.route("/Diabetes")
def Diabetes():
    return render_template('Diabetes.html')


@app.route("/Heart")
def Heart():
    return render_template('Heart.html')


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    error = None
    if request.method == 'POST':
        if request.form['uname'] == 'admin' and request.form['password'] == 'admin':

            conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
            # cursor = conn.cursor()
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb ")
            data = cur.fetchall()
            return render_template('AdminHome.html', data=data)

        else:

            alert = 'Username or Password is wrong'
            return render_template('goback.html', data=alert)


@app.route("/AdminHome")
def AdminHome():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb ")
    data = cur.fetchall()
    return render_template('AdminHome.html', data=data)


@app.route("/OwnerInfo")
def OwnerInfo():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM ownertb ")
    data = cur.fetchall()
    return render_template('OwnerInfo.html', data=data)


@app.route("/UploadDataset")
def UploadDataset():
    return render_template('ViewExcel.html')


@app.route("/AdminUserInfo")
def AdminUserInfo():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    # cursor = conn.cursor()
    cur = conn.cursor()
    cur.execute("SELECT * FROM doctortb ")
    data = cur.fetchall()

    return render_template('AdminUserInfo.html', data=data)


@app.route("/AdminAssignInfo")
def AdminAssignInfo():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    # cursor = conn.cursor()
    cur = conn.cursor()
    cur.execute("SELECT * FROM drugtb ")
    data = cur.fetchall()

    return render_template('AdminAssignInfo.html', data=data)


@app.route("/doclogin", methods=['GET', 'POST'])
def doclogin():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['password']
        session['dname'] = request.form['uname']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from ownertb where username='" + username + "' and Password='" + password + "'")
        data = cursor.fetchone()
        if data is None:

            data1 = 'Username or Password is wrong'
            return render_template('goback.html', data=data1)


        else:
            print(data[0])
            session['uid'] = data[0]
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM ownertb where username='" + username + "' and Password='" + password + "'")
            data = cur.fetchall()

            return render_template('OwnerHome.html', data=data)


@app.route("/uploadModel", methods=['GET', 'POST'])
def uploadModel():
    if request.method == 'POST':

        name1 = session['dname']
        typ = request.form['typ']
        file = request.files['fileupload']
        file.save("static/upload/" + file.filename)

        secp_k = generate_key()
        privhex = secp_k.to_hex()
        pubhex = secp_k.public_key.format(True).hex()

        filepath = "./static/upload/" + file.filename
        head, tail = os.path.split(filepath)

        newfilepath1 = './static/Encrypt/' + str(tail)
        newfilepath2 = './static/Decrypt/' + str(tail)

        data = 0
        with open(filepath, "rb") as File:
            data = base64.b64encode(File.read())  # convert binary to string data to read file

        print("Private_key:", privhex, "\nPublic_key:", pubhex, "Type: ", type(privhex))

        if (privhex == 'null'):
            alert = 'Please Choose Another File,file corrupted!'
            return render_template('goback.html', data=alert)

        else:

            print("Binary of the file:", data)
            encrypted_secp = encrypt(pubhex, data)
            print("Encrypted binary:", encrypted_secp)

            with open(newfilepath1, "wb") as EFile:
                EFile.write(base64.b64encode(encrypted_secp))
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO  modeltb VALUES ('','" + name1 + "','" + typ + "','" + file.filename + "','" + pubhex + "','" + privhex + "')")
            conn.commit()
            conn.close()
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
            # cursor = conn.cursor()
            cur = conn.cursor()
            cur.execute("SELECT * FROM modeltb where ownerName='" + name1 + "' ")
            data = cur.fetchall()
            return render_template('UploadInfo.html', data=data)


@app.route("/UploadInfo")
def UploadInfo():
    name1 = session['dname']
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM modeltb where ownerName='" + name1 + "' ")
    data = cur.fetchall()
    return render_template('UploadInfo.html', data=data)


@app.route("/UploadModel")
def UploadModel():
    return render_template('UploadModel.html')


@app.route("/RequestInfo")
def RequestInfo():
    name1 = session['dname']
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM requesttb where ownerName='" + name1 + "' ")
    data = cur.fetchall()
    return render_template('RequestInfo.html', data=data)


@app.route('/Accept')
def Accept():
    id = request.args.get('id')
    session['id'] = id
    name1 = session['dname']

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cursor = conn.cursor()
    cursor.execute("SELECT  *  FROM requesttb where  id='" + session['id'] + "'  ")
    data = cursor.fetchone()
    if data:
        username = data[1]
        Prikey = data[5]

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cursor = conn.cursor()
    cursor.execute("SELECT  *  FROM regtb  where  username='" + username + "'  ")
    data = cursor.fetchone()
    if data:
        mail = data[3]
        print(mail)
        sendmail(mail, "Id " + session['id'] + "  Prikey " + str(Prikey))

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cursor = conn.cursor()
    cursor.execute(
        "update  requesttb set status='Accept' where Id='" + session['id'] + "'")
    conn.commit()
    conn.close()

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM requesttb where ownerName='" + name1 + "' ")
    data = cur.fetchall()

    return render_template('RequestInfo.html', data=data)


@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        name1 = request.form['name']
        gender1 = request.form['gender']
        Age = request.form['age']
        email = request.form['email']
        pnumber = request.form['phone']
        address = request.form['address']

        uname = request.form['uname']
        password = request.form['psw']
        loc = request.form['loc']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO regtb VALUES ('" + name1 + "','" + gender1 + "','" + Age + "','" + email + "','" + pnumber + "','" + address + "','" + uname + "','" + password + "','" + loc + "')")
        conn.commit()
        conn.close()
        # return 'file register successfully'

    return render_template('UserLogin.html')


@app.route("/newdoctor", methods=['GET', 'POST'])
def newdoctor():
    if request.method == 'POST':
        name1 = request.form['name']
        gender1 = request.form['gender']
        Age = request.form['age']
        email = request.form['email']
        pnumber = request.form['phone']
        address = request.form['address']
        special = request.form['special']
        loc = request.form['loc']

        uname = request.form['uname']
        password = request.form['psw']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ownertb VALUES ('" + name1 + "','" + gender1 + "','" + Age + "','" + email + "','" + pnumber + "','" + address + "','" + special + "','" + uname + "','" + password + "','" + loc + "')")
        conn.commit()
        conn.close()

    data1 = 'Record Saved'
    return render_template('goback.html', data=data1)


@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    error = None
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['password']
        session['uname'] = request.form['uname']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username='" + username + "' and Password='" + password + "'")
        data = cursor.fetchone()
        if data is None:

            data1 = 'Username or Password is Incorrect!'
            return render_template('goback.html', data=data1)



        else:
            print(data[0])
            session['uid'] = data[0]
            mob = data[4]
            email = data[3]

            import random
            n = random.randint(1111, 9999)

            sendmsg(mob, "Your OTP" + str(n))
            sendmail(email, "Your OTP" + str(n))

            session['otp'] = str(n)
            return render_template('OTP.html', data=data)


@app.route("/otplogin", methods=['GET', 'POST'])
def otplogin():
    error = None
    if request.method == 'POST':
        username = request.form['uname']

        if session['otp'] == username:

            username1 = session['uname']
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb where username='" + username1 + "'")
            data = cur.fetchall()

            return render_template('UserHome.html', data=data)

        else:

            data1 = 'OTP is Incorrect!'
            return render_template('goback.html', data=data1)



@app.route('/UserHome')
def UserHome():
    username1 = session['uname']
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb where username='" + username1 + "'")
    data = cur.fetchall()

    return render_template('UserHome.html', data=data)

@app.route("/UModelInfo", methods=['GET', 'POST'])
def UModelInfo():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    # cursor = conn.cursor()
    cur = conn.cursor()
    cur.execute("SELECT * FROM modeltb ")
    data = cur.fetchall()
    return render_template('UModelInfo.html', data=data)


@app.route('/SendRequest')
def SendRequest():
    id = request.args.get('id')
    session['id'] = id

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cursor = conn.cursor()
    cursor.execute("SELECT  *  FROM modeltb where  id='" + session['id'] + "'  ")
    data = cursor.fetchone()

    if data:
        Ownername = data[1]
        type = data[2]
        Model = data[3]
        Privkey = data[5]

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO  requesttb VALUES ('','" + session[
            'uname'] + "','" + Ownername + "','" + type + "','" + Model + "','" + Privkey + "','waiting')")
    conn.commit()
    conn.close()

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM requesttb where UserName='" + session['uname'] + "' ")
    data = cur.fetchall()

    return render_template('URequestInfo.html', data=data)


@app.route('/URequestInfo')
def URequestInfo():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM requesttb where UserName='" + session['uname'] + "' ")
    data = cur.fetchall()

    return render_template('URequestInfo.html', data=data)


@app.route('/Decrypt')
def Decrypt():
    id = request.args.get('id')
    session['id'] = id
    st = request.args.get('st')

    if st == "Accept":
        return render_template('Decrypt.html')
    else:
        data1 = 'Waiting For  Owner Approved! '
        return render_template('goback.html', data=data1)


@app.route("/decryt", methods=['GET', 'POST'])
def decryt():
    if request.method == 'POST':

        keys = request.form['keys']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
        cursor = conn.cursor()
        cursor.execute("SELECT  *  FROM requesttb where  id='" + session['id'] + "' and PriKey='" + keys + "' ")
        data = cursor.fetchone()

        if data:
            typ = data[3]
            prkey = data[5]
            fname = data[4]
            session['oname'] = data[2]

            privhex = prkey

            filepath = "./static/Encrypt/" + fname
            head, tail = os.path.split(filepath)

            newfilepath1 = './static/Encrypt/' + str(tail)
            newfilepath2 = './static/Decrypt/' + str(tail)

            data = 0
            with open(newfilepath1, "rb") as File:
                data = base64.b64decode(File.read())

            print(data)
            decrypted_secp = decrypt(privhex, data)
            print("\nDecrypted:", decrypted_secp)
            with open(newfilepath2, "wb") as DFile:
                DFile.write(base64.b64decode(decrypted_secp))

            session['ptype'] = typ

            if typ == "Kidney":
                return render_template('Predict.html',model=typ)
            elif typ == "Liver":
                return render_template('Predict.html',model=typ)
            elif typ == "Lung":
                return render_template('Predict.html',model=typ)
        else:

            data1 = 'Key Incorrect! '
            return render_template('goback.html', data=data1)


@app.route("/predict", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        username = session['uname']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username='" + username + "' ")
        data = cursor.fetchone()
        if data is None:

            data1 = 'Username or Password is Incorrect!'
            return render_template('goback.html', data=data1)



        else:
            print(data[0])
            session['uid'] = data[0]
            mob = data[4]
            email = data[3]



        if session['ptype'] == "Lung":
            import tensorflow as tf
            import cv2

            file = request.files['file']
            file.save('static/upload/Test.png')
            fname = 'static/upload/Test.png'
            img1 = cv2.imread('static/upload/Test.png')
            dst = cv2.fastNlMeansDenoisingColored(img1, None, 10, 10, 7, 21)
            noi = 'static/upload/noi.png'

            cv2.imwrite(noi, dst)

            import warnings
            warnings.filterwarnings('ignore')

            classifierLoad = tf.keras.models.load_model('lungmodel.h5')
            test_image = image.load_img('static/upload/Test.png', target_size=(200, 200))
            test_image = np.expand_dims(test_image, axis=0)
            result = classifierLoad.predict(test_image)
            print(result)
            ind = np.argmax(result)
            out = ''

            if ind == 0:
                out = 'Covid'
                session['Ans'] = 'yes'
            elif ind == 1:
                out = 'Influenza'
                session['Ans'] = 'yes'
            elif ind == 2:
                out = 'Normal'
                session['Ans'] = 'No'
            elif ind == 3:
                out = 'Pneumonia'
                session['Ans'] = 'yes'
            elif ind == 4:
                out = 'Tuberculosis'
                session['Ans'] = 'yes'


            if session['Ans'] == 'yes':
                sendmail(email,"You Have "+ out + "Appointment Today")

            session['out'] = out


            return render_template('Answer.html', data=out,org=fname)
        elif  session['ptype'] == "Kidney":
            import tensorflow as tf
            import cv2

            file = request.files['file']
            file.save('static/upload/Test.png')
            fname = 'static/upload/Test.png'
            img1 = cv2.imread('static/upload/Test.png')
            dst = cv2.fastNlMeansDenoisingColored(img1, None, 10, 10, 7, 21)
            noi = 'static/upload/noi.png'

            cv2.imwrite(noi, dst)

            import warnings
            warnings.filterwarnings('ignore')

            classifierLoad = tf.keras.models.load_model('kidneymodel.h5')
            test_image = image.load_img('static/upload/Test.png', target_size=(200, 200))
            test_image = np.expand_dims(test_image, axis=0)
            result = classifierLoad.predict(test_image)
            print(result)
            ind = np.argmax(result)
            out = ''

            if ind == 0:
                out = 'Cyst'
                session['Ans'] = 'yes'
            elif ind == 1:
                out = 'Normal'
                session['Ans'] = 'No'
            elif ind == 2:
                out = 'Stone'
                session['Ans'] = 'yes'
            elif ind == 2:
                out = 'Tumor'
                session['Ans'] = 'yes'

            if session['Ans'] == 'yes':
                sendmail(email,"You Have "+ out + "Appointment Today")

            session['out'] = out

            return render_template('Answer.html', data=out,org=fname)

        else:

            import tensorflow as tf
            import cv2

            file = request.files['file']
            file.save('static/upload/Test.png')
            fname = 'static/upload/Test.png'
            img1 = cv2.imread('static/upload/Test.png')
            dst = cv2.fastNlMeansDenoisingColored(img1, None, 10, 10, 7, 21)
            noi = 'static/upload/noi.png'

            cv2.imwrite(noi, dst)

            import warnings
            warnings.filterwarnings('ignore')

            classifierLoad = tf.keras.models.load_model('livermodel.h5')
            test_image = image.load_img('static/upload/Test.png', target_size=(200, 200))
            test_image = np.expand_dims(test_image, axis=0)
            result = classifierLoad.predict(test_image)
            print(result)
            ind = np.argmax(result)
            out = ''

            if ind == 0:
                out = 'Cancer'
                session['Ans'] = 'yes'
            elif ind == 1:
                out = 'Cirrhosis'
                session['Ans'] = 'yes'
            elif ind == 2:
                out = 'Liverfailure'
                session['Ans'] = 'yes'
            elif ind == 3:
                out = 'Normal'
                session['Ans'] = 'No'
            elif ind == 4:
                out = 'Portalhypertension'
                session['Ans'] = 'yes'

            if session['Ans'] == 'yes':
                sendmail(email,"You Have "+ out + "Appointment Today")

            session['out'] = out


            return render_template('Answer.html', data=out,org=fname)



@app.route("/ViewDoctor",methods=['GET', 'POST'])
def ViewDoctor():
    if session['Ans'] == 'yes':
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')

        cur = conn.cursor()
        cur.execute("SELECT * FROM doctortb")
        data = cur.fetchall()

        return render_template('UserAppointment.html', data=data)
    else:
        data1 = 'Your Are Normal!'
        return render_template('goback.html', data=data1)




@app.route("/UserAssignDrugInfo")
def UserAssignDrugInfo():
    uname = session['uname']
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM  drugtb where UserName='" + uname + "'  ")
    data = cur.fetchall()

    return render_template('UserAssignDrugInfo.html', data=data)


@app.route("/Appointment")
def Appointment():
    dusername = request.args.get('id')
    import datetime
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    uname = session['uname']
    dise = session['out']

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cursor = conn.cursor()
    cursor.execute("SELECT  *  FROM  doctortb where  UserNAme='" + dusername + "'")
    data = cursor.fetchone()

    if data:
        spec = data[6]



    else:

        return 'Incorrect username / password !'

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cursor = conn.cursor()
    cursor.execute("SELECT  *  FROM regtb where  UserNAme='" + uname + "'")
    data = cursor.fetchone()

    if data:
        mobile = data[4]
        email = data[3]


    else:

        return 'Incorrect username / password !'

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO  apptb VALUES ('','" + uname + "','" + mobile + "','" + email + "','" + dusername + "','" + date + "','" + spec + "','"+ dise  +"')")
    conn.commit()
    conn.close()

    data1 = 'Record Saved'
    return render_template('goback.html', data=data1)


@app.route('/download')
def download():
    id = request.args.get('id')

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cursor = conn.cursor()
    cursor.execute("SELECT  *  FROM drugtb where  id = '" + str(id) + "'")
    data = cursor.fetchone()
    if data:
        filename = "static\\upload\\" + data[7]

        return send_file(filename, as_attachment=True)

    else:
        return 'Incorrect username / password !'



@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        date = request.form['date']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
        # cursor = conn.cursor()
        cur = conn.cursor()
        cur.execute("SELECT * FROM assigntb where Lastdate='" + date + "'")
        data = cur.fetchall()

        return render_template('Notification.html', data=data)


def sendmsg(targetno,message):
    import requests
    requests.post(
        "http://sms.creativepoint.in/api/push.json?apikey=6555c521622c1&route=transsms&sender=FSSMSS&mobileno=" + targetno + "&text=Dear customer your msg is " + message + "  Sent By FSMSG FSSMSS")



@app.route("/newdoctor1", methods=['GET', 'POST'])
def newdoctor1():
    if request.method == 'POST':
        name1 = request.form['name']
        gender1 = request.form['gender']
        Age = request.form['age']
        email = request.form['email']
        pnumber = request.form['phone']
        address = request.form['address']
        special = request.form['special']
        loc = request.form['loc']

        uname = request.form['uname']
        password = request.form['psw']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO doctortb VALUES ('" + name1 + "','" + gender1 + "','" + Age + "','" + email + "','" + pnumber + "','" + address + "','" + special + "','" + uname + "','" + password + "','" + loc + "')")
        conn.commit()
        conn.close()

    data1 = 'Record Saved'
    return render_template('goback.html', data=data1)

@app.route("/DoctorUserInfo")
def DoctorUserInfo():
    dname = session['dname']

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    # cursor = conn.cursor()
    cur = conn.cursor()
    cur.execute("SELECT * FROM apptb where DoctorName='" + dname + "' ")
    data = cur.fetchall()

    return render_template('DoctorUserInfo.html', data=data)


@app.route("/DoctorAssignInfo")
def DoctorAssignInfo():
    dname = session['dname']

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    # cursor = conn.cursor()
    cur = conn.cursor()
    cur.execute("SELECT * FROM drugtb where DoctorName='" + dname + "' ")
    data = cur.fetchall()

    return render_template('DoctorAssignInfo.html', data=data)


@app.route("/doclogin1", methods=['GET', 'POST'])
def doclogin1():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['password']
        session['dname'] = request.form['uname']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from doctortb where username='" + username + "' and Password='" + password + "'")
        data = cursor.fetchone()
        if data is None:

            data1 = 'Username or Password is wrong'
            return render_template('goback.html', data=data1)


        else:
            print(data[0])
            session['uid'] = data[0]
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
            # cursor = conn.cursor()
            cur = conn.cursor()
            cur.execute("SELECT * FROM doctortb where username='" + username + "' and Password='" + password + "'")
            data = cur.fetchall()

            return render_template('DoctorHome.html', data=data)


@app.route("/searchid")
def searchid():
    user = request.args.get('user')
    session['user'] = user
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
    cur = conn.cursor()
    cur.execute(
        "SELECT  *  FROM apptb where  username='" + str(user) + "'")
    data = cur.fetchall()
    print(data)

    return render_template('AdminAssign.html', data=data)


@app.route("/assigndrug", methods=['GET', 'POST'])
def assigndrug():
    if request.method == 'POST':
        uname = request.form['UserName']
        phone = request.form['Phone']
        email = request.form['Email']
        dname = session['dname']
        medi = request.form['Medicine']
        other = request.form['Other']
        file = request.files['file']
        file.save("static/upload/" + file.filename)
        Adate = request.form['Adate']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO  drugtb VALUES ('','" + uname + "','" + phone + "','" + email + "','" + dname + "','" + medi + "','" + other + "','" + file.filename + "','" + Adate + "')")
        conn.commit()
        conn.close()

        # return 'file register successfully'
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1Federatedimagedb')
        # cursor = conn.cursor()
        cur = conn.cursor()
        cur.execute("SELECT * FROM drugtb where DoctorName='" + dname + "' ")
        data = cur.fetchall()

    return render_template('DoctorAssignInfo.html', data=data)

def sendmail(Mailid, message):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    fromaddr = "projectmailm@gmail.com"
    toaddr = Mailid

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Alert"

    # string to store the body of the mail
    body = message

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "qmgn xecl bkqv musr")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
