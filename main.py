from flask import *
import sqlite3
import os
import time
import requests
from users import UserType
from users import UserAccount
from datetime import datetime
import nltk
import csv
import numpy as np

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random
import math 
import time

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVR
#from sklearn.svm import LinearSVR 
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
# Import package for linear model
from sklearn.linear_model import LinearRegression

#import datetime
import operator
from flask import Flask, render_template, Response

from FER_Camera import VideoCamera


app = Flask(__name__)
app.secret_key = '67tyrteytertwiruih67456bcagd'




# ------------------------------------------- nltk start ----------------------------------------------
def processTextNltk(text):
    negative = []
    with open("words_negative.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            negative.append(row)

    positive = []
    with open("words_positive.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            positive.append(row)



    temp = []  #
    text_sent = nltk.sent_tokenize(text)
    for sentence in text_sent:
        n_count = 0
        p_count = 0
        sent_words = nltk.word_tokenize(sentence)
        for word in sent_words:
            for item in positive:
                if (word == item[0]):
                    p_count += 1
            for item in negative:
                if (word == item[0]):
                    n_count += 1

        if (p_count > 0 and n_count == 0):  # any number of only positives (+) [case 1]
            # print "+ : " + sentence
            temp.append(1)
        elif (n_count % 2 > 0):  # odd number of negatives (-) [case2]
            # print "- : " + sentence
            temp.append(-1)
        elif (n_count % 2 == 0 and n_count > 0):  # even number of negatives (+) [case3]
            # print "+ : " + sentence
            temp.append(1)
        else:
            # print "? : " + sentence
            temp.append(0)

    return np.average(temp)











# ------------------------------------------- nltk end   ----------------------------------------------





# ------------------------------------------- data base start ----------------------------------------------
DATABASE = 'userdatabase.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# ------------------------------------ data base end -------------------------------------------


# ------------------------------------      admin Login start       ----------------------------
def adminLogin(phone, password):
    conn = get_db()
    user = query_db('select * from administrator where phone = ? AND pass = ?',
                    (phone, password), one=True)
    return user


# ------------------------------------ data base admin login end   -----------------------------


# -----------------------------         station code start          ----------------------------
def insert_station(name, location, pincode, address, phone):
    con = get_db()
    status = False
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO stations(name,location,pincode,address, phone)VALUES(?,?,?,?,?)",
                    (name, location, pincode, address, phone))
        con.commit()
        status = True
    except Exception as e:
        print(e)
        con.rollback()
        status = False
    finally:
        return status


def getAllStations():
    conn = get_db()
    stations = query_db('select * from stations')
    return stations


def delete_station_id(station_id):
    conn = get_db()
    sql = 'DELETE FROM stations WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (station_id,))
    conn.commit()


def getStation(station_id):
    conn = get_db()
    station = query_db('select * from stations where id = ?',
                       (station_id,), one=True)
    return station


def updateStation(station_id, name, location, pinCode, address, phone):
    status = False
    try:
        conn = get_db()
        sql = "UPDATE stations SET name = ?, location = ?, pincode=?, address=?, phone=? WHERE id = ?"
        cur = conn.cursor()
        cur.execute(sql, (name, location, pinCode, address, phone, station_id))
        conn.commit()
        status = True
    except Exception as e:
        print(e)
        conn.rollback()
        status = False
    finally:
        return status


# -----------------------------         station code end          ----------------------------

# ----------------------------- officers code start  ------------------------------------
def insert_officer(officer_id, station_name, name, phone, psw, address):
    con = get_db()
    status = False
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO officers(officer_id,station_name,name,phone, psw, address)VALUES(?,?,?,?,?,?)",
                    (officer_id, station_name, name, phone, psw, address))
        con.commit()
        status = True
    except Exception as e:
        print(e)
        con.rollback()
        status = False
    finally:
        return status


def getAllOfficers():
    conn = get_db()
    officers = query_db('select * from officers')
    return officers


def delete_officer_id(officer_db_id):
    conn = get_db()
    sql = 'DELETE FROM officers WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (officer_db_id,))
    conn.commit()


def getOfficer(officer_db_id):
    conn = get_db()
    station = query_db('select * from officers where id = ?',
                       (officer_db_id,), one=True)
    return station


def updateOfficer(officer_db_id, officer_id, name, phone, psw, station, address):
    status = False
    try:
        conn = get_db()
        sql = "UPDATE officers SET officer_id = ?, name = ?, phone=?, psw=?, address=?, station_name=? WHERE id = ?"
        cur = conn.cursor()
        cur.execute(sql, (officer_id, name, phone, psw, address, station, officer_db_id))
        conn.commit()
        status = True
    except Exception as e:
        print(e)
        conn.rollback()
        status = False
    finally:
        return status


def officerLogin(phone, password):
    conn = get_db()
    user = query_db('select * from officers where phone = ? AND psw = ?',
                    (phone, password), one=True)
    return user


# --------------------------- officers code end here  --------------------------------------


# ----------------------------- citizen code start  ------------------------------------
def insert_citizen(name, phone, psw, address, station_name):
    con = get_db()
    status = False
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO citizens(name,phone, psw, address,station_name)VALUES(?,?,?,?,?)",
                    (name, phone, psw, address, station_name))
        con.commit()
        status = True
    except Exception as e:
        print(e)
        con.rollback()
        status = False
    finally:
        return status


def getAllCitizens():
    conn = get_db()
    officers = query_db('select * from citizens')
    return officers


def delete_citizen_id(citizen_db_id):
    conn = get_db()
    sql = 'DELETE FROM citizens WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (citizen_db_id,))
    conn.commit()


def getCitizen(citizen_db_id):
    conn = get_db()
    station = query_db('select * from citizens where id = ?',
                       (citizen_db_id,), one=True)
    return station


def updateCitizen(citizen_db_id, name, phone, psw, address, station):
    status = False
    try:
        conn = get_db()
        sql = "UPDATE citizens SET  name = ?, phone=?, psw=?, address=?, station_name=? WHERE id = ?"
        cur = conn.cursor()
        cur.execute(sql, (name, phone, psw, address, station, citizen_db_id))
        conn.commit()
        status = True
    except Exception as e:
        print(e)
        conn.rollback()
        status = False
    finally:
        return status


def citizenLogin(phone, password):
    conn = get_db()
    user = query_db('select * from citizens where phone = ? AND psw = ?',
                    (phone, password), one=True)
    return user


# --------------------------- citizen code end here  --------------------------------------


# ----------------------------- complaint code start  ------------------------------------
# (name,phone,address,description,station_name,status):
def insert_complaint(name, phone, address, description, station_name, status):
    con = get_db()

    now = datetime.now()
    dnt = now.strftime("%m/%d/%Y, %H:%M:%S")

    sts = False
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO complaints(name,phone, address,description, station_name,status,dnt)VALUES(?,?,?,?,?,?,?)",
            (name, phone, address, description, station_name, status, dnt))
        con.commit()
        sts = True
    except Exception as e:
        print(e)
        con.rollback()
        sts = False
    finally:
        return sts


def getAllComplaints():
    conn = get_db()
    complaints = query_db('select * from complaints')
    return complaints


