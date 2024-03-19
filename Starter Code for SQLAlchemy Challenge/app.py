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

    # Precipitation query
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago)

    # Turn precipitation query results into data frame
    precipitation_df = pd.DataFrame(precipitation, columns = ("Date", "Precipitation"))
    
    # Turn data frame into dictionary
    precipitation_dict = precipitation_df.set_index('Date')['Precipitation'].to_dict()

    # Jsonify dictionary
    return jsonify(precipitation_dict)

    # Close session
    session.close()



@app.route("/api/v1.0/stations")
def stations():

    # Query the stations
    station_query = session.query(Station.station)

    # Empty list for stations
    station_list = []
    
    # Iterate through station_query and append each station to station_list
    for result in station_query:
        station_list.append(result.station)

    # Jsonify station_list
    return jsonify(station_list)

    # Close session
    session.close()



@app.route("/api/v1.0/tobs")
def tobs():

    # Query temperature data, filter results to get everything from one_year_ago to the most recent date,
    # then filter to get results for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).\
        filter(Measurement.station == h_station[0])

    # Turn query results into a data frame
    temperature_df = pd.DataFrame(temperature_data, columns = ("Date", "Tobs"))

    # Get Tobs data from data frame and turn it into a list
    temperatures = temperature_df["Tobs"].tolist()

    # Jsonify the temperatures list
    return jsonify(temperatures)

    # Close session
    session.close()



@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_stop(start, end):
    # Date values for start and end must be in the form 'YYYY-MM-DD'.
    # For first route (remember to type 'None' where <end> would be):
    if end == None:
        
        # Query the temperature observations and filter by start date
        desired_data = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date >= start)

        # Turn query results into data frame  
        desired_data_df = pd.DataFrame(desired_data, columns = ('Tobs', 'Date'))


    # For second route:    
    else:
        # Query the temperature observations, filter by start date through end date.
        desired_data = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date >= start).\
            filter(Measurement.date <= end)
        
        # Turn query results into data frame
        desired_data_df = pd.DataFrame(desired_data, columns = ('Tobs', 'Date'))
            
    # Average temperature (tavg), minimum temperature (tmin), maximum temperature (tmax)
    tavg = desired_data_df['Tobs'].mean()
    tmin = min(desired_data_df['Tobs'])
    tmax = max(desired_data_df['Tobs'])

    # Close session
    session.close()

    # Puts tavg, tmin, and tmax into list of f strings
    results_list = [f"Average Temperature: {tavg}", f"Minimum Temperature: {tmin}", f"Maximum Temperature: {tmax}"]

    # results_list is returned
    return results_list

    


if __name__ == '__main__':
    app.run()