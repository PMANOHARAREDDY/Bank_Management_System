from flask import Flask, render_template, request, session, redirect, flash
import sqlite3
import werkzeug
from threading import Thread


conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS banking (ID INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(256), pin VARCHAR(256),  balance INTEGER, loan INTEGER, interest INTEGER)')
conn.close()
app = Flask('')
app.secret_key = "abc"

@app.route("/", methods=["GET", "POST"])
def hello_world():
    session["loggedin"] = "no"
    if session["loggedin"] == "yes":
        return redirect("/info")
    else:
        if request.method == "GET":
            return render_template("index.html")
        else:
            mode = request.form.get('mode')
            username = request.form.get('username')
            password = request.form.get('password')

            if mode == "register":
                password = werkzeug.security.generate_password_hash(password)
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                c.execute('INSERT INTO banking (name, pin, balance, loan, interest) VALUES ("{}", "{}", {}, {}, {})'.format(username, password, 0,0,0))
                conn.commit()
                row=c.execute("SELECT * FROM banking WHERE name='{}' AND pin='{}' AND balance={} AND loan={} AND interest={}".format(username, password,0,0,0))
                target=row.fetchone()
                session["loggedin"]="yes"
                session["id"]=target[0]
                conn.close()
                return redirect("/info")
            else:

                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                row = c.execute("SELECT * FROM banking WHERE name = '{}'".format(username))
                targets = row.fetchall()
                for target in targets:
                    if werkzeug.security.check_password_hash(target[2], password):
                        session["loggedin"] = "yes"
                        session["id"] = target[0]
                        conn.close()
                        return redirect("/info")
                return render_template("index.html", error="INCORRECT USERNAME OR PASSWORD")

            return render_template("index.html")

@app.route("/info")
def info():
    if session["loggedin"] == "yes":
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        row = c.execute("SELECT * FROM banking WHERE id = {}".format(session['id']))
        target = row.fetchone()
        conn.close()
        if target[5]==0:
         return render_template("balance.html", accountinfo= target)
        else:
          return render_template("afterloan.html", accountinfo=target)
    else:
        return redirect("/")

      
@app.route("/afterloan")
def afterloan():
    if session["loggedin"] == "yes":
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        row = c.execute("SELECT * FROM banking WHERE id = {}".format(session['id']))
        target = row.fetchone()
        conn.close()
        return render_template("afterloan.html", accountinfo= target)
    else:
        return redirect("/")


@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    if session["loggedin"] == "yes":
        if request.method == "GET":
            return render_template("deposit.html", accid=session["id"])
        else:
            amount = int(request.form.get('money'))
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            row = c.execute("SELECT * FROM banking WHERE id = {}".format(session['id']))
            target = row.fetchone()
            c.execute("UPDATE banking SET balance = {} WHERE id = {}".format(target[3]+amount, session['id']))
            conn.commit()
            conn.close()
            return redirect("/info")
    else:
        return redirect("/")

@app.route("/withdraw",  methods=["GET", "POST"])
def withdraw():
        if session["loggedin"] == "yes":
            if request.method == "GET":
                return render_template("withdraw.html", accid=session["id"])
            else:
                amount = int(request.form.get('money'))
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                row = c.execute("SELECT * FROM banking WHERE id = {}".format(session['id']))
                target = row.fetchone()
                if target[3] - amount < 0:
                    return render_template("withdraw.html", error="Insufficient funds")
                c.execute("UPDATE banking SET balance = {} WHERE id = {}".format(target[3]-amount, session['id']))
                conn.commit()
                conn.close()
                return redirect("/info")
        else:
            return redirect("/")


