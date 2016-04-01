#!/usr/bin/python
# -*- coding: utf-8 -*-

#####################################################################################
# Imports
#####################################################################################

import glob
import StringIO
import sqlite3 as lite
import collections

#####################################################################################
# Program description:
#####################################################################################

# Author: D. Hudson Smith
# Date: March 31, 2016

# This program gets all files from the World Data Center for Cosmic Rays (WDCCR),
# converts the data into a convenient form, and stores all the data in a local SQL database.
# WDCCR website: http://center.stelab.nagoya-u.ac.jp/WDCCR/
# ftp server is: ftp://ftp.stelab.nagoya-u.ac.jp/
# All of the relevant files are stored in /pub/WDCCR/STATIONS/
# The server hosts the data in three forms, LONGFORMAT, SHORTFORMAT, and CARDFORMAT
# This code is designed to parse the LONGFORMAT data and will fail on files that
# do not meet the precise formatting characteristics of these files which is outlined below.

# Description of files on the ftp server:
# Each file corresponds to one station within some time window, containing an integer number of months
# The months are stored in blocks of 4096 bytes with no padding
# The one-month blocks are of the form:
# ----------------------------------------
# Bytes Format  Description
# ----------------------------------------
# 1-6	A6	    First six characters of abbreviated station name
# 7-13	A7	    Comments on data, e.g.:
#               N64	NM-64neutron monitor
#               P	Pressure-corrected data
#               C	Counts
#               S	Scaled counts
#               A	Absolute values
# 14	I1	    1: Hourly data
#               2: Two-hour data
# 15-16	I2	    Year-1900 before 1999, Year-2000 after 2000
# 17-18	I2	    Month
# 19-46	4F7.2	Latitude, Longitude, Altitude, Vertical cut-off rigidity
# 47-74	4F7.1	Scaling Factor(SF),UT of the beginning of the first data of a
#               given day (for 1-hour data measured in the interval from
#               00:00 to 01:00, this value is 0), Constant to be added to the
#               tabulated data, Monthly average
#               Real Count = (tabulated value + Constant)*SF
# 75-364	A290	Information for data usage (see below)
# 365-370	A6	    Warning for discontinuity in monthly data (by 1988)
#                   or information on data including contact point
# 371-376	3I2	    Date of revision (YYMMDD)
# 377-4096	744I5	Hourly data (24 x 31=744). 99999 for "no data"

# Description of SQL Database:
# The database, called "CRData.db". All cosmic ray data points are inserted into a
# table called "Data". "Data" has the following fieldsL
# Station TEXT, Date INT, Hour INT, Lat REAL, Lon REAL, Alt REAL, Warn TEXT, Count INT

#####################################################################################
# Global Variables:
#####################################################################################

# Length in bytes of one month
monthlength = 4096

#####################################################################################
# Named tuples:
#####################################################################################

# Tuple called "MonthData" represents the cosmic ray data for one month
# Length: 8
# Fields: "Station" (str), "year" (int), "month" (int), "lat" (float),
#   "lon" (float), "alt" (float) "warn" (str), "realcounts" (list<int>)
monthtuple = collections.namedtuple('MonthData', 'station year month lat lon alt warn realcounts')

# Tuple called "Datum" represents the cosmic ray data for one hour at a specific station
# Length: 8
# Fields: "Station" (str), "date" (int, yyyymmdd), "hour" (int), "lat" (float),
#   "lon" (float), "alt" (float) "warn" (str), "realcounts" (list<int>)
datumtuple = collections.namedtuple('Datum', 'station date hour lat lon alt warn realcount')


#####################################################################################
# Function definitions:
#####################################################################################

def splitfile(filename):
    """Given a full filename containing multiple months
    return a list of StringIO objects for each month

    Arguments:
    filename --  a string representing a full file name

    Return:
    A list of StringIO objects to be read bytewise
    """

    with open(filename, "rb") as f:
        # Read in the file and chop any funny business off the end
        allstr = f.read().rstrip()
        monthstrls = allstr.split('\n')
        monthstrls = [x.rstrip() for x in monthstrls]
        monthbufls = (StringIO.StringIO(x) for x in monthstrls)

        # Remove the last empty element
        # monthbufls.pop()

        return monthbufls


