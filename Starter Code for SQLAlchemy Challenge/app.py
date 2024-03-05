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


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start <br/>"
        f"/api/v1.0/start/end <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago)
    
    precipitation_df = pd.DataFrame(precipitation, columns = ("Date", "Precipitation"))
    
    precipitation_dict = precipitation_df.set_index('Date')['Precipitation'].to_dict()

    return jsonify(precipitation_dict)

    session.close()

@app.route("/api/v1.0/stations")
def stations():

    
    station_query = session.query(Station.station)

    station_df = pd.DataFrame(station_query, columns = ("Station"))
    
    station_list = station_df['Station'].tolist()

    return jsonify(station_list)

    session.close()


@app.route("/api/v1.0/tobs")
def tobs():

    temperature_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).\
    filter(Measurement.station == f_station[0])

    temperature_df = pd.DataFrame(temperature_data, columns = ("Date", "Tobs"))

    temperatures = temperature_df["Tobs"].tolist()

    return jsonify(temperatures)

    session.close()

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_stop():
    start = input("Input a start date in the form YYYY-MM-DD" )
    end = input("Optional: Input an end date in the form YYYY-MM-DD. Otherwise input NA." )
        
    if end != 'NA':
            
        desired_data = session.query(Measurement.tobs).filter(Measurement.date >= start)\
        .filter(Measurement.date <= end)
            
        desired_df = pd.DataFrame(desired_data, columns = ('Tobs'))
            
        tavg = desired_df['Tobs'].mean()
        tmin = min(desired_df['Tobs'])
        tmax = max(desired_df['Tobs'])
        
    else:

        desired_data = session.query(Measurement.tobs).filter(Measurement.date >= start)
            
        desired_df = pd.DataFrame(desired_data, columns = ('Tobs'))
            
        tavg = desired_df['Tobs'].mean()
        tmin = min(desired_df['Tobs'])
        tmax = max(desired_df['Tobs'])


if __name__ == '__main__':
    app.run()