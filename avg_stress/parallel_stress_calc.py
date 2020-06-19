"""
Runs avg_stress_calc.py on all directories in folder
Parallelized with Process by making each directory a separate process
"""
from multiprocessing import Process
import sys
import glob
import avg_stress_calc as ASC

def main():
    parentFolder = sys.argv[1]

    childFolders = glob.glob(parentFolder + "*/")
    processes = [
        Process(target=ASC.ext_run, args=(childFolders[i],), kwargs={"skip_mod":10})
        for i in range(len(childFolders))
    ]

    for i in range(len(processes)):
        processes[i].start()
        print("Started {}".format(childFolders[i]))

    for p in processes:
        p.join()

    print("Finished")


if __name__ == "__main__":
    main()