def getAllComplaintsOfStation(station):
    conn = get_db()
    complaints = query_db('select * from complaints where station_name = ?',
                          (station,), one=False)
    return complaints


def getAllComplaintsOfCitizen(citizen_phone):
    conn = get_db()
    complaints = query_db('select * from complaints where phone = ?',
                          (citizen_phone,), one=False)
    return complaints


def getAllEmergencyComplaintsOfCitizen(citizen_phone):
    conn = get_db()
    complaints = query_db('select * from emcomplaints where phone = ?',
                          (citizen_phone,), one=False)
    return complaints


def delete_complaint_id(complaint_db_id):
    conn = get_db()
    sql = 'DELETE FROM complaints WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (complaint_db_id,))
    conn.commit()


def getComplaint(complaint_db_id):
    conn = get_db()
    station = query_db('select * from complaints where id = ?',
                       (complaint_db_id,), one=True)
    return station


def updateComplaint(complaint_db_id, name, phone, address, description, station_name, status):
    result = False
    try:
        conn = get_db()
        sql = "UPDATE complaints SET name = ?, phone=?, address=?, station_name=?, description= ?, status=? WHERE id = ?"
        cur = conn.cursor()
        cur.execute(sql, (name, phone, address, station_name, description, status, complaint_db_id))
        conn.commit()
        result = True
    except Exception as e:
        print(e)
        conn.rollback()
        result = False
    finally:
        return result


# --------------------------- complaint code end here  --------------------------------------


# ----------------------------- emergancy complaint code start  -----------------------------
def insert_emergency_complaint(name, phone, address, description, station_name, status):
    con = get_db()
    sts = False
    try:
        now = datetime.now()
        dnt = now.strftime("%m/%d/%Y, %H:%M:%S")
        cur = con.cursor()
        cur.execute(
            "INSERT INTO emcomplaints(name,phone, address,description, station_name,status,dnt)VALUES(?,?,?,?,?,?,?)",
            (name, phone, address, description, station_name, status, dnt))
        con.commit()
        sts = True
    except Exception as e:
        print(e)
        con.rollback()
        sts = False
    finally:
        return sts


def getAllEmergencyComplaints():
    conn = get_db()
    complaints = query_db('select * from emcomplaints')
    return complaints


def getAllEmergencyComplaintsOfStation(station):
    conn = get_db()
    complaints = query_db('select * from emcomplaints where station_name = ?',
                          (station,), one=False)
    return complaints


def delete_emergency_complaint_id(complaint_db_id):
    conn = get_db()
    sql = 'DELETE FROM emcomplaints WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (complaint_db_id,))
    conn.commit()


def getEmergencyComplaint(complaint_db_id):
    conn = get_db()
    station = query_db('select * from emcomplaints where id = ?',
                       (complaint_db_id,), one=True)
    return station


def updateEmergencyComplaint(complaint_db_id, name, phone, address, description, station_name, status):
    result = False
    try:
        conn = get_db()
        sql = "UPDATE emcomplaints SET name = ?, phone=?, address=?, station_name=?, description= ?, status=? WHERE id = ?"
        cur = conn.cursor()
        cur.execute(sql, (name, phone, address, station_name, description, status, complaint_db_id))
        conn.commit()
        result = True
    except Exception as e:
        print(e)
        conn.rollback()
        result = False
    finally:
        return result


# --------------------------- complaint code end here  --------------------------------------


# ----------------------------- query code start  -------------------------------------------
def insert_query_complaint(name, query, answer):
    con = get_db()
    sts = False

    try:
        now = datetime.now()
        dnt = now.strftime("%m/%d/%Y, %H:%M:%S")
        cur = con.cursor()
        cur.execute("INSERT INTO queries(name, query, answer,dnt)VALUES(?,?,?,?)",
                    (name, query, answer, dnt))
        con.commit()
        sts = True
    except Exception as e:
        print(e)
        con.rollback()
        sts = False
    finally:
        return sts


def getAllQuery():
    conn = get_db()
    complaints = query_db('select * from queries')
    return complaints


def delete_query_id(complaint_db_id):
    conn = get_db()
    sql = 'DELETE FROM queries WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (complaint_db_id,))
    conn.commit()


def getQuery(query_db_id):
    conn = get_db()
    station = query_db('select * from queries where id = ?',
                       (query_db_id,), one=True)
    return station


def updateQuery(query_db_id, name, query, answer):
    result = False
    try:
        conn = get_db()
        sql = "UPDATE queries SET name = ?, query=?, answer=? WHERE id = ?"
        cur = conn.cursor()
        cur.execute(sql, (name, query, answer, query_db_id))
        conn.commit()
        result = True
    except Exception as e:
        print(e)
        conn.rollback()
        result = False
    finally:
        return result


# --------------------------- query code end here  ----------------------------------------


# ----------------------------- feedbacks code start  -------------------------------------------
def insert_feedback(feedback):
    con = get_db()
    sts = False
    try:
        now = datetime.now()
        dnt = now.strftime("%m/%d/%Y, %H:%M:%S")
        cur = con.cursor()
        cur.execute("INSERT INTO feedbacks( feedback,dnt)VALUES(?,?)",
                    (feedback, dnt))
        con.commit()
        sts = True
    except Exception as e:
        print(e)
        con.rollback()
        sts = False
    finally:
        return sts


def getAllFeedbacks():
    conn = get_db()
    complaints = query_db('select * from feedbacks')
    return complaints


def delete_feedback_id(feedback_db_id):
    conn = get_db()
    sql = 'DELETE FROM feedbacks WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (feedback_db_id,))
    conn.commit()


def getFeedback(feedback_db_id):
    conn = get_db()
    station = query_db('select * from feedbacks where id = ?',
                       (feedback_db_id,), one=True)
    return station


def updateFeedback(query_db_id, feedback):
    result = False
    try:
        conn = get_db()
        sql = "UPDATE feedbacks SET  feedback=? WHERE id = ?"
        cur = conn.cursor()
        cur.execute(sql, (feedback, query_db_id))
        conn.commit()
        result = True
    except Exception as e:
        print(e)
        conn.rollback()
        result = False
    finally:
        return result


# --------------------------- feedbacks code end here  ----------------------------------------


@app.route('/')
def index():
    states = ["ANDHRA PRADESH", "ARUNACHAL PRADESH", "ASSAM", "BIHAR", "CHHATTISGARH", "GOA", "GUJARAT", "HARYANA", \
              "HIMACHAL PRADESH", "JAMMU & KASHMIR", "JHARKHAND", "KARNATAKA", "KERALA", "MADHYA PRADESH",
              "MAHARASHTRA", \
              "MANIPUR", "MEGHALAYA", "MIZORAM", "NAGALAND", "ODISHA", "PUNJAB", "RAJASTHAN", "SIKKIM", "TAMIL NADU",
              "TRIPURA", \
              "UTTAR PRADESH", "UTTARAKHAND", "WEST BENGAL", "A & N ISLANDS", "CHANDIGARH", "D & N HAVELI",
              "DAMAN & DIU", "DELHI UT", "LAKSHADWEEP", "PUDUCHERRY"]

    years = ["2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012"]

    if request.args.get('year') is None:
        current_year = years[0]
    else:
        if request.args.get('year') in years:
            current_year = request.args.get('year')
        else:
            current_year = years[0]

    if request.args.get('state') is None:
        current_state = states[0]
    else:
        if request.args.get('state') in states:
            current_state = request.args.get('state')
        else:
            current_state = states[0]

    rvYears = years
    rvYears.reverse()
    print(rvYears)

    return render_template('index.html', user=UserType, dataYears=years,
                           dataStates=states, selected_year=current_year, selected_state=current_state, reverseYears=rvYears)


