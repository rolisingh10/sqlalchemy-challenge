# Import the dependencies.
import numpy as np
import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import matplotlib.dates as mdates
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
os.chdir(os.path.dirname(os.path.realpath(__file__)))

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)
# reflect the tables


# Save references to each table
Mm = Base.classes.measurement
St = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/tstats/&lt;start&gt;<br>"
        f"/api/v1.0/tstats/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Find the most recent date in the data set.

    session.query(Mm.date).order_by(Mm.date.desc()).first()
    # Calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=1*365)

    # Perform a query to retrieve the data and precipitation scores
    Query_result =session.query(Mm.date,Mm.prcp).\
    filter(Mm.date >= '2016-08-23').\
    order_by(Mm.date).all()
    
    all_precipitation = []
    for date, prcp in Query_result:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)

    # Design a query to find all the stations in the dataset
    station_data = session.query(St.station).all()
    # change tuple to list
    station_list = list(np.ravel(station_data))
    session.close()
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
        session = Session(engine)
    # Using the most active station id
# Query the last 12 months of temperature observation data for this station 
        Year_temperature = session.query( Mm.tobs, Mm.date).\
                   filter(Mm.station =='USC00519281').\
                   filter(Mm.date >= '2016-08-23').all()
     
        all_tobs = []
        for date, tobs in Year_temperature:
             tobs_dict = {}
             tobs_dict["date"] = date
             tobs_dict["tobs"] = tobs
             all_tobs.append(tobs_dict)
        session.close()     
        return jsonify(all_tobs)

@app.route("/api/v1.0/tstats/<start>")
@app.route("/api/v1.0/tstats/<start>/<end>")       
def tstats(start, end=None):
    session = Session(engine)
    if not end:
        end = dt.date.max

    result = session.query(func.min(Mm.tobs), func.avg(Mm.tobs), func.max(Mm.tobs)).\
                filter(Mm.date >= start).\
                filter(Mm.date <= end).\
                all()
     
     # Create a dictionary from the row data and append to a list of start_date_tobs
    start_date_tobs = []
    for min, avg, max in result:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min_temp"] = min
        start_date_tobs_dict["avg_temp"] = avg
        start_date_tobs_dict["max_temp"] = max
        start_date_tobs.append(start_date_tobs_dict) 
        session.close()
    return jsonify(start_date_tobs)
     











if __name__ == '__main__':
    app.run(debug=True)