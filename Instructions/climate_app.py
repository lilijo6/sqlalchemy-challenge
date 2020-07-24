import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
from dateutil.relativedelta import relativedelta


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite",
    connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

#Create our session (link) from Python to the DB
session = Session(engine)

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
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/<start><br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    

    # Perform a query to retrieve the data and precipitation scores
    precipitation = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date).all()

    session.close()

    #Create a dictionary from the precipitation data and append to a list
    precipitation_list = []

    for date, prcp in precipitation:
        precipitation_dictionary = {}
        precipitation_dictionary[date] = prcp
        precipitation_list.append(precipitation_dictionary)

    #Return the JSON representation on dictionary
    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations") 
def stations():
    
    # Create our session (link) from Python to the DB
    stations = session.query(station.station).all()

    #close session
    session.close()

    #list the names
    station_list= list(np.ravel(stations))

    #Return the JSON representation of your dictionary.
    return jsonify(station_list) 

@app.route("/api/v1.0/tobs")
def tobs_data():
    
    # Query the dates and temperature observations of the most active station for the last year of data.
    #Find latest date in the database
    last_observation=session.query(measurement).order_by(measurement.date.desc()).first()
    last_date=last_observation.date
    
    #Calculate the date 1 year from max date
    one_year_ago=(dt.datetime.strptime(last_date, '%Y-%m-%d') - relativedelta(years=1)).date()
    
    #The most active station query
    active_station=session.query(measurement).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()
    most_active_station=active_station.station
    
    # Perform a query to retrieve the date and tobs value for most active station
    result=session.query(measurement.date,measurement.tobs).filter(measurement.station==most_active_station)\
    .filter(measurement.date>=one_year_ago).filter(measurement.date<=last_date)\
    .all()

    #Close session after use
    session.close()

    # Convert list of tuples into dictionary with date as id and tobs as value
    station_tobs=dict(result)
    return jsonify(station_tobs)

@app.route("/api/v1.0/<start>")
def start_date(start):

    #Find min, average and max temperature observation for dates equal to greater than start date passed in the API
    start=session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs))\
    .filter(func.strftime("%Y-%m-%d", measurement.date) >=start)\
    .all()
 
    #Close session after use
    session.close()

    start_list=[]
    for tmin, tavg, tmax in start:
        start_dict = {}
        start_dict["min_temp"]= tmin
        start_dict["avg_temp"]= tavg
        start_dict["max_temp"]= tmax
        start_list.append(start_dict)
    
    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def stats_Start_end(start,end):
    
    #Find min, average and max temperature observation for dates equal to greater than start date passed in the API
    result=session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs))\
    .filter(func.strftime("%Y-%m-%d", measurement.date) >=start)\
    .filter(func.strftime("%Y-%m-%d", measurement.date) <=end)\
    .all()
    #Close session after use
    session.close()

    start_end_list=[]
    #dict(data)

    for tmin, tavg, tmax in result:
        start_end_dict = {}
        start_end_dict["min_temp"] = tmin
        start_end_dict["avg_temp"] = tavg
        start_end_dict["max_temp"] = tmax
        start_end_list.append(start_end_dict)
    
   #Return the JSON representation of your dictionary.
    return jsonify(start_end_list)


if __name__ == "__main__":
    app.run(debug=True)





