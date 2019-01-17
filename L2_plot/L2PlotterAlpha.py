import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import csv
import sys
import glob, os
import re

'''
plots data
'''
#volRat = input('What reduced volume?: ')
#alpha = input('What alpha?: ')
#folder = raw_input('Enter folder to plot L2 Norms: ')
plt.rc('font', family='sans-serif')
plt.rc('xtick', labelsize='small')
plt.rc('ytick', labelsize='small')
folder = sys.argv[1]
os.chdir(folder)
fig = plt.figure(figsize=(6, 6))
legEntries = []
numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
for fn in sorted(glob.glob("*.csv")):
#read in data from file
    with open(fn, 'rb') as csvfile:
        #ignore first 7 lines then get Ca and ignore rest of header
        for i in range(14):
            tmp = csvfile.next()
            if "Alpha" in tmp:
                rx = re.compile(numeric_const_pattern, re.VERBOSE)
                legEntries.append(rx.findall(tmp))

        reader = csv.DictReader(filter(lambda row: row[0].isdigit() and row[4].isdigit(), csvfile), fieldnames = ("time", "Sxz", "N1", "N2", "L2VN", "ures", "aspect ratio"))
        dataList = [] # list of dictionaries
        timeList = [] # list of the time values
        for row in reader: #ignores repeated times
            tmpTime = float(row["time"])
            if tmpTime not in timeList:
                timeList.append(float(tmpTime))
                dataList.append(row)

#moving all the data to lists for plotting
#spatial data in form of outer index = row num, inner index = step
    time = []
    norm = []
    for row in dataList:
        time.append(float(row['time']))
        norm.append(float(row['L2VN']))
    
# plotting norm vs time
    plt.semilogy(time, norm)

    #plt.title('Reduced Volume {0}, Viscosity Ratio = {1}, alpha = {2}'.format(volRat, viscRat, alpha))
    plt.xlabel('Time', fontsize=15)
    plt.ylabel('$L_2$ Norm of Normal Velocity', fontsize=15)
    #plt.ylim( (10**-3,10**-2) )
    plt.grid(True)
    #plt.ylim( (10**-3,10**-2) )
    legend = plt.legend(legEntries, title="flow type parameter", fontsize=12)
    plt.tight_layout()
    plt.savefig('L2NormPlot.pdf',format='pdf', dpi=1000)