# -------------------------------- admin operation start from here -----------------------

@app.route('/admin_login', methods=['POST'])
def admin_login():
    phone = request.form['phone']
    password = request.form['pass']
    u = adminLogin(phone, password)
    # print(user[1])

    if u is None:
        return "<script>alert('Phone or password did not match.'); window.open('/','_self')</script>"
    else:
        # uid, name, phone, psw, email, account_type, address, gender
        user = UserAccount()
        user.uid = u[0]
        user.name = u[1]
        user.phone = u[2]
        user.psw = [3]
        user.account_type = UserType.admin
        user.gender = u[4]

        session['user_type'] = UserType.admin
        session['user_name'] = user.name

        return redirect("/admin_account", code=302)


@app.route('/admin_account', methods=['POST', 'GET'])
def admin_account():
    if session['user_type'] == UserType.admin:
        return render_template('admin-account.html')
    else:
        return redirect("/", code=302)


@app.route('/manage')
def manage():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('opt') == "police_stations":
        return redirect("/manage_police_station", code=302)

    elif request.args.get('opt') == "police_officers":
        return redirect("/manage_police_officers", code=302)

    elif request.args.get('opt') == "citizens":
        return redirect("/manage_citizens", code=302)

    elif request.args.get('opt') == "complaints":
        return redirect("/manage_complaints", code=302)

    elif request.args.get('opt') == "em_complaints":
        return redirect("/manage_emergency_complaints", code=302)

    elif request.args.get('opt') == "queries":
        return redirect("/manage_queries", code=302)

    elif request.args.get('opt') == "feedbacks":
        return redirect("/manage_feedbacks", code=302)

    elif request.args.get('type') == UserType.officer:
        return render_template('login.html', user_type=UserType.officer)

    return render_template('index.html', user=UserType)


# manage police station start from here

@app.route('/manage_police_station')
def manage_police_station():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('opt') is None or request.args.get('opt') == "add_police_stations":
        return render_template('manage-police-stations.html', active='Add Police Stations', stationToUpdate=None)

    elif request.args.get('opt') == "update_police_stations":
        if request.args.get('update_id') is not None:
            update_id = request.args.get('update_id')
            stationUpdate = getStation(update_id)
            # print(stationUpdate)
            return render_template('manage-police-stations.html', active='Update Police Stations',
                                   stationToUpdate=stationUpdate)
        else:
            stations = getAllStations()
            return render_template('manage-police-stations.html', active='Update Police Stations', stations=stations,
                                   stationToUpdate=None)

    elif request.args.get('opt') == "display_police_stations":
        stations = getAllStations()
        return render_template('manage-police-stations.html', active='Display Police Stations', stations=stations,
                               stationToUpdate=None)

    elif request.args.get('opt') == "delete_police_stations":
        stations = getAllStations()
        return render_template('manage-police-stations.html', active='Delete Police Stations', stations=stations,
                               stationToUpdate=None)

    return render_template('manage-police-stations.html', active='Add Police Stations', stationToUpdate=None)


@app.route('/add_station', methods=['POST', 'GET'])
def add_station():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)
    name = request.form['name']
    location = request.form['location']
    pincode = request.form['pincode']
    address = request.form['address']
    phone = request.form['phone']

    if insert_station(name, location, pincode, address, phone):
        return "<script>alert('Add station successful.'); window.open(" \
               "'/manage_police_station?opt=display_police_stations','_self')</script> "
    else:
        return "<script>alert('Fail to add Station.'); window.open(" \
               "'/manage_police_station?opt=add_police_stations','_self')</script> "


@app.route('/update_station', methods=['POST', 'GET'])
def update_station():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)
    station_id = request.form['station_id']
    name = request.form['name']
    location = request.form['location']
    pincode = request.form['pincode']
    address = request.form['address']
    phone = request.form['phone']

    if updateStation(station_id, name, location, pincode, address, phone):
        return "<script>alert('Update station successful.'); window.open(" \
               "'/manage_police_station?opt=update_police_stations','_self')</script> "
    else:
        return "<script>alert('Fail to update Station.'); window.open(" \
               "'/manage_police_station','_self')</script> "


@app.route('/delete_station', methods=['POST', 'GET'])
def delete_station():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('id') is not None:
        id = request.args.get('id')
        delete_station_id(id)
        return "<script>alert('Delete station successful.'); window.open(" \
               "'/manage_police_station?opt=delete_police_stations','_self')</script>"

    return "<script>alert('Fail to delete station.'); window.open(" \
           "'/manage_police_station?opt=delete_police_stations','_self')</script>"


# manage officers start from here
@app.route('/manage_police_officers')
def manage_police_officers():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('opt') is None or request.args.get('opt') == "add_police_officers":
        all_stations = getAllStations()
        return render_template('manage-police-officers.html', active='Add Police Officer', all_stations=all_stations)

    elif request.args.get('opt') == "update_police_officers":
        if request.args.get('update_id') is not None:
            update_id = request.args.get('update_id')
            officer = getOfficer(update_id)
            stations = getAllStations()
            return render_template('manage-police-officers.html', active='Update Police Officer',
                                   officerToUpdate=officer, all_stations=stations)
        else:
            officers = getAllOfficers()
            return render_template('manage-police-officers.html', active='Update Police Officer', allOfficers=officers,
                                   officerToUpdate=None)

    elif request.args.get('opt') == "display_police_officers":
        officers = getAllOfficers()
        return render_template('manage-police-officers.html', active='Display Police Officer',
                               allOfficers=officers)

    elif request.args.get('opt') == "delete_police_officers":
        allOfficers = getAllOfficers()
        return render_template('manage-police-officers.html', active='Delete Police Officer', allOfficers=allOfficers,
                               officerToUpdate=None)
    all_stations = getAllStations()
    return render_template('manage-police-officers.html', active='Add Police Officer', all_stations=all_stations)


@app.route('/add_officer', methods=['POST', 'GET'])
def add_officer():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)
    officer_id = request.form['officer_id']
    station_name = request.form['station_name']
    name = request.form['name']
    phone = request.form['phone']
    psw = request.form['psw']
    address = request.form['address']

    if insert_officer(officer_id, station_name, name, phone, psw, address):
        return "<script>alert('Add Officer successful.'); window.open(" \
               "'/manage_police_officers?opt=display_police_officers','_self')</script> "
    else:
        return "<script>alert('Fail to add Officer.'); window.open(" \
               "'/manage_police_officers','_self')</script>"


@app.route('/delete_officer', methods=['POST', 'GET'])
def delete_officer():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('id') is not None:
        id = request.args.get('id')
        delete_officer_id(id)
        return "<script>alert('Delete Officer successful.'); window.open(" \
               "'/manage_police_officers?opt=delete_police_officers','_self')</script>"

    return "<script>alert('Fail to Officer station.'); window.open(" \
           "'/manage_police_officers?opt=delete_police_officers','_self')</script>"


