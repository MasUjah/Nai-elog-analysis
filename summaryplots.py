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
from Functions import InputFunction, make_res_hist, make_var_hist, make_volt_hist, res_var_2d, res_volt_2d, \
    var_volt_2d, poor_res_list

output_directory, input_directory, print_out_filepath = InputFunction()


rows_to_skip = [1,55,78] #only if there is incomplete entry
df = pd.read_csv(input_directory, encoding='latin1', skiprows=rows_to_skip)
#                 usecols=(4, 5, 6, 7, 8, 9, 10, 18))
# csv file downloaded from ELOG using 'Find'

make_res_hist(output_directory, df)
make_var_hist(output_directory, df)
make_volt_hist(df, output_directory)

res_var_2d(output_directory, df)
res_volt_2d(output_directory, df)
var_volt_2d(output_directory, df)

print_out_file = open(print_out_filepath, "a")

print(poor_res_list(30, df))

print_out_file.write('Crystals with poor resolution are' + '\n ->'.join(poor_res_list(30, df)))
print_out_file.close()
