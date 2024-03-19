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
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Read in hawaii_measurements file
hawaii_measurements = pd.read_csv("..\\Starter Code for SQLAlchemy Challenge\\Resources\\hawaii_measurements.csv")

# Most recent date in the data set
most_recent_date = hawaii_measurements["date"].max()

# One year prior to the most recent date
one_year_ago = datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

# Formatting
one_year_ago = one_year_ago.strftime('%Y-%m-%d')



# Most active station
h_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
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

    station_list = []
    
    for result in station_query:
        station_list.append(result.station)

    return jsonify(station_list)

    session.close()



@app.route("/api/v1.0/tobs")
def tobs():

    temperature_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).\
    filter(Measurement.station == h_station[0])

    temperature_df = pd.DataFrame(temperature_data, columns = ("Date", "Tobs"))

    temperatures = temperature_df["Tobs"].tolist()

    return jsonify(temperatures)

    session.close()



@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_stop(start, end):
    
    if end == None:

        desired_data = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date >= start)
            
        desired_data_df = pd.DataFrame(desired_data, columns = ('Tobs', 'Date'))
        
    else:

        desired_data = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date >= start).\
            filter(Measurement.date <= end)
            
        desired_data_df = pd.DataFrame(desired_data, columns = ('Tobs', 'Date'))
            
    
    tavg = desired_data_df['Tobs'].mean()
    tmin = min(desired_data_df['Tobs'])
    tmax = max(desired_data_df['Tobs'])

    session.close()

    results_list = [f"Average Temperature: {tavg}", f"Minimum Temperature: {tmin}", f"Maximum Temperature: {tmax}"]

    return results_list

    


if __name__ == '__main__':
    app.run()