@app.route("/transfer",  methods=["GET", "POST"])
def transfer():
        if session["loggedin"] == "yes":
            if request.method == "GET":
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                row = c.execute("SELECT * FROM banking ")
                target = row.fetchall()
                for tar in target:
                    if tar[0] == session['id']:
                        target.remove(tar)
                conn.close()
                print(target)
                return render_template("transfer.html", accid=session["id"], targets=target)
            else:
                accid = int(request.form.get('accid'))
                amount = int(request.form.get('money'))
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                row = c.execute("SELECT * FROM banking WHERE id = {}".format(session['id']))
                target = row.fetchone()
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                row = c.execute("SELECT * FROM banking ")
                accids = row.fetchall()
                for tar in accids:
                    if tar[0] == session['id']:
                        accids.remove(tar)
                
                if target[3] - amount < 0:
                    return render_template("transfer.html", error="Insufficient funds",targets=accids)
                c.execute("UPDATE banking SET balance = {} WHERE id = {}".format(target[3]-amount, session['id']))
                conn.commit()
                row = c.execute("SELECT * FROM banking WHERE id = {}".format(accid))
                target = row.fetchone()
                c.execute("UPDATE banking SET balance = {} WHERE id = {}".format(target[3]+amount, accid))
                conn.commit()
                conn.close()
                return redirect("/info")
        else:
            return redirect("/")


@app.route("/loanrepay",  methods=["GET", "POST"])
def loanrepay():
        if session["loggedin"] == "yes":
            if request.method == "GET":
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                row = c.execute("SELECT * FROM banking ")
                target = row.fetchall()
                for tar in target:
                    if tar[4] == session['id']:
                        target.remove(tar)
                conn.close()
                print(target)
                return render_template("loanrepay.html", accid=session["id"], targets=target)
            else:
                accid = session["id"]
                amount = int(request.form.get('money'))
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                row = c.execute("SELECT * FROM banking WHERE id = {}".format(session['id']))
                target = row.fetchone()
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                row = c.execute("SELECT * FROM banking ")
                accids = row.fetchall()
                for tar in accids:
                    if tar[4] == session['id']:
                        accids.remove(tar)
                
                if target[3] - amount < 0:
                    return render_template("loanrepay.html", error="Insufficient funds",targets=accids)
                if target[5]-amount>=0:
                  c.execute("UPDATE banking SET balance = {} WHERE id = {}".format(target[3]-amount, session['id']))
                  conn.commit()
                  row = c.execute("SELECT * FROM banking WHERE id = {}".format(accid))
                  target = row.fetchone()
                  c.execute("UPDATE banking SET interest = {} WHERE id = {}".format(target[5]-amount, accid))
                  if (target[4]-amount)>0:
                    c.execute("UPDATE banking SET loan = {} WHERE id = {}".format(target[4]-amount, accid))
                  else:
                    c.execute("UPDATE banking SET loan = {} WHERE id = {}".format(0, accid))
                  
                  conn.commit()
                  conn.close()
                  return redirect("/info")
                else:
                  return render_template("loanrepay.html",error="Repayment cannot be greater than the loan amount")
        else:
            return redirect("/")


          

@app.route("/loan",  methods=["GET", "POST"])
def loan():
        if session["loggedin"] == "yes":
            if request.method == "GET":
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                row = c.execute("SELECT * FROM banking ")
                target = row.fetchall()
                for tar in target:
                    if tar[0] == session['id']:
                        target.remove(tar)
                conn.close()
                print(target)
                return render_template("loan.html", accid=session["id"], targets=target)
            else:
                accid = session["id"]
                amount = int(request.form.get('money'))
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                row = c.execute("SELECT * FROM banking WHERE id = {}".format(session['id']))
                target = row.fetchone()
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                row = c.execute("SELECT * FROM banking ")
                accids = row.fetchall()
                for tar in accids:
                    if tar[0] == session['id']:
                        accids.remove(tar)
                
                if target[3] + amount >= 1000000:
                    return render_template("loan.html", error="Not Enough Credit Score",targets=accids)
                elif target[5] > 0:
                  return render_template("loan.html",error="You already have an active loan")
                row = c.execute("SELECT * FROM banking WHERE id = {}".format(accid))
                target = row.fetchone()
                c.execute("UPDATE banking SET balance = {} WHERE id = {}".format(target[3]+amount, accid))
                c.execute("UPDATE banking SET loan = {} WHERE id = {}".format(target[4]+amount, accid))
                c.execute("UPDATE banking SET interest = {} WHERE id = {}".format(((target[4]+amount)*(1.12)//1), accid))
                conn.commit()
                conn.close()
                flash("You have been credited with the loan at 12% per annum")
                return redirect("/afterloan")

        else:
            return redirect("/")




def run():
  app.run(host='0.0.0.0',port=9016)
  app.run(debug=True)

def keep_alive():
    t = Thread(target=run)
    t.start()
    
keep_alive()
