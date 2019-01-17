import numpy as np
import matplotlib.pyplot as plt
import csv
import sys
import glob, os

'''
plots data
'''
os.chdir("./data/")
fig = plt.figure()
names = []
for fn in sorted(glob.glob("*.csv")):
#read in data from file
  with open(fn, 'rb') as csvfile:
    #opens csv file and makes dict reader
    header = csvfile.readline()
    reader = csv.DictReader(filter(lambda row: row[0]!='#',csvfile))
    dataList = list(reader)#list of dictionaries

  names.append(header[11:15])
  time = []
  length = []

#moving all the data to lists for plotting
#spatial data in form of outer index = row num, inner index = step
  for row in dataList:
    time.append(float(row['time']))
    length.append(float(row['length']))
  
  for i in range(len(length)):
    length[i] -= length[len(length) - 1];
    
# plotting length vs time
  plt.semilogy(time, length)

plt.title('Vesicle Relaxation Self Similar')
plt.xlabel('Time ($t/t_s$)')
plt.ylabel('Long axis length (L/a) - final length')
legend = plt.legend(names, title="Reduced Volume")
plt.savefig('RelaxCa10SS.pdf',format='pdf', dpi=1000)
