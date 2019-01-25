import csv
import glob
import matplotlib.pyplot as plt

'''
plots data
'''
fig = plt.figure()
for fn in sorted(glob.glob("./data/*.csv")):
    #read in data from file
    with open(fn, 'rb') as csvfile:
        #opens csv file and makes dict reader
        reader = csv.DictReader(filter(lambda row: row[0] != '#', csvfile), skipinitialspace=True)
        dataList = list(reader)#list of dictionaries

    times = []
    lengths = []
    print dataList[0]

#moving all the data to lists for plotting
#spatial data in form of outer index = row num, inner index = step
    for row in dataList:
        times.append(float(row["time"]))
        lengths.append(float(row["length"]))

# plotting length vs time
    plt.plot(times, lengths)

plt.title('De/Ca comparison')
plt.xlabel('time')
plt.ylabel('Long axis length (L/a)')
legend = plt.legend(["De = 1", "De = 10"], title="Reduced Volume")
plt.savefig('length_plot.pdf', format='pdf', dpi=1000)
