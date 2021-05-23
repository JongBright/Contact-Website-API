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
            if (contact[2] not in emails) and (contact[3] not in tels):
                sql_formula = "INSERT INTO contacts (First_Name, Last_Name, Email, Phone) VALUES (%s, %s, %s, %s)"
                mycursor.execute(sql_formula, contact)
                db.connection.commit()
                resp = jsonify("Contact added sucessfully")
                resp.status_code = 200
                return resp
            else:
                resp = jsonify('contact not added, either Email or Phone already exist!')
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
    try:
        mycursor.execute("SELECT * FROM contacts")
        info = mycursor.fetchall()
        resp = jsonify(info)
        resp.status_code = 200
        return resp
    except Exception as e:
        resp = jsonify('No contacts found!')
        resp.status_code = 404
        return resp
    finally:
        mycursor.close()



@app.route("/delete contact/<int:id>", methods=["DELETE"])
def delete_contact(id):

    try:
        mycursor = db.connection.cursor()
        mycursor.execute('DELETE FROM contacts WHERE Phone = (%s)', (id, ))
        db.connection.commit()
        resp = jsonify('User deleted sucessfully!')
        resp.status_code = 200
        return resp

    except Exception as e:
        resp = jsonify('contact NOT found!')
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
            resp = jsonify("Contact updated sucessfully!")
            resp.status_code = 200
            return resp
        else:
            pass
    except Exception as e:
        resp = jsonify('contact to be updated NOT found!')
        resp.status_code = 404
        return resp
    finally:
        db.connection.cursor().close()

if __name__ == "__main__":
    app.run(debug=True)

