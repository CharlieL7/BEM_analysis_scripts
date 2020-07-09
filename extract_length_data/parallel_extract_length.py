"""
Runs extract_length_data.py on all directories in folder
Parallelized with Process by making each direcoty a separate process
"""
from multiprocessing import Process
import os
import glob
import argparse as argp
import extract_length_data as ELD

def main():
    parser = argp.ArgumentParser(description="Runs several extral_length_data jobs in parallel")
    parser.add_argument("in_dir", help="folder of tecdat files")
    parser.add_argument("mod", help="modulus for skipping files")
    args = parser.parse_args()
    parentFolder = args.in_dir
    parentFolder = os.path.join(parentFolder, '')
    childFolders = glob.glob(parentFolder + "*/")
    processes = [
        Process(target=ELD.ext_run, args=(childFolders[i], int(args.mod),))
        for i in range(len(childFolders))
    ]

    for i, proc in enumerate(processes):
        proc.start()
        print("Started {}".format(childFolders[i]))

    for p in processes:
        p.join()

    print("Finished")


if __name__ == "__main__":
    main()