def readmonth(file):
    """Read one month of data and returns a dataumtuple

    Arguments:
    n -- nth month in the list. Must be less than the number of months
    buf -- the binary buffer object to be scanned

    Return: datumtuple named tuple
    """

    # Protect against invalid months
    if (file.len != monthlength):
        print "Not a valid month!: ", file.len, "\n", file.read()
        return None

    # If we've reached the end of the file the station bytes will return empty

    file.seek(0)

    station = file.read(6)
    file.read(13 - 7 + 1)
    file.read(1)

    year = int(file.read(2))
    month = int(file.read(2))

    lat = float(file.read(7))
    lon = float(file.read(7))
    alt = float(file.read(7))
    file.read(7)

    scalefactor = float(file.read(7))
    file.read(7)
    const = float(file.read(7))
    file.read(7)

    file.read(364 - 75 + 1)

    warning = file.read(370 - 365 + 1)

    file.read(376 - 371 + 1)

    # Read the hourly data into a list. Each entry is 5 bytes long.
    rawcounts = []
    for i in range(0, 744):
        rawcounts.append(int(file.read(5)))

    # Calculate the hourly real counts (see above documentation). Missing data represented by -1
    realcounts = []
    for x in rawcounts:
        if x == 99999:
            realcounts.append(-1)
        else:
            realcounts.append(int((x + const) * scalefactor))

    # Combine relevant data into tuple for output
    thismonth = monthtuple(station=station, year=year, month=month, lat=lat, lon=lon, alt=alt, warn=warning,
                           realcounts=realcounts)

    return thismonth


def coercemonth(namedmonthtuple):
    """Converts a monthtuple into a list of datumtuple

    Arguments:
    monthtuple -- monthtuple

    Return:
    list of datumtuple
    """

    # Protect against invalid months, marked by None
    if namedmonthtuple is None:
        return None

    # An empty list to store the tuples
    datatuples = []

    year = namedmonthtuple.year
    if year <= 16:
        year += 2000
    else:
        year += 1900

    # i should range from 1 to 744 and it denotes the hour of month with i=1 corresponding to the 12:00am through 1:00am on the
    # first day of the month and i=744 corresponding to 11:00pm through 11:59pm on the 31st day of the month
    for i in range(0, len(namedmonthtuple.realcounts)):
        day = int(1 + i / 24)
        date = int(str(year) + str(namedmonthtuple.month).zfill(2) + str(day).zfill(2))
        hour = 1 + i % 24

        thisdatum = datumtuple(station=namedmonthtuple.station, date=date, hour=hour, lat=namedmonthtuple.lat,
                               lon=namedmonthtuple.lon, alt=namedmonthtuple.alt, warn=namedmonthtuple.warn,
                               realcount=namedmonthtuple.realcounts[i])

        datatuples.append(thisdatum)

    return datatuples


def cleanup(datatuples):
    """Cleanup a list of data tuples.
     1) Throw out "None" entries
     2) Throw out missing values. Throwing out missing
    values automatically removes imaginary days since they are represented as missing
    values.

    Arguments:
    datatuples -- list of datumtuple to be cleaned

    Return:
    cleaned list of datumtuple
    """
    if datatuples is not None:
        listmissing = []
        for i in range(0, len(datatuples)):
            if datatuples[i] is None:
                listmissing.append(i)
            elif datatuples[i].realcount < 0:
                listmissing.append(i)

        for i in sorted(listmissing, reverse=True):
            del datatuples[i]

        return datatuples

    else:
        return None


#####################################################################################
# Program execution
#####################################################################################

# ----------------------------------------
# File Access and data coercion
# ----------------------------------------

path = "ftpmirror/*/LONGFORMAT/*.txt"

data = []
for file in glob.iglob(path):
    months = splitfile(file)
    for month in months:
        datum = cleanup(coercemonth(readmonth(month)))
        if datum is not None:
            data += datum

# ----------------------------------------
# SQL insertion
# ----------------------------------------

# Initialize the connection
con = lite.connect('CRData.db')

with con:
    cur = con.cursor()

    # create the table if it doesn't exist
    cur.execute(
        "CREATE TABLE IF NOT EXISTS Data(Id INTEGER PRIMARY KEY, Station TEXT, Date INT, Hour INT, Lat REAL, Lon REAL, Alt REAL, Warn TEXT, Count INT)")

    # insert all the tuples into the database
    cur.executemany("INSERT INTO Data(Station,Date,Hour,Lat,Lon,Alt,Warn,Count) VALUES(?,?,?,?,?,?,?,?)",
                    data)
