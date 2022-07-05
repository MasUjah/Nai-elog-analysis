import numpy as np
import pandas as pd
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, messagebox
import linecache
import sys
import os
import ntpath
import shutil
from datetime import datetime

def InputFunction():

    while True:
        try:
            promptList = [
                "(1) Enter an output directory (e.g. 'Documents' or 'Desktop'; An input-specific directory will be created automatically): \n -> ",
                "\r(2) Enter a data input filepath (~.csv): \n -> ",
                ]

            methods = {
                'dialog': '[filedialog.askdirectory(title=promptList[0]), '
                          'filedialog.askopenfilename(title=promptList[1])]'
                          ,
                'manual': '[input(i) for i in promptList]'
            }

            method_input = 0
            while method_input not in methods:
                method_input = input("Method of path selection ('dialog' or 'manual'):")
                if method_input == 'dialog':
                    Tk().withdraw()
                    messagebox.showinfo(title="Input information",
                                        message=''.join(['NOTE\n\r'] + [i for i in promptList]))
                if method_input not in methods:
                    print('\n\rPlease input a correct option!')

            Tk().withdraw()
            return OutputFileConstructor(eval(methods[method_input]))

        except:
            print("Error occurred\n\r")

def OutputFileConstructor(pathlist):

    correct_dir_sep = ""
    wrong_dir_sep = ""

    if "\\" in pathlist[0]:
        correct_dir_sep = "\\"
        wrong_dir_sep = "/"
    else:
        wrong_dir_sep = "\\"
        correct_dir_sep = "/"

    name_and_type = os.path.basename(pathlist[1]).split('.')

    pathlist[0] = os.path.join(pathlist[0],
                               f"Status - {name_and_type[0]} ({name_and_type[1]}) - [{datetime.now().strftime('(date) %d_%m_%Y (time) %H_%M_%S')}]").replace(wrong_dir_sep, correct_dir_sep)


    try:
        shutil.rmtree(pathlist[0])
    except OSError as e:
        pass


    os.makedirs(pathlist[0])

    return pathlist[0] + correct_dir_sep, pathlist[1], os.path.join(pathlist[0], "Output.txt").replace(wrong_dir_sep, correct_dir_sep)
'''
Plot the histograms
'''

'''Histogram #1: plot histogram of voltages when log(gain)=4, interpolated from gain curve'''


# data are all strings, need to convert column "Gain Offset" to a float array without uncertainty values
def offset_cleanup(df):
    offset = df['Gain Offset']
    offsetPar = np.zeros(len(offset))  # create an empty set to store data in for loop
    for i in range(len(offset)):
        line = offset[i]
        if isinstance(line, str):  # numbers are stored as string, "NaN"'s are float.
            count = line.index('+')  # find index of '+'
            offsetPar[i] = line[:count]  # only keep digits before the found index, to get rid of uncertainty value
        else:
            offsetPar[i] = offset[i]
        i += 1
    return offsetPar
    # now offsetPar list contains no uncertainty value

def slope_cleanup(df):
    slope = df['Gain Slope']
    slopePar = np.zeros(len(slope))
    i = 0
    for i in range(len(slope)):
        line = slope[i]
        if isinstance(line, str):
            if len(line) >= 8:
                count = line.index('+')
                slopePar[i] = line[:count]
            else:  # some don't have "+", so we can directly use the data
                slopePar[i] = line[:8]
        else:
            slopePar[i] = slope[i]
        i += 1
    return slopePar


# now slopePar list contains no  uncertainty value

def curvature_cleanup(df):
    sat = df['Gain Saturation']
    curvaturePar = np.zeros(len(sat))
    for i in range(len(sat)):
        line = sat[i]
        if isinstance(line, str):
            # count = line.index('+')
            count = line.index('e') + 4
            curvaturePar[i] = line[:count]
        else:
            curvaturePar[i] = sat[i]
        i += 1
    return curvaturePar
    # now curvaturePar list contains no uncertainty value

# to find voltage when log(gain)=-3.5
def get_voltages(gain, df):  # function output depends on gain value
    voltList = []
    for i in range(df.shape[0]):
        curvature = curvature_cleanup(df)
        slope = slope_cleanup(df)
        offset = offset_cleanup(df)
        a = curvature[i]
        b = slope[i]
        c = offset[i] - gain  # gain is log(gain)
        coeff = [a, b, c]
        roots = np.roots(coeff)
        voltList.append(roots[1])
    print(voltList)
    return voltList  # a list of interpolated voltage values for all crystals is created
    


# plot the voltage value, at log(gain=-3.5), as a histogram.
# Crytals with similar voltage values will be grouped together in experiment later on.
def make_volt_hist(df, output_directory):
    volt_data = get_voltages(-3.5, df)
    plt.hist(volt_data, bins=range(620, 950, 10), stacked=True, facecolor='blue', ec='black')
    plt.title("Voltages (Log(G)=-3.5)")
    plt.xlabel('Voltage')
    plt.xticks(range(620, 950, 50))  # Range can be changed
    plt.ylabel('Counts')
    plt.savefig(output_directory + 'Voltages (Log(G)=-3.5).png')
    plt.show()


'''Histogram #2:137Cs Position 3 Peak Resolution'''


