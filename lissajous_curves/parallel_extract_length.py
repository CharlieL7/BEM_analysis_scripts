"""
Runs extract_length_data.py on all directories in folder
Parallelized with Process
"""
from multiprocessing import Process
import sys
import os
import glob
import extract_length_data as ELD

def main():
    parentFolder = sys.argv[1]

    childFolders = glob.glob(parentFolder + "/*")
    childNames = [os.path.basename(x) + ".csv" for x in childFolders]

    processes = [
        Process(target=ELD.ext_run, args=(childFolders[i], childNames[i]))
        for i in range(len(childFolders))
    ]

    for i in range(len(processes)):
        processes[i].start()
        print("Started {}".format(childNames[i]))

    for p in processes:
        p.join()

    print("Finished")

if __name__ == "__main__":
    main()
