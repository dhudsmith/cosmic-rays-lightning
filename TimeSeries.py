#!/usr/bin/python
# -*- coding: utf-8 -*-

#####################################################################################
# Imports and setup
#####################################################################################

import sqlite3 as lite
import datetime
import pandas as pd
import numpy as np
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
    """Performs the SQL query
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
                    (station, datemin, datemax))

        data = cur.fetchall()

    # date and time to pandas.datetime
    data2 = []
    for x in data:
        time = datetime.datetime.strptime(str(x[0]) + str(x[1]).zfill(2) + "0000", '%Y%m%d%H%M%S')
        print time
        # time = str(x[0]) + str(x[1]).zfill(2)
        data2.append((time, x[2]))

    return data2


#####################################################################################
# Program execution
#####################################################################################

# get some cosmic ray data of sql database:
# Initialize the connection
con = lite.connect('CRData.db')

data = querySQL(con, "MEXICO", 19990101, 19990105)
print type(data)

for tup in data:
    print type(tup[0]), " ", type(tup[1]), " ", tup