@app.route('/update_officer', methods=['POST', 'GET'])
def update_officer():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)
    officer_db_id = request.form['officer_db_id']
    officer_id = request.form['officer_id']
    name = request.form['name']
    phone = request.form['phone']
    psw = request.form['pass']
    station_name = request.form['station_name']
    address = request.form['address']
    # updateOfficer(officer_db_id, officer_id, name, phone, psw, station, address)
    if updateOfficer(officer_db_id, officer_id, name, phone, psw, station_name, address):
        return "<script>alert('Update officer successful.'); window.open(" \
               "'/manage_police_officers?opt=update_police_officers','_self')</script> "
    else:
        return "<script>alert('Fail to update Officer.'); window.open(" \
               "'/manage_police_officers','_self')</script> "

    # manage police officer end


# manage citizen start from here

@app.route('/manage_citizens')
def manage_citizens():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('opt') is None or request.args.get('opt') == "add_citizens":
        all_stations = getAllStations()
        return render_template('manage-citizens.html', active='Add Citizen', all_stations=all_stations)

    elif request.args.get('opt') == "update_citizens":
        if request.args.get('update_id') is not None:
            update_id = request.args.get('update_id')
            stations = getAllStations()
            citizen = getCitizen(update_id)
            # print(citizen)
            return render_template('manage-citizens.html', active='Update Citizen',
                                   citizenToUpdate=citizen, all_stations=stations)
        else:
            citizens = getAllCitizens()
            return render_template('manage-citizens.html', active='Update Citizen', allCitizens=citizens,
                                   citizenToUpdate=None)

    elif request.args.get('opt') == "display_citizens":
        citizens = getAllCitizens()
        return render_template('manage-citizens.html', active='Display Citizen',
                               allCitizens=citizens)

    elif request.args.get('opt') == "delete_citizens":
        citizens = getAllCitizens()
        return render_template('manage-citizens.html', active='Delete Citizen', allCitizens=citizens,
                               citizenToUpdate=None)
    all_stations = getAllStations()
    return render_template('manage-citizens.html', active='Add Citizen', all_stations=all_stations)


@app.route('/add_citizen', methods=['POST', 'GET'])
def add_citizen():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    name = request.form['name']
    phone = request.form['phone']
    psw = request.form['psw']
    address = request.form['address']
    station_name = request.form['station_name']

    if insert_citizen(name, phone, psw, address, station_name):
        return "<script>alert('Add Citizen successful.'); window.open(" \
               "'/manage_citizens?opt=display_citizen','_self')</script> "
    else:
        return "<script>alert('Fail to add Citizen.'); window.open(" \
               "'/manage_citizens','_self')</script>"


@app.route('/delete_citizen', methods=['POST', 'GET'])
def delete_citizen():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('id') is not None:
        id = request.args.get('id')
        delete_citizen_id(id)
        return "<script>alert('Delete Citizen successful.'); window.open(" \
               "'/manage_citizens?opt=delete_citizens','_self')</script>"

    return "<script>alert('Fail to delete Citizen.'); window.open(" \
           "'/manage_citizens?opt=delete_citizens','_self')</script>"


@app.route('/update_citizen', methods=['POST', 'GET'])
def update_citizen():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)
    officer_db_id = request.form['citizen_db_id']
    name = request.form['name']
    phone = request.form['phone']
    psw = request.form['pass']
    station_name = request.form['station_name']
    address = request.form['address']

    if updateCitizen(officer_db_id, name, phone, psw, address, station_name):
        return "<script>alert('Update Citizen successful.'); window.open(" \
               "'/manage_citizens?opt=update_citizens','_self')</script> "
    else:
        return "<script>alert('Fail to update Citizen.'); window.open(" \
               "'/manage_citizens','_self')</script> "


# manage citizen end from here


# manage Complaint start from here

@app.route('/manage_complaints')
def manage_complaints():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('opt') is None or request.args.get('opt') == "add_complaints":
        all_stations = getAllStations()
        return render_template('manage-complaints.html', active='Add Complaint', all_stations=all_stations)

    elif request.args.get('opt') == "update_complaints":
        if request.args.get('update_id') is not None:
            update_id = request.args.get('update_id')
            stations = getAllStations()
            complaints = getComplaint(update_id)
            # print(complaints)
            return render_template('manage-complaints.html', active='Update Complaint',
                                   complaintToUpdate=complaints, all_stations=stations)
        else:
            complaints = getAllComplaints()
            return render_template('manage-complaints.html', active='Update Complaint', allComplaints=complaints,
                                   complaintToUpdate=None)

    elif request.args.get('opt') == "display_complaints":
        complaints = getAllComplaints()

        print(complaints)

        complaints_senti = []

        for complaint in complaints:
            analysis = processTextNltk(complaint[4])
            print(complaints.index(complaint))
            complaint =  complaint+(analysis,)
            complaints_senti.append(complaint)
            print(type(complaint))


        print(complaints_senti)
        return render_template('manage-complaints.html', active='Display Complaint',
                               allComplaints=complaints_senti)

    elif request.args.get('opt') == "delete_complaints":
        complaints = getAllComplaints()
        return render_template('manage-complaints.html', active='Delete Complaint', allComplaints=complaints,
                               citizenToUpdate=None)
    all_stations = getAllStations()
    return render_template('manage-complaints.html', active='Add Complaint', all_stations=all_stations)


@app.route('/add_complaint', methods=['POST', 'GET'])
def add_complaint():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    description = request.form['description']
    station_name = request.form['station_name']
    status = request.form['status']

    if insert_complaint(name, phone, address, description, station_name, status):
        return "<script>alert('Add Complaint successful.'); window.open(" \
               "'/manage_complaints?opt=display_complaints','_self')</script> "
    else:
        return "<script>alert('Fail to add Complaint.'); window.open(" \
               "'/manage_complaints','_self')</script>"


@app.route('/delete_complaint', methods=['POST', 'GET'])
def delete_complaint():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('id') is not None:
        id = request.args.get('id')
        delete_complaint_id(id)
        return "<script>alert('Delete Complaint successful.'); window.open(" \
               "'/manage_complaints?opt=delete_complaints','_self')</script>"

    return "<script>alert('Fail to Complaint Citizen.'); window.open(" \
           "'/manage_complaints?opt=delete_complaints','_self')</script>"


@app.route('/update_complaint', methods=['POST', 'GET'])
def update_complaint():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    complaint_db_id = request.form['complaint_db_id']

    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    description = request.form['description']
    station_name = request.form['station_name']
    status = request.form['status']

    if updateComplaint(complaint_db_id, name, phone, address, description, station_name, status):
        return "<script>alert('Update Complaint successful.'); window.open(" \
               "'/manage_complaints?opt=update_complaints','_self')</script> "
    else:
        return "<script>alert('Fail to update Complaint.'); window.open(" \
               "'/manage_complaints','_self')</script> "


# manage complaint end from here


# manage emergency complaint start from here