def res_cleanup(df):
    res = df['137Cs Position 3 Peak Resolution']
    resPar = np.zeros(len(res))
    for i in range(len(res)):  # getting rid of uncertainty values
        line = res[i]
        if isinstance(line, str):
            count = line.index('.')
            resPar[i] = line[:count]
        else:
            resPar[i] = res[i]
        i += 1
    resList = resPar.astype(np.float)  # convert string array to float array
    return resList



# this function makes plot#2, a histogram of energy resolution
def make_res_hist(output_directory, df):
    resList = res_cleanup(df)
    plt.hist(resList, bins=range(20, 46, 2), stacked=True, facecolor='blue', ec='black')
    plt.title("137Cs Energy Resolution")
    plt.xlabel('Calibrated Energy (keV)')
    plt.xticks(range(20, 46, 2))
    plt.ylabel('Counts')
    plt.savefig(output_directory + '137Cs Energy Resolution.png')
    plt.show()


'''Histogram #3:137Cs Total Energy Variation'''


def var_cleanup(df):
    '''
    var = df['137Cs Total Energy Variation']
    varPar = np.zeros(len(var))
    print(df)
    for i in range(len(var)):  # getting ride of uncertainty values

        print(var[i])
        line = var[i]

        # if isinstance(line,str):
        # count = line.index('')
        # varPar[i] = line[:count]
        if line[-1:] == 'V':
            count = line.index('V')
            var[i] = line[:count - 2]
        else:
            var[i] = line

        i += 1
    varList = varPar.astype(np.float)
    return varList
    '''
    var = df['137Cs Total Energy Variation']
    varPar = np.zeros(len(var))
    #   print(df)
    for i in range(len(var)):  # getting ride of uncertainty values
        line = var[i]
        print(line)
        if isinstance(line, str):
            #            count = line.index('')
            #            print("count",count, "line",line, line[:count])
            #            varPar[i] = float(line[:count])
            line = line.replace("keV", "")
            line = line.replace("KeV", "")
            varPar[i] = float(line)
        #        if line[-1:]=='V':
        #                count = line.index('V')
        #                varPar[i] = line[:count-2]
        else:
            varPar[i] = line
            continue
        i += 1
    varList = varPar.astype(np.float)
    return varList


def make_var_hist(output_directory, df):
    varList = var_cleanup(df)
    plt.hist(varList, bins=range(0, 56, 2), stacked=True, facecolor='blue', ec='black')
    plt.title("137Cs Peak Energy Variation with Source Position")
    plt.xlabel('Calibrated Energy (keV)')
    plt.xticks(range(0, 56, 5))
    plt.ylabel('Counts')
    plt.yticks(np.arange(0, 25, step=5))
    plt.savefig(output_directory + '137Cs Peak Energy Variation with Source Position.png')
    plt.show()

'''
make 2D plots
'''

'''2D plot#1: Resolution vs Variation '''


def res_var_2d(output_directory, df):
    resList = res_cleanup(df)
    varList = var_cleanup(df)
    plt.hist2d(resList, varList, bins=(11, 12), range=[[20, 42], [0, 60]], cmap='binary')
    #     print(max(resList))
    #     print(varList)
    #     print(max(varList))
    plt.colorbar(label='number of xtals', cmap='binary')
    plt.xlabel("137Cs Position 3 Peak Resolution(keV)")
    plt.ylabel("137Cs Total Energy Variation(keV)")
    plt.xticks(range(20, 44, 2))
    plt.yticks(range(0, 65, 5))
    plt.title("Energy Variation vs Peak Resolution")
    plt.savefig(output_directory + 'Energy Variation vs Peak Resolution.png', dpi=100)
    plt.show()



'''2D plot #2: Resolution vs voltage '''


def res_volt_2d(output_directory, df):
    resList = res_cleanup(df)
    plt.hist2d(resList, get_voltages(-3.5, df), bins=(11, 10), range=[[20, 42], [660, 990]], cmap='binary')
    plt.colorbar(label='number of xtals', cmap='binary')
    plt.xlabel("137Cs Position 3 Peak Resolution(keV)")
    plt.ylabel("Voltages (Log(G)=-3.5)")
    plt.xticks(range(20, 44, 2))
    plt.yticks(range(660, 990, 30))
    plt.title("Gain vs Peak Resolution")
    plt.savefig(output_directory + 'Gain vs Peak Resolution.png', dpi=100)
    plt.show()


'''2D plot #3: variation vs voltage '''


def var_volt_2d(output_directory, df):
    varList = var_cleanup(df)
    plt.hist2d(varList, get_voltages(-3.5, df), bins=(12, 10), range=[[0, 60], [660, 960]], cmap='binary')
    # print(max(varList))
    plt.colorbar(label='number of xtals', cmap='binary')
    plt.xlabel("137Cs Total Energy Variation(keV)")
    plt.ylabel("Voltages (Log(G)=-3.5)")
    plt.xticks(range(0, 65, 5))
    plt.yticks(range(660, 990, 30))
    plt.title("Gain vs Peak Variation")
    plt.savefig(output_directory + 'Gain vs Peak Variation.png', dpi=100)
    plt.show()



'''
Identify the xtals with high resolution
'''


def poor_res_list(res_value, df):
    bad_xtal = []
    resList = res_cleanup(df)
    for i in range(len(resList)):
        if resList[i] >= res_value:
            # print(i)
            bad_xtal.append(df['Crystal SN'][i])
    return bad_xtal
