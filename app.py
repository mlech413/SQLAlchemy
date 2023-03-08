import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Create Database Connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect Database into ORM classes
Base = automap_base()
Base.prepare(engine)
# Map classes

Measurement = Base.classes.measurement
Station = Base.classes.station
# create a session

session = Session(engine)
# ceate flask app

app = Flask(__name__)

# Home page
@app.route("/")
def welcome():
    return (
        f"CLIMATE ANALYSIS API<br>"
        f"Honalulu, Hawaii 01/01/2010 - 08/23/2017<br/>"
        f"<p>Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date<br/>"
        f"/api/v1.0/start date/end date<br/>"
        f"<p>'start date' and 'end date' MUST be in the format MMDDYYY.<p/>"
    )

# Route to show 1 year of precipitation values
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Calculate 1 year back
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Get date and precip values for past year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
   
    # close session
    session.close()
    
    # create dictionary of values
    precip = { date: prcp for date, prcp in precipitation}
   
   # return the results
    return jsonify(precip)

# Route to show list of all stations
@app.route("/api/v1.0/stations")
def stations():
    
    # Get all stations
    stations = session.query(Station.station).all()
    
    # close session
    session.close()
    
    # create list of values
    station_list = list(np.ravel(stations))
    
    # return the results
    return jsonify(station_list)

# Route to show 1 year of temperature observations at most active station USC00519281
@app.route("/api/v1.0/tobs")
def tobs():
    
    # Calculate 1 year back
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    # Get temp observations for past year at station USC00519281
    temperature_observations = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    
    # close session
    session.close()
    
    # create list of values
    temp_obs = list(np.ravel(temperature_observations))
    
    # return the results
    return jsonify(temp_obs)

# Two routes - either just stating date, or both starting and ending dates
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date_range(start = None, end = None):
    date_range = [func.min(Measurement.tobs), func.round(func.avg(Measurement.tobs),1), func.max(Measurement.tobs)]
    
    # Start time is always an input here
    start = dt.datetime.strptime(start, "%m%d%Y")
    
    # If only start date is provided
    if not end:
    
        # Query with only start time
        results = session.query(*date_range).\
            filter(Measurement.date >= start).all()
    
    # Else, if both start and end dates are provided
    else:
    
        # End time was provided
        end = dt.datetime.strptime(end, "%m%d%Y")
    
        # QUery using both times    
        results = session.query(*date_range).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    
    # close session
    session.close()
    
    # create list of values
    temps = list(np.ravel(results))
    
    # return the results
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)