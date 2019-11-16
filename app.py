import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#weather app
app = Flask(__name__)


today_date = (session.query(Measurement.date)
                .order_by(Measurement.date.desc())
                .first())
today_date = list(np.ravel(today_date))[0]

today_date = dt.datetime.strptime(today_date, '%Y-%m-%d')
current_year = int(dt.datetime.strftime(today_date, '%Y'))
current_month = int(dt.datetime.strftime(today_date, '%m'))
current_day = int(dt.datetime.strftime(today_date, '%d'))

last_year = dt.date(current_year, current_month, current_day) - dt.timedelta(days=365)
last_year = dt.datetime.strftime(last_year, '%Y-%m-%d')




@app.route("/")
def home():
    return (f"Surf's Up Dude!: Hawaii's Climate API<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/stations     => station observation <br/>"
            f"/api/v1.0/precipitaton => preceipitation data<br/>"
            f"/api/v1.0/temperature  => temperature data<br/>"
            f"/api/v1.0/start => start date<br/>"
            f"/api/v1.0/datesearch/startEnd => end date<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


@app.route("/api/v1.0/stations")
def stations():
    info = session.query(Station.name).all()
    total_stations = list(np.ravel(info))
    return jsonify(total_stations)



@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > last_year)
                      .order_by(Measurement.date)
                      .all())

    precipData = []
    for result in results:
        precipDict = {result.date: result.prcp, "Station": result.station}
        precipData.append(precipDict)

    return jsonify(precipData)

@app.route("/api/v1.0/temperature")
def temperature():

    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
        .filter(Measurement.date > last_year)
        .order_by(Measurement.date)
        .all())

    tempData = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        tempData.append(tempDict)

    return jsonify(tempData)




@app.route("/api/v1.0/start")
def start(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route("/api/v1.0/datesearch/startEnd")
def startEnd(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)