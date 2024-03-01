# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

# reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.metadata.create_all(engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(bind=engine)
session

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


hawaii_measurements = pd.read_csv("..\\Starter Code for SQLAlchemy Challenge\\Resources\\hawaii_measurements.csv")
most_recent_date = hawaii_measurements["date"].max()
one_year_ago = datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
one_year_ago = one_year_ago.strftime('%Y-%m-%d')

f_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
    order_by(desc(func.count(Measurement.station))).first()

f_station_max = session.query(Measurement.station, func.max(Measurement.tobs)).group_by(Measurement.station).\
    order_by(desc(func.count(Measurement.station))).first()

f_station_min = session.query(Measurement.station, func.min(Measurement.tobs)).group_by(Measurement.station).\
    order_by(desc(func.count(Measurement.station))).first()

f_station_avg = session.query(Measurement.station, func.avg(Measurement.tobs)).group_by(Measurement.station).\
    order_by(desc(func.count(Measurement.station))).first()


temperature_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).\
    filter(Measurement.station == f_station[0])

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available routes:"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago)

    precipitation_dict = {}

    for date, prcp in precipitation:
        precipitation_dict[date] = prcp

    return jsonify(precipitation_dict)

    session.close()

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)
    
    station_list = list(session.query(Station.station))

    return jsonify(station_list)

    session.close()


@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)

    temperature_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).\
    filter(Measurement.station == f_station[0])

    temperatures = []

    for date, tobs in temperature_data:
        temperatures.append(tobs)

    return jsonify(temperatures)

    session.close()

#@app.route("/api/v1.0/<start>")
#def start():
    

    


#@app.route("/api/v1.0/<start>/<end>")
#def start_stop():

session.close()