@app.route('/manage_emergency_complaints')
def manage_emergency_complaints():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('opt') is None or request.args.get('opt') == "add_emergency_complaints":
        all_stations = getAllStations()
        return render_template('manage-em-complaints.html', active='Add Emergency Complaint', all_stations=all_stations)

    elif request.args.get('opt') == "update_emergency_complaints":
        if request.args.get('update_id') is not None:
            update_id = request.args.get('update_id')
            stations = getAllStations()
            complaints = getEmergencyComplaint(update_id)
            # print(complaints)
            return render_template('manage-em-complaints.html', active='Update Emergency Complaint',
                                   complaintToUpdate=complaints, all_stations=stations)
        else:
            complaints = getAllEmergencyComplaints()
            return render_template('manage-em-complaints.html', active='Update Emergency Complaint',
                                   allComplaints=complaints,
                                   complaintToUpdate=None)

    elif request.args.get('opt') == "display_emergency_complaints":
        complaints = getAllEmergencyComplaints()
        # print(complaints)
        return render_template('manage-em-complaints.html', active='Display Emergency Complaint',
                               allComplaints=complaints)

    elif request.args.get('opt') == "delete_emergency_complaints":
        complaints = getAllEmergencyComplaints()
        return render_template('manage-em-complaints.html', active='Delete Emergency Complaint',
                               allComplaints=complaints,
                               citizenToUpdate=None)
    all_stations = getAllStations()
    return render_template('manage-em-complaints.html', active='Add Emergency Complaint', all_stations=all_stations)


@app.route('/add_emergency_complaint', methods=['POST', 'GET'])
def add_emergency_complaint():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    description = request.form['description']
    station_name = request.form['station_name']
    status = request.form['status']

    if insert_emergency_complaint(name, phone, address, description, station_name, status):
        return "<script>alert('Add Emergency Complaint successful.'); window.open(" \
               "'/manage_emergency_complaints?opt=display_emergency_complaints','_self')</script> "
    else:
        return "<script>alert('Fail to add Emergency Complaint.'); window.open(" \
               "'/manage_emergency_complaints','_self')</script>"


@app.route('/delete_emergency_complaint', methods=['POST', 'GET'])
def delete_emergency_complaint():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('id') is not None:
        id = request.args.get('id')

        delete_emergency_complaint_id(id)
        return "<script>alert('Delete Emergency Complaint successful.'); window.open(" \
               "'/manage_emergency_complaints?opt=delete_emergency_complaints','_self')</script>"

    return "<script>alert('Fail to delete Emergency Complaint.'); window.open(" \
           "'/manage_emergency_complaints?opt=delete_emergency_complaints','_self')</script>"


@app.route('/update_emergency_complaint', methods=['POST', 'GET'])
def update_emergency_complaint():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    complaint_db_id = request.form['complaint_db_id']

    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    description = request.form['description']
    station_name = request.form['station_name']
    status = request.form['status']

    if updateEmergencyComplaint(complaint_db_id, name, phone, address, description, station_name, status):
        return "<script>alert('Update Emergency Complaint successful.'); window.open(" \
               "'/manage_emergency_complaints?opt=update_emergency_complaints','_self')</script> "
    else:
        return "<script>alert('Fail to update Emergency Complaint.'); window.open(" \
               "'/manage_emergency_complaints','_self')</script> "


# manage emergency complaint end from here


# manage queries start from here

@app.route('/manage_queries')
def manage_queries():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('opt') is None or request.args.get('opt') == "add_queries":
        all_stations = getAllStations()
        return render_template('manage-queries.html', active='Add Query', all_stations=all_stations)

    elif request.args.get('opt') == "update_queries":
        if request.args.get('update_id') is not None:
            update_id = request.args.get('update_id')
            queries = getAllQuery()
            query = getQuery(update_id)
            # print(complaints)
            return render_template('manage-queries.html', active='Update Query',
                                   queryToUpdate=query, allQueries=queries)
        else:
            queries = getAllQuery()
            return render_template('manage-queries.html', active='Update Query', allQueries=queries,
                                   queryToUpdate=None)

    elif request.args.get('opt') == "display_queries":
        queries = getAllQuery()
        # print(complaints)
        return render_template('manage-queries.html', active='Display Query',
                               allQueries=queries)

    elif request.args.get('opt') == "delete_queries":
        queries = getAllQuery()
        return render_template('manage-queries.html', active='Delete Query', allQueries=queries,
                               queryToUpdate=None)
    all_stations = getAllStations()
    return render_template('manage-queries.html', active='Add Query', all_stations=all_stations)


@app.route('/add_query', methods=['POST', 'GET'])
def add_query():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    name = request.form['name']
    query = request.form['query']

    if insert_query_complaint(name, query, ""):
        return "<script>alert('Add Query successful.'); window.open(" \
               "'/manage_queries?opt=display_queries','_self')</script> "
    else:
        return "<script>alert('Fail to add Query.'); window.open(" \
               "'/manage_queries','_self')</script>"


@app.route('/delete_query', methods=['POST', 'GET'])
def delete_query():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('id') is not None:
        id = request.args.get('id')

        delete_query_id(id)
        return "<script>alert('Delete Query successful.'); window.open(" \
               "'/manage_queries?opt=delete_queries','_self')</script>"

    return "<script>alert('Fail to delete Query.'); window.open(" \
           "'/manage_queries?opt=delete_queries','_self')</script>"


@app.route('/update_query', methods=['POST', 'GET'])
def update_query():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    query_db_id = request.form['query_db_id']

    name = request.form['name']
    query = request.form['query']
    answer = request.form['answer']

    if updateQuery(query_db_id, name, query, answer):
        return "<script>alert('Update Query successful.'); window.open(" \
               "'/manage_queries?opt=update_queries','_self')</script> "
    else:
        return "<script>alert('Fail to update Query.'); window.open(" \
               "'/manage_queries','_self')</script> "


# manage queries end from here


# manage feedback start from here

@app.route('/manage_feedbacks')
def manage_feedbacks():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('opt') is None or request.args.get('opt') == "add_feedbacks":
        all_stations = getAllStations()
        return render_template('manage-feedbacks.html', active='Add Feedback', all_stations=all_stations)

    elif request.args.get('opt') == "update_feedbacks":
        if request.args.get('update_id') is not None:
            update_id = request.args.get('update_id')
            feedbacks = getAllFeedbacks()
            feedback = getFeedback(update_id)
            # print(complaints)
            return render_template('manage-feedbacks.html', active='Update Feedback',
                                   feedbackToUpdate=feedback, allFeedbacks=feedbacks)
        else:
            feedbacks = getAllFeedbacks()
            return render_template('manage-feedbacks.html', active='Update Feedback', allFeedbacks=feedbacks,
                                   feedbackToUpdate=None)

    elif request.args.get('opt') == "display_feedbacks":
        feedbacks = getAllFeedbacks()
        # print(complaints)
        return render_template('manage-feedbacks.html', active='Display Feedback',
                               allFeedbacks=feedbacks)

    elif request.args.get('opt') == "delete_feedbacks":
        feedbacks = getAllFeedbacks()
        return render_template('manage-feedbacks.html', active='Delete Feedback', allFeedbacks=feedbacks,
                               queryToUpdate=None)
    all_stations = getAllStations()
    return render_template('manage-feedbacks.html', active='Add Feedback', all_stations=all_stations)


