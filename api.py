from flask import Flask, render_template, url_for, flash, redirect, request, json, jsonify
import mysql.connector
from flask_mysqldb import MySQL


#creating an instance of the Flask framework and setting website secret key
app = Flask(__name__)
app.config["SECRET_KEY"] = ("a"*32)

#Initializing MySQL database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'brightai'
app.config['MYSQL_DB'] = 'ContactWeb'

db = MySQL(app)

@app.after_request
def add_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Access-Control-Allow-Headers, Automatic"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, PUT, DELETE, OPTIONS"
    return response


#routing the website pages
@app.route("/Add contact", methods=["POST"])
def add_contact():
    mycursor = db.connection.cursor()
    emails = []
    tels = []
    try:
        _json = request.json
        _fname = _json['First_Name']
        _lname = _json['Last_Name']
        _email = _json['Email']
        _phone = _json['Phone']
        if _fname and _lname and _email and request.method == 'POST':
            contact = (_fname, _lname, _email, _phone,)
            mycursor.execute('SELECT Email FROM contacts')
            emails_info = mycursor.fetchall()
            for email in emails_info:
                emails.append(email[0])
            mycursor.execute('SELECT Phone FROM contacts')
            tels_info = mycursor.fetchall()
            for tel in tels_info:
                tels.append(tel[0])
            if ((contact[2] not in emails) and (contact[3] not in tels)):
                sql_formula = "INSERT INTO contacts (First_Name, Last_Name, Email, Phone) VALUES (%s, %s, %s, %s)"
                mycursor.execute(sql_formula, contact)
                db.connection.commit()
                resp = jsonify({"status": "Ok" ,"message": "Contact added sucessfully"})
                resp.status_code = 200
                return resp
            else:
                resp = jsonify({"status": "NOT ADDED" ,"message": "contact not added, either Email or Phone already exist!"})
                resp.status_code = 404
                return resp
        else:
            pass
    except Exception as e:
        print(e)
    finally:
        mycursor.close()

@app.route("/contact list")
def view_contacts():

    mycursor = db.connection.cursor()

    gotten = []
    people = []

    try:
        mycursor.execute("SELECT * FROM contacts")
        info = mycursor.fetchall()
        for i in info:
            gotten.append(i)

        for i in gotten:
            temp = {}
            temp.update({"First Name": i[0], "Last Name": i[1], "Email": i[2], "Phone": i[3]})
            people.append(temp)

        data = {"status": "Ok", "message": "Success","count": len(people), "data": people}
        resp = jsonify(data)
        resp.status_code = 200
        return resp
    except Exception as e:
        resp = jsonify({"status": "NOT FOUND" ,"message": "No contacts Found!"})
        resp.status_code = 404
        return resp
    finally:
        mycursor.close()


@app.route("/search contact/<id>")
def search_contact(id):

    info = id
    required = str(info)
    number = len(required)

    fnames = []
    lnames = []
    names = []
    emails = []
    tels = []


    try:
        mycursor = db.connection.cursor()

        mycursor.execute('SELECT First_Name FROM contacts')
        fnames_info = mycursor.fetchall()
        for name in fnames_info:
            fnames.append(str(name[0]))

        mycursor.execute('SELECT Last_Name FROM contacts')
        lnames_info = mycursor.fetchall()
        for name in lnames_info:
            lnames.append(str(name[0]))


        for i in range(len(fnames)):
            names.append(str(fnames[i] + " " + lnames[i]))


        mycursor.execute('SELECT Email FROM contacts')
        emails_info = mycursor.fetchall()
        for email in emails_info:
            emails.append(str(email[0]))

        mycursor.execute('SELECT Phone FROM contacts')
        tels_info = mycursor.fetchall()
        for tel in tels_info:
            tels.append(str(tel[0]))



        gotten = []
        people = []

        for name in fnames:
            if (name[0:(number)] == required or name[:] == required):
                mycursor.execute('SELECT first_name First_Name, last_name Last_Name, email Email, phone Phone FROM contacts WHERE First_Name=(%s)', (str(name), ))
                contact = mycursor.fetchall()
                gotten.append(contact)

        for email in emails:
            if (email[0:(number)] == required or email[:] == required):
                mycursor.execute('SELECT first_name First_Name, last_name Last_Name, email Email, phone Phone FROM contacts WHERE Email=(%s)', (str(email), ))
                contact = mycursor.fetchall()
                gotten.append(contact)

        for tel in tels:
            if (tel[0:(number)] == required or tel[:] == required):
                mycursor.execute('SELECT first_name First_Name, last_name Last_Name, email Email, phone Phone FROM contacts WHERE Phone=(%s)', (int(tel), ))
                contact = mycursor.fetchall()
                gotten.append(contact)


        for i in gotten:
            temp = {}
            temp.update({"First Name": i[0][0], "Last Name": i[0][1], "Email": i[0][2], "Phone": i[0][3]})
            people.append(temp)

        if len(people)==1:
            data = {"status": "Ok", "message": "Success","count": len(people), "data": people}
            resp = jsonify(data)
            resp.status_code = 200
            return resp
        elif len(people)>1:
            data = {"status": "Ok", "message": "Possible contacts found","count": len(people), "data": people}
            resp = jsonify(data)
            resp.status_code = 200
            return resp
        else:
            resp = jsonify({"status": "NOT FOUND" ,"message": "contact NOT found!"})
            resp.status_code = 404
            return resp


    except Exception as e:
        resp = jsonify({"status": "NOT FOUND" ,"message": "contact NOT found!"})
        resp.status_code = 404
        return resp
    finally:
        db.connection.cursor().close()



@app.route("/delete contact/<int:id>", methods=["DELETE"])
def delete_contact(id):

    try:
        mycursor = db.connection.cursor()
        mycursor.execute('DELETE FROM contacts WHERE Phone = (%s)', (id, ))
        db.connection.commit()
        resp = jsonify({"status": "Ok" ,"message": "Success!"})
        resp.status_code = 200
        return resp

    except Exception as e:
        resp = jsonify({"status": "NOT FOUND" ,"message": "contact NOT found!"})
        resp.status_code = 404
        return resp
    finally:
        db.connection.cursor().close()


@app.route("/update contact/<int:id>", methods=['PUT'])
def update_contact(id):
    try:
        mycursor = db.connection.cursor()
        _json = request.json
        _fname2 = _json['First_Name']
        _lname2 = _json['Last_Name']
        _email2 = _json['Email']
        _phone2 = _json['Phone']
        if _fname2 and _lname2 and _email2 and request.method == 'PUT':
            mycursor.execute("""
            UPDATE contacts
            SET First_Name = %s, Last_Name = %s, Email = %s, Phone = %s
            WHERE Phone = %s


            """, (_fname2, _lname2, _email2, _phone2, id))

            db.connection.commit()

            resp = jsonify({"status": "Ok" ,"message": "Success!"})
            resp.status_code = 200
            return resp
        else:
            pass
    except Exception as e:
        resp = jsonify({"status": "NOT FOUND" ,"message": "contact to be updated NOT found!"})
        resp.status_code = 404
        return resp
    finally:
        db.connection.cursor().close()

if __name__ == "__main__":
    app.run(debug=True)

