import sys
import glob
import os
import errno

folder = sys.argv[1]
os.chdir(folder)
substring_list = ["error", "PETSC", "application", "User", "Libraries", "See", "Configure"] #the substrings I want to get rid of

path = "FormattedData/"
try:  
    os.mkdir(path)
except OSError as e:  
    print ("Directory ({}) already exists".format(path))
    if e.errno != errno.EEXIST:
        raise
else:  
    print ("Successfully created the directory {} ".format(path))

print(glob.glob("*.csv"))
for fn in glob.glob("*.csv"):
    with open(fn, 'r') as csvfile:
        lines = csvfile.readlines()

# list comprehension, removes lines with substring in it 
    trunLines = [x for x in lines if not any(substring in x for substring in substring_list)]     

    tmp = fn[0:-4]
    with open(path + tmp + "_truc.csv", 'w') as f:
        for item in trunLines:
            f.write("{}".format(item) )    

