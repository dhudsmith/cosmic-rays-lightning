#!/usr/bin/python
# -*- coding: utf-8 -*-

#####################################################################################
# Imports and setup
#####################################################################################

import sqlite3 as lite
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas import Series, DataFrame, Panel


# pd.set_printoptions(max_rows=15) # limit maximimum number of rows printed

#####################################################################################
# Program description:
#####################################################################################

# Author: D. Hudson Smith
# Date: April 1, 2016

#####################################################################################
# Global Variables:
#####################################################################################

#####################################################################################
# Named tuples:
#####################################################################################

#####################################################################################
# Function definitions:
#####################################################################################

def querySQL(con, station, datemin=0, datemax=99999999):
    """Performs the SQL query to find all records from "station" with dates in [datemin,  datemax)
     "SELECT Date, Hour, Count FROM Data WHERE Station = 'station' AND Date BETWEEN 'datemin' AND 'datemax' ORDER BY Date, Hour"

    Arguments:
    con -- the database connection
    station -- a string denoting the station
    datemin -- an integer of the form yyyymmdd denoting the earliest day
    datemax -- an integer of the form yyyymmdd denoting the lastest day

    Return:
    A tuple of tuples. One per hour. The tuples have the form: (pandas.datetime, count)
    """

    # fetch the data
    with con:
        cur = con.cursor()

        # Get some data
        cur.execute("SELECT Date, Hour, Count FROM Data WHERE Station = ? AND Date BETWEEN ? AND ? ORDER BY Date, Hour",
                    (station, datemin-1, datemax))

        data = np.array(cur.fetchall())

    # date and time to pandas.datetime
    data2 = []
    for x in data:
        timestring = str(x[0]) + str(x[1]-1).zfill(2) + "0000"
        time = pd.to_datetime(datetime.strptime(timestring, '%Y%m%d%H%M%S'))

        data2.append((time, x[2]))

    return np.array(data2)


#####################################################################################
# Program execution
#####################################################################################
#
# get some cosmic ray data of sql database:
# Initialize the connection
con = lite.connect('CRData.db')

startdate = 19990101
enddate = 19990201
data = querySQL(con, "MEXICO", startdate, enddate)

# Get the date range
startdatepd = pd.to_datetime(datetime.strptime(str(startdate), '%Y%m%d'))
enddatepd = pd.to_datetime(datetime.strptime(str(enddate), '%Y%m%d'))
dates = pd.date_range(startdatepd, enddatepd, freq='H')

# Build the time series
ts = Series(data[:,1], index = data[:,0])
ts.plot()
plt.show()