@app.route('/add_feedback', methods=['POST', 'GET'])
def add_feedback():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    feedback = request.form['feedback']

    if insert_feedback(feedback):
        return "<script>alert('Add Feedback successful.'); window.open(" \
               "'/manage_feedbacks?opt=display_feedbacks','_self')</script> "
    else:
        return "<script>alert('Fail to add Feedback.'); window.open(" \
               "'/manage_feedbacks','_self')</script>"


@app.route('/delete_feedback', methods=['POST', 'GET'])
def delete_feedback():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    if request.args.get('id') is not None:
        id = request.args.get('id')

        delete_feedback_id(id)
        return "<script>alert('Delete Feedback successful.'); window.open(" \
               "'/manage_queries?opt=delete_feedbacks','_self')</script>"

    return "<script>alert('Fail to delete Feedback.'); window.open(" \
           "'/manage_queries?opt=delete_feedbacks','_self')</script>"


@app.route('/update_feedback', methods=['POST', 'GET'])
def update_feedback():
    if not session['user_type'] == UserType.admin:
        return render_template('index.html', user=UserType)

    query_db_id = request.form['query_db_id']

    feedback = request.form['feedback']

    if updateFeedback(query_db_id, feedback):
        return "<script>alert('Update Feedback successful.'); window.open(" \
               "'/manage_feedbacks?opt=update_feedbacks','_self')</script> "
    else:
        return "<script>alert('Fail to update Feedback.'); window.open(" \
               "'/manage_feedbacks','_self')</script> "


# manage feedback end from here


# -----------------            admin end here            -----------------------


# ----------- officer start from here ------------------------

@app.route('/officer_login', methods=['POST', 'GET'])
def officer_login():
    phone = request.form['phone']
    password = request.form['pass']
    u = officerLogin(phone, password)
    print(u)

    if u is None:
        return "<script>alert('Phone or password did not match.'); window.open('/','_self')</script>"
    else:
        # uid, name, phone, psw, email, account_type, address, gender
        user = UserAccount()
        user.uid = u[0]
        user.name = u[1]
        user.phone = u[2]
        user.psw = [3]
        user.account_type = UserType.officer

        session['user_type'] = UserType.officer
        session['user_name'] = user.name
        session['user_id'] = user.uid
        session['station_name'] = u[6]
        # print("redirected ..")
        return redirect("/officer_account", code=302)


@app.route('/officer_account', methods=['POST', 'GET'])
def officer_account():
    # print(session['user_type'])
    if not session['user_type'] == UserType.officer:
        return redirect("/", code=302)

    if request.args.get('opt') == "update_complaints":
        if request.args.get('update_id') is not None:
            update_id = request.args.get('update_id')
            stations = getAllStations()
            complaints = getComplaint(update_id)
            # print(complaints)
            return render_template('officer-account.html', active='Update Complaint',
                                   complaintToUpdate=complaints, all_stations=stations)
        else:
            station_name = session['station_name']
            complaints = getAllComplaintsOfStation(station_name)
            print(complaints)

            return render_template('officer-account.html', active='Update Complaint', allComplaints=complaints,
                                   complaintToUpdate=None)

    elif request.args.get('opt') == "display_complaints" or request.args.get('opt') is None:
        station_name = session['station_name']
        complaints = getAllComplaintsOfStation(station_name)
        print(complaints)
        complaints_senti = []

        for complaint in complaints:
            analysis = processTextNltk(complaint[4])
            print(complaints.index(complaint))
            complaint = complaint + (analysis,)
            complaints_senti.append(complaint)
            print(type(complaint))

        return render_template('officer-account.html', active='Display Complaint',
                               allComplaints=complaints_senti)

    elif request.args.get('opt') == "update_emergency_complaints":
        if request.args.get('update_id') is not None:
            update_id = request.args.get('update_id')
            stations = getAllStations()
            complaints = getEmergencyComplaint(update_id)
            # print(complaints)
            return render_template('officer-account.html', active='Update Emergency Complaint',
                                   complaintToUpdate=complaints, all_stations=stations)
        else:
            station_name = session['station_name']
            complaints = getAllEmergencyComplaintsOfStation(station_name)
            return render_template('officer-account.html', active='Update Emergency Complaint',
                                   allComplaints=complaints,
                                   complaintToUpdate=None)

    elif request.args.get('opt') == "display_emergency_complaints":
        station_name = session['station_name']
        complaints = getAllEmergencyComplaintsOfStation(station_name)
        # print(complaints)
        return render_template('officer-account.html', active='Display Emergency Complaint',
                               allComplaints=complaints)

    all_stations = getAllStations()
    return render_template('officer-account.html', active='Display Complaint', all_stations=all_stations)


@app.route('/update_complaint_officer', methods=['POST', 'GET'])
def update_complaint_officer():
    if not session['user_type'] == UserType.officer:
        return render_template('index.html', user=UserType)

    complaint_db_id = request.form['complaint_db_id']

    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    description = request.form['description']
    station_name = request.form['station_name']
    status = request.form['status']

    if updateComplaint(complaint_db_id, name, phone, address, description, station_name, status):
        return "<script>alert('Update Complaint successful.'); window.open(" \
               "'/officer_account?opt=update_complaints','_self')</script> "
    else:
        return "<script>alert('Fail to update Complaint.'); window.open(" \
               "'/officer_account','_self')</script> "


@app.route('/update_emergency_complaint_officer', methods=['POST', 'GET'])
def update_emergency_complaint_officer():
    if not session['user_type'] == UserType.officer:
        return render_template('index.html', user=UserType)

    complaint_db_id = request.form['complaint_db_id']

    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    description = request.form['description']
    station_name = request.form['station_name']
    status = request.form['status']

    if updateEmergencyComplaint(complaint_db_id, name, phone, address, description, station_name, status):
        return "<script>alert('Update Complaint successful.'); window.open(" \
               "'/officer_account?opt=update_emergency_complaints','_self')</script> "
    else:
        return "<script>alert('Fail to update Complaint.'); window.open(" \
               "'/officer_account','_self')</script> "


# ----------- officer end from here ------------------------


# citizen account start from here

@app.route('/citizen_login', methods=['POST', 'GET'])
def citizen_login():
    phone = request.form['phone']
    password = request.form['pass']
    u = citizenLogin(phone, password)
    print(u)

    if u is None:
        return "<script>alert('Phone or password did not match.'); window.open('/','_self')</script>"
    else:
        # uid, name, phone, psw, email, account_type, address, gender
        user = UserAccount()
        user.uid = u[0]
        user.name = u[1]
        user.phone = u[2]
        user.psw = [3]
        user.account_type = UserType.citizen

        session['user_type'] = UserType.citizen
        session['user_name'] = user.name
        session['user_id'] = user.uid
        session['phone'] = user.phone
        # print("redirected ..")
        return redirect("/citizen_account", code=302)


