import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import csv
import sys
import glob, os
import re

"""
Plots the L2Norm of normal velocity data from the vesicle output files in csv format
"""

def main():
    plt.rc('font', family='sans-serif')
    plt.rc('xtick', labelsize='small')
    plt.rc('ytick', labelsize='small')
    folder = sys.argv[1]
    titleStr = raw_input("Figure Title: ")
    os.chdir(folder)
    fig = plt.figure(figsize=(6, 6))
    legEntries = []
    for fn in sorted(glob.glob("*.csv")):
        with open(fn, 'rb') as csvfile:

            for i in range(14):
                tmp = csvfile.next()
                if(tmp.find("Capillary Number")!= -1):
                    legEntries.append(tmp[19:26])# get Ca

            reader = csv.DictReader(filter(lambda row: row[0].isdigit() and row[4].isdigit(), csvfile), fieldnames = ("time", "Sxz", "N1", "N2", "L2VN", "ures", "length"))
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
            norm.append(float(row['length']))
        
    # plotting norm vs time
        plt.semilogy(time, norm)

        plt.title(titleStr)
        plt.xlabel('Time', fontsize=15)
        plt.ylabel('$L_2$ Norm of Normal Velocity', fontsize=15)
        #plt.ylim( (10**-3,10**-2) )
        plt.grid(True)
        #plt.ylim( (10**-3,10**-2) )
        legend = plt.legend(legEntries, title="Capillary Numbers", fontsize=12)
        plt.tight_layout()
        plt.savefig('LenPlot{}.pdf'.format(titleStr),format='pdf', dpi=1000)


def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

if __name__ == "__main__":
    main()
