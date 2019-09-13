from multiprocessing import Process
import sys
import os
import glob
import length_xy as lxy

def main():
    """
    Runs length_xy on all of the folders in a parent folder
    """
    parentFolder = sys.argv[1]

    childFolders = glob.glob(parentFolder + "/*")
    childNames = [os.path.basename(x) for x in childFolders]

    processes = [Process(target=lxy.len_plot, args=(childFolders[i], childNames[i])) for i in range(len(childFolders))]

    for i in range(len(processes)):
        processes[i].start()
        print("Started {}".format(childNames[i]))

    for p in processes:
        p.join()

    print("Finished")

if __name__ == "__main__":
    main()
