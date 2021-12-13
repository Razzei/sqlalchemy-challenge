import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [measurement.date, measurement.prcp]
    result = session.query(*sel).all()

    precipitation = []
    for date, prcp in result:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = prcp
        precipitation.append(precip_dict)

    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    result = session.query(*sel).all()
    session.close()

    stations = []
    for station, name, lat, lon, el in result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    sel = [measurement.date, measurement.tobs, measurement.prcp]
    result = session.query(*sel).filter(measurement.date >= '2016-08-23').filter(measurement.station=='USC00519281').order_by(measurement.date).all()
    tobs_list = []

    for prcp, date, tobs in result:
        tobs_dict = {}
        tobs_dict["prcp"] = prcp
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)
    result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()

    summary = []
    for min, avg, max in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        summary.append(tobs_dict)

    return jsonify(summary)

@app.route('/api/v1.0/<start>/<end>')
def get_t_start_stop(start, end):
    session = Session(engine)
    result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    summary = []
    for min,avg,max in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        summary.append(tobs_dict)

    return jsonify(summary)

if __name__ == "__main__":
    app.run(debug=True)