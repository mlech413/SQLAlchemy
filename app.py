import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

header_text =    (
        f"CLIMATE ANALYSIS API<br>"
        f"Honalulu, Hawaii 01/01/2010 - 08/23/2017<br/>"
        f"<p>Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date<br/>"
        f"/api/v1.0/start date/end date<br/>"
        f"<p>'start date' and 'end date' date must be in the format MMDDYYY.<p/>"
    )

@app.route("/")
def welcome():
    return (
        header_text
        # f"CLIMATE ANALYSIS API<br>"
        # f"Honalulu, Hawaii 01/01/2010 - 08/23/2017<br/>"
        # f"<p>Available Routes:<br/>"
        # f"/api/v1.0/precipitation<br/>"
        # f"/api/v1.0/stations<br/>"
        # f"/api/v1.0/tobs<br/>"
        # f"/api/v1.0/start date<br/>"
        # f"/api/v1.0/start date/end date<br/>"
        # f"<p>'start date' and 'end date' date must be in the format MMDDYYY.<p/>"
    )

# Route to show 1 year of precipitation values
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate 1 year back
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Get date and precip values for past year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    
    session.close()
    precip = { date: prcp for date, prcp in precipitation}

    return (
        f"{header_text}"
        f"{jsonify(precip)}"
        )

# Route to show list of all stations
@app.route("/api/v1.0/stations")
def stations():

    stations = session.query(Station.station).all()
    
    session.close()

    station_list = list(np.ravel(stations))

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
    
    session.close()

    temp_obs = list(np.ravel(temperature_observations))

    return jsonify(temp_obs)

# Two route - either just stating date, or both starting and ending dates
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date_range(start = None, end = None):
    date_range = [func.min(Measurement.tobs), func.round(func.avg(Measurement.tobs),1), func.max(Measurement.tobs)]

    # Always have start time
    start = dt.datetime.strptime(start, "%m%d%Y")

    # If only start date is provided
    if not end:
        # Query with only start time
        results = session.query(*date_range).\
            filter(Measurement.date >= start).all()
    
    # If both start and end dates are provided
    else:
        # End time was provided
        end = dt.datetime.strptime(end, "%m%d%Y")
        # QUery using both times    
        results = session.query(*date_range).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
       
    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)