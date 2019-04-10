import csv
import sys
import glob
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

'''
Plot the steady-state Taylor deformation data
'''

def main():
    folder = sys.argv[1]
    ca_s_val = sys.argv[2]
    leg_title = r"$\lambda$"
    fn_out = "test"
    data_list = get_data(folder)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    visc_rats = ["0.010", "0.500", "1.000", "5.000"]
    marker_dict = {"0.010":".", "0.500":"s", "1.000":"p", "5.000":"*"}
    ca_data = [y for y in data_list if float(y["Ca_s"]) == float(ca_s_val)]
    for visc_rat in visc_rats:
        alphas = []
        Ds = []
        for data in ca_data:
            if data["visc_rat"] == visc_rat:
                alphas.append(float(data["alpha"]))
                Ds.append(float(data["D"]))
        ax.plot(alphas, Ds, marker=marker_dict[visc_rat], linestyle="None", label=visc_rat)

    ax.set_xlabel(r"$\alpha$ (flow type)")
    ax.set_ylabel(r"Taylor parameter $(\frac{L-B}{L+B})$")
    ax.set_xlim(0., 1.1)
    ax.set_ylim(0., 1.)
    ax.legend(title=leg_title, bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0, prop={"size": 10})

    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.savefig("{}.pdf".format(fn_out), format="pdf")
    plt.close()

def get_data(filename):
    """
    Reads the data from the tsv file and returns a list of 
    """
    # read header data:
    with open(filename) as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        data_list = list(reader)
    return data_list

if __name__ == "__main__":
    main()
