from multiprocessing import Process
import sys
import os
import glob
import liss_plot as lp

def main():
    """
    Runs liss_plot on all of the folders in a parent folder
    """
    parentFolder = sys.argv[1]

    childFolders = glob.glob(parentFolder + "/*")
    childNames = [os.path.basename(x) for x in childFolders]

    processes = [Process(target=lp.plot_liss, args=(childFolders[i], childNames[i])) for i in range(len(childFolders))]

    for i in range(len(processes)):
        processes[i].start()
        print("Started {}".format(childNames[i]))

    for p in processes:
        p.join()

    print("Finished")

if __name__ == "__main__":
    main()
