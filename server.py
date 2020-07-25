from flask import Flask,render_template,request, redirect, url_for, session,flash,Response
import psycopg2 as dbapi2
from datetime import datetime
import os
import io
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


def executeSQL(sqlCode,operation):
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        url = os.getenv("HEROKU_POSTGRESQL_BLUE_URL")
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

gFeature = "temparature"
gNode = "1"

@app.route("/")
@app.route("/home")
def home_page():
    return render_template("homepage.html")

@app.route('/plot.png')
def plot_png():
    global gFeature
    global gNode
    graphSQL = "select id, " + gFeature + " from node_" + gNode + " ORDER BY id DESC LIMIT 60"
    graphData = executeSQL(graphSQL, "select")
    arr = np.array(graphData)
    t = arr[:,0]
    s = arr[:,1]

    fig, ax = plt.subplots()
    ax.plot(t, s)
    if gFeature == "temparature":
        gFeature = "temperature"

    ymin = np.min(s)
    ymax = np.max(s)
    ax.set(xlabel='time',title="Node " + gNode +" "+ gFeature)
    ax.set_ylim([ymin -25,ymax + 25])
    ax.grid()
    plt.gcf().autofmt_xdate()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route("/data", methods=['GET','POST'])
def data_page():
    if request.method == "GET":
        graphCheck = False
        return render_template("data.html",graphCheck = graphCheck)
    if request.method == "POST":
        graphCheck = True
        global gNode
        global gFeature
        gNode = request.form['node_id']
        gFeature = request.form['feature']
        dataSQL = "Select * from public.node_" + gNode + " ORDER BY id DESC LIMIT 10"
        datas = executeSQL(dataSQL, "select")
        return render_template("data.html", datas = datas, graphCheck = graphCheck)

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