@app.route('/citizen_account')
def citizen_account():
    if not session['user_type'] == UserType.citizen:
        return render_template('index.html', user=UserType)

    if request.args.get('opt') is None or request.args.get('opt') == "citizen_profile":
        stations = getAllStations()
        usr_id = session['user_id']
        citizen = getCitizen(usr_id)
        return render_template('citizen-account.html', active='Citizen Profile', all_stations=stations,
                               citizenProfile=citizen)

    elif request.args.get('opt') == "update_password":
        stations = getAllStations()
        usr_id = session['user_id']
        citizen = getCitizen(usr_id)
        return render_template('citizen-account.html', active='Update Password',
                               all_stations=stations, citizenPasswordToUpdate=citizen)

    elif request.args.get('opt') == "display_citizen_complaint":
        citizen_phone = session['phone']
        citizen_complaints = getAllComplaintsOfCitizen(citizen_phone)
        return render_template('citizen-account.html', active='Display Complaints',
                               allComplaintsOfCitizen=citizen_complaints)

    elif request.args.get('opt') == "register_citizen_complaint":
        stations = getAllStations()
        usr_id = session['user_id']
        citizen = getCitizen(usr_id)
        return render_template('citizen-account.html', active='Register Complaint',
                               all_stations=stations, citizen=citizen)

    elif request.args.get('opt') == "register_citizen_emergency_complaint":
        stations = getAllStations()
        usr_id = session['user_id']
        citizen = getCitizen(usr_id)
        return render_template('citizen-account.html', active='Register Emergency Complaint',
                               all_stations=stations, citizen=citizen)

    elif request.args.get('opt') == "display_citizen_emergency_complaint":
        citizen_phone = session['phone']
        citizen_complaints = getAllEmergencyComplaintsOfCitizen(citizen_phone)
        return render_template('citizen-account.html', active='Display Emergency Complaint',
                               allComplaintsOfCitizen=citizen_complaints)

    elif request.args.get('opt') == "feedback_citizen":
        citizen_phone = session['phone']
        citizen_complaints = getAllEmergencyComplaintsOfCitizen(citizen_phone)
        return render_template('citizen-account.html', active='Feedback',
                               allComplaintsOfCitizen=citizen_complaints)

    stations = getAllStations()
    usr_id = session['user_id']
    citizen = getCitizen(usr_id)
    return render_template('citizen-account.html', active='Citizen Profile', all_stations=stations,
                           citizenProfile=citizen)


@app.route('/register_citizen', methods=['POST', 'GET'])
def register_citizen():
    name = request.form['name']
    phone = request.form['phone']
    psw = request.form['psw']
    address = request.form['address']
    station_name = request.form['station_name']

    if insert_citizen(name, phone, psw, address, station_name):
        phone = request.form['phone']
        password = request.form['pass']
        u = citizenLogin(phone, password)
        print(u)

        if u is None:
            return "<script>alert('Phone or password did not match.'); window.open('/','_self')</script>"
        else:
            user = UserAccount()
            user.uid = u[0]
            user.name = u[1]
            user.phone = u[2]
            user.psw = [3]
            user.account_type = UserType.citizen

            session['user_type'] = UserType.officer
            session['user_name'] = user.name
            session['user_id'] = user.uid
            session['phone'] = user.phone

            return "<script>alert('Register Citizen successful.'); window.open(" \
                   "'/citizen_account','_self')</script> "

    else:
        return "<script>alert('Fail to Register Citizen.'); window.open(" \
               "'/registration_citizen','_self')</script>"


@app.route('/update_citizen_password', methods=['POST', 'GET'])
def update_citizen_password():
    if not session['user_type'] == UserType.citizen:
        return render_template('index.html', user=UserType)
    officer_db_id = request.form['citizen_db_id']
    name = request.form['name']
    phone = request.form['phone']
    psw = request.form['psw']
    station_name = request.form['station_name']
    address = request.form['address']
    passwordnew = request.form['passwordnew']
    passwordrenew = request.form['passwordrenew']

    u = citizenLogin(phone, psw)
    print(u)

    if u is None:
        return "<script>alert('Old password did not match.'); window.open('/','_self')</script>"

    elif not passwordnew == passwordrenew:
        return "<script>alert('Passwords are not same.'); window.open(" \
               "'/citizen_account?opt=update_password','_self')</script> "

    elif updateCitizen(officer_db_id, name, phone, passwordnew, address, station_name):
        return "<script>alert('Citizen password update successful.'); window.open(" \
               "'/citizen_account?opt=citizen_profile','_self')</script> "
    else:
        return "<script>alert('Fail to update Citizen Password.'); window.open(" \
               "'/citizen_account?opt=update_password','_self')</script> "


@app.route('/update_citizen_profile', methods=['POST', 'GET'])
def update_citizen_profile():
    if not session['user_type'] == UserType.citizen:
        return render_template('index.html', user=UserType)
    officer_db_id = request.form['citizen_db_id']
    name = request.form['name']
    phone = request.form['phone']
    psw = request.form['pass']
    station_name = request.form['station_name']
    address = request.form['address']

    if updateCitizen(officer_db_id, name, phone, psw, address, station_name):
        return "<script>alert('Update Citizen profile successful.'); window.open(" \
               "'/citizen_account?opt=update_citizens','_self')</script> "
    else:
        return "<script>alert('Fail to update Citizen profile.'); window.open(" \
               "'/citizen_account','_self')</script> "


@app.route('/register_complaint', methods=['POST', 'GET'])
def register_complaint():
    if not session['user_type'] == UserType.citizen:
        return render_template('index.html', user=UserType)

    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    description = request.form['description']
    station_name = request.form['station_name']
    status = "registered"

    if insert_complaint(name, phone, address, description, station_name, status):
        return "<script>alert('Complaint registered successful.'); window.open(" \
               "'/citizen_account?opt=display_citizen_complaint','_self')</script> "
    else:
        return "<script>alert('Fail to register complaint.'); window.open(" \
               "'/citizen_account?opt=display_citizen_complaint','_self')</script>"


@app.route('/register_emergency_complaint', methods=['POST', 'GET'])
def register_emergency_complaint():
    if not session['user_type'] == UserType.citizen:
        return render_template('index.html', user=UserType)

    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    description = request.form['description']
    station_name = request.form['station_name']
    status = "registered"

    if insert_emergency_complaint(name, phone, address, description, station_name, status):
        return "<script>alert('Emergency complaint registered successful.'); window.open(" \
               "'/citizen_account?opt=display_citizen_emergency_complaint','_self')</script> "
    else:
        return "<script>alert('Fail to register emergency complaint.'); window.open(" \
               "'/citizen_account?opt=display_citizen_emergency_complaint','_self')</script>"


@app.route('/add_feedback_citizen', methods=['POST', 'GET'])
def add_feedback_citizen():
    if not session['user_type'] == UserType.citizen:
        return render_template('index.html', user=UserType)

    feedback = request.form['feedback']

    if insert_feedback(feedback):
        return "<script>alert('Feedback submit successful.'); window.open(" \
               "'/citizen_account','_self')</script> "
    else:
        return "<script>alert('Fail to submit Feedback.'); window.open(" \
               "'/citizen_account','_self')</script>"


# manage citizen end from here

# public-account start from here.

@app.route('/public_account')
def public_account():
    if request.args.get('opt') is None or request.args.get('opt') == "display_public_emergency_complaint":
        citizen_phone = 'public'
        citizen_complaints = getAllEmergencyComplaintsOfCitizen(citizen_phone)
        return render_template('public-account.html', active='Display Emergency Complaint',
                               allComplaintsOfCitizen=citizen_complaints)

    elif request.args.get('opt') == "register_public_emergency_complaint":
        stations = getAllStations()
        return render_template('public-account.html', active='Register Emergency Complaint',
                               all_stations=stations)

    elif request.args.get('opt') == "feedback_public":
        return render_template('public-account.html', active='Feedback')

    return render_template('index.html', user=UserType)


