from flask import Flask,render_template,request, redirect, url_for, session,flash
import psycopg2 as dbapi2
from datetime import datetime
import os


def executeSQL(sqlCode,operation):
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        url = os.getenv("DATABASE_URL")
        connection = dbapi2.connect(url)
        cursor = connection.cursor()
        
        # Execute SQL code
        cursor.execute(sqlCode)
        if(operation == "select"):
            data = cursor.fetchall()
            cursor.close()
            connection.close()
            return data
        if(operation == "insert" or "update"):
            connection.commit()
            cursor.close()
            connection.close()

        
    
    except (Exception, dbapi2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

app = Flask(__name__)
app.secret_key = "super secret key"


@app.route("/")
@app.route("/home")
def home_page():
    return render_template("homepage.html")

@app.route("/data", methods=['GET','POST'])
def data_page():
    node=1
    if request.method == "GET":
        dataSQL = "Select * from public.node_" + str(node) + " ORDER BY id DESC LIMIT 10"
        datas = executeSQL(dataSQL, "select")
        return render_template("data.html", datas = datas)
    if request.method == "POST":
        node = request.form['node_id']
        dataSQL = "Select * from public.node_" + str(node) + " ORDER BY id DESC LIMIT 10"
        datas = executeSQL(dataSQL, "select")
        return render_template("data.html", datas = datas)

@app.route("/nodeCommand", methods=['GET','POST'])
def nodeCommand_page():
    if request.method == "POST":
        node = request.form['node']
        try:
            fan = request.form['fan']
        except:
            fan = "off"
        try:
            lamp = request.form['lamp']
        except:
            lamp = "off"
        try:
            roof = request.form['roof']
        except:
            roof = "off"
        try:
            water = request.form['water']
        except:
            water = "off"
        print(node,fan,lamp,roof,water)
        query = "UPDATE public.state SET fan= '"+ fan +"', lamp= '"+ lamp +"', roof= '"+roof+"', water= '"+water+"' WHERE node= '"+node+"';"
        executeSQL(query,"insert")
        #return redirect(url_for('home_page'))
        return render_template("nodeCommand.html")
    else:
         return render_template("nodeCommand.html")

if __name__ == "__main__":
    app.run()
