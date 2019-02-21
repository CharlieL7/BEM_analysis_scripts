import csv
import sys
import glob
import matplotlib.pyplot as plt

'''
Plot the steady-state length data
'''

def main():
    folder = sys.argv[1]
    textstr = "reduced volume = 0.65\n" + "viscosity ratio = 1.00"
    leg_title = "alpha"
    fn_out = "test"
    fig = plt.figure()
    ax = fig.add_subplot(111)

    for f_name in sorted(glob.glob("{}/*.tsv".format(folder))):
        Ca_s_list, length_list, params = get_data(f_name)
        ax.plot(Ca_s_list, length_list, 'o', label=params["alpha"])
    
    ax.set_title("Steady-state lengths")
    ax.set_xlabel(r"Ca $\cdot \sqrt{\alpha}}$")
    ax.set_ylabel(r"S-S length $(\frac{L}{a_0})$")
    ax.legend(title=leg_title, bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0, prop={"size": 10})

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.savefig("{}.pdf".format(fn_out), format="pdf")
    plt.close()

def get_data(filename):
    """
    Reads the data from the tsv file and returns a named tuple with the data values
    """
    # read header data:
    with open(filename) as csv_file:
        is_header = True
        while is_header:
            last_pos = csv_file.tell()
            tmp_line = csv_file.readline()
            if tmp_line.find('#') == 0:
                eq_pos = tmp_line.find('=')
                if tmp_line.find("alpha") != -1 and eq_pos != -1:
                    alpha = float(tmp_line[eq_pos+1:])
                elif tmp_line.find("viscRat") != -1 and eq_pos != -1:
                    visc_rat = float(tmp_line[eq_pos+1:])
                elif tmp_line.find("volRat") != -1 and eq_pos != -1:
                    vol_rat = float(tmp_line[eq_pos+1:])
                else:
                    print("Unrecognized header line: {}".format(tmp_line))

            else:
                is_header = False
                csv_file.seek(last_pos)

        reader = csv.DictReader(csv_file, delimiter="\t")
        data_list = list(reader)

    # moving all the data to lists for plotting
    params = {"alpha": alpha, "visc_rat": visc_rat, "vol_rat": vol_rat}
    Ca_s_list = []
    length_list = []
    for row in data_list:
        Ca_s_list.append(float(row["Ca_s"]))
        length_list.append(float(row["SS_length"]))
    try:
        return (Ca_s_list, length_list, params)
    except NameError:
        print("missing a header variable")
        return None


if __name__ == "__main__":
    main()