@app.route('/register_emergency_complaint_public', methods=['POST', 'GET'])
def register_emergency_complaint_public():
    name = request.form['name']
    phone = 'public'
    address = request.form['address']
    description = request.form['description']
    station_name = request.form['station_name']
    status = "registered"

    if insert_emergency_complaint(name, phone, address, description, station_name, status):
        return "<script>alert('Emergency complaint registered successful.'); window.open(" \
               "'/public_account?opt=display_public_emergency_complaint','_self')</script> "
    else:
        return "<script>alert('Fail to register emergency complaint.'); window.open(" \
               "'/public_account?opt=display_public_emergency_complaint','_self')</script>"


@app.route('/add_feedback_public', methods=['POST', 'GET'])
def add_feedback_public():
    feedback = request.form['feedback']

    if insert_feedback(feedback):
        return "<script>alert('Feedback submit successful.'); window.open(" \
               "'/public_account','_self')</script> "
    else:
        return "<script>alert('Fail to submit Feedback.'); window.open(" \
               "'/public_account','_self')</script>"


# manage public account end here


@app.route('/login')
def user_login():
    if request.args.get('type') == UserType.admin:
        return render_template('login.html', user_type=UserType.admin, submit_url="admin_login")

    elif request.args.get('type') == UserType.officer:
        return render_template('login.html', user_type=UserType.officer, submit_url="officer_login")

    elif request.args.get('type') == UserType.citizen:
        return render_template('login.html', user_type=UserType.citizen, submit_url="citizen_login")

    elif request.args.get('type') == UserType.public:
        session["user_type"] = UserType.public
        return redirect("/public", code=302)

    else:
        return redirect("/", code=302)



@app.route('/prediction', methods=['POST', 'GET'])
def prediction():

    result = None

    if request.method == 'POST':
        state = request.form['state']
        year_str = request.form['year']
        year = int(year_str)
        crime = request.form['crime']

        mystate_df = pd.read_csv("refined_by_state_year.csv")
        mystate_df = mystate_df.loc[mystate_df['STATE/UT'] == state]
        train, test = train_test_split(mystate_df, test_size=0.20)
        # Reshape index column to 2D array for .fit() method
        X_train = np.array(train['YEAR']).reshape(-1, 1)
        y_train = np.array(train[crime]).reshape(-1, 1)
        # Create LinearRegression Object
        model = LinearRegression()
        # Fit linear model using the train data set
        model.fit(X_train, y_train)
        # Create test arrays
        X_test = np.array([year]).reshape(-1, 1)
        y_test = np.array(test[crime]).reshape(-1, 1)
        y_pred = model.predict(X_test)

        results = []
        
        results.append("State: " + state)
        results.append("Year: " + year_str)
        results.append("Crime Type: " + crime)
        results.append("Prediction: " + str(y_pred[0][0]))



        result =  results

        
    crimes = [ "MURDER","ATTEMPT TO MURDER","CULPABLE HOMICIDE NOT AMOUNTING TO MURDER","RAPE","CUSTODIAL RAPE","OTHER RAPE",
            "KIDNAPPING & ABDUCTION","KIDNAPPING AND ABDUCTION OF WOMEN AND GIRLS","KIDNAPPING AND ABDUCTION OF OTHERS","DACOITY",
            "PREPARATION AND ASSEMBLY FOR DACOITY","ROBBERY","BURGLARY","THEFT","AUTO THEFT","OTHER THEFT","RIOTS","CRIMINAL BREACH OF TRUST",
            "CHEATING","COUNTERFIETING","ARSON","HURT/GREVIOUS HURT","DOWRY DEATHS","ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY",
            "INSULT TO MODESTY OF WOMEN","CRUELTY BY HUSBAND OR HIS RELATIVES","IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES","CAUSING DEATH BY NEGLIGENCE",
            "OTHER IPC CRIMES","TOTAL IPC CRIMES", ]
    
    states = ["ANDHRA PRADESH", "ARUNACHAL PRADESH", "ASSAM", "BIHAR", "CHHATTISGARH", "GOA", "GUJARAT", "HARYANA", \
            "HIMACHAL PRADESH", "JAMMU & KASHMIR", "JHARKHAND", "KARNATAKA", "KERALA", "MADHYA PRADESH",
            "MAHARASHTRA", \
            "MANIPUR", "MEGHALAYA", "MIZORAM", "NAGALAND", "ODISHA", "PUNJAB", "RAJASTHAN", "SIKKIM", "TAMIL NADU",
            "TRIPURA", \
            "UTTAR PRADESH", "UTTARAKHAND", "WEST BENGAL", "A & N ISLANDS", "CHANDIGARH", "D & N HAVELI",
            "DAMAN & DIU", "DELHI UT", "LAKSHADWEEP", "PUDUCHERRY"]


    return render_template('prediction.html', states=states, crimes = crimes, result = result)


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_type', None)
    session.pop('user_name', None)
    return "<script>alert('Logout complete.'); window.open('/','_self')</script>"



@app.route('/statics', methods= ['GET', 'POST'])
def statics():
    states = ["ANDHRA PRADESH", "ARUNACHAL PRADESH", "ASSAM", "BIHAR", "CHHATTISGARH", "GOA", "GUJARAT", "HARYANA", \
              "HIMACHAL PRADESH", "JAMMU & KASHMIR", "JHARKHAND", "KARNATAKA", "KERALA", "MADHYA PRADESH",
              "MAHARASHTRA", \
              "MANIPUR", "MEGHALAYA", "MIZORAM", "NAGALAND", "ODISHA", "PUNJAB", "RAJASTHAN", "SIKKIM", "TAMIL NADU",
              "TRIPURA", \
              "UTTAR PRADESH", "UTTARAKHAND", "WEST BENGAL", "A & N ISLANDS", "CHANDIGARH", "D & N HAVELI",
              "DAMAN & DIU", "DELHI UT", "LAKSHADWEEP", "PUDUCHERRY"]

    years = ["2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012"]

    if request.args.get('year') is None:
        current_year = years[0]
    else:
        if request.args.get('year') in years:
            current_year = request.args.get('year')
        else:
            current_year = years[0]

    if request.args.get('state') is None:
        current_state = states[0]
    else:
        if request.args.get('state') in states:
            current_state = request.args.get('state')
        else:
            current_state = states[0]

    rvYears = years
    rvYears.reverse()
    print(rvYears)

    return render_template('statics.html', user=UserType, dataYears=years,
                           dataStates=states, selected_year=current_year, selected_state=current_state, reverseYears=rvYears)
    #return render_template('.html')


@app.route('/livedetection', methods= ['GET','POST'])
def livedetection():
    return render_template("face-detect.html")


def generate(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n') 

@app.route("/video_feed")
def video_feed():
    return Response(generate(VideoCamera()),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/video")
def video():
    return render_template("video.html")





if __name__ == '__main__':

    print(">>>#to install nltk\n>>>import nltk\nnltk.download('punkt')")
    app.run(debug=True)
