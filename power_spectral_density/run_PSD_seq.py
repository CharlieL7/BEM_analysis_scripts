from multiprocessing import Process
import sys
import os
import glob
import PSD_plot as psd

def main():
    """
    Runs plot_corr_PSD on all of the folders in a parent folder
    """
    parentFolder = sys.argv[1]

    childFolders = glob.glob(parentFolder + "/*")
    childNames = [os.path.basename(x) for x in childFolders]

    x = psd.PSD()
    for i in range(len(childFolders)):
        x.plot_corr_PSD(childFolders[i], childNames[i])

if __name__ == "__main__":
    main()
