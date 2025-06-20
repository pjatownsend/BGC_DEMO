#!/usr/bin/env python3

import numpy as np
import pandas as pd
import netCDF4 as nc
import matplotlib.pyplot as plt
import xarray as xr
import sys
from netCDF4 import Dataset

w = pd.read_csv('models.csv')

mods = w['name'].tolist()
year = w['year'].tolist()
base = w['directory'].tolist()


## Create plots
ratio = 2
fig = plt.figure()
fig.set_figheight(4*ratio) # rows
fig.set_figwidth(9*ratio)  # columns

ax1 = plt.subplot2grid(shape=(4,9), loc=(0,0), rowspan=2, colspan=3)
ax2 = plt.subplot2grid(shape=(4,9), loc=(0,3), rowspan=2, colspan=3)
ax3 = plt.subplot2grid(shape=(4,9), loc=(0,6), rowspan=2, colspan=3)

ax4 = plt.subplot2grid(shape=(4,9), loc=(2,0), rowspan=2, colspan=3)
ax5 = plt.subplot2grid(shape=(4,9), loc=(2,3), rowspan=2, colspan=3)

axs = [ax1, ax2, ax3, ax4, ax5]

cols = ['b', 'r']

# Plot for P4Z
var_list = ['PHY', 'PHY2', 'ZOO', 'ZOO2']

m = mods[0]
y = year[0]
b = base[0]
tdir = f'{b}/{m}'

wk = np.arange(52)

in_file_phyto = Dataset(f'{tdir}/ORCA2_7d_{y}0101_{y}1231_domphy_T.nc', 'r')
for i in range(0, 2):
	varName = var_list[i]

	var_in   = in_file_phyto.variables[varName][:]
	var_glob = np.apply_over_axes(np.nanmean, var_in, [1,2]) # average over the global ocean

	axs[i].plot(wk, var_glob[:,0,0], cols[0]);

in_file_zoo = Dataset(f'{tdir}/ORCA2_7d_{y}0101_{y}1231_domzoo_T.nc', 'r')
for i in range(2, 4):
	varName = var_list[i]

	var_in   = in_file_zoo.variables[varName][:]
	var_glob = np.apply_over_axes(np.nanmean, var_in, [1,2]) # average over the global ocean

	axs[i+1].plot(wk, var_glob[:,0,0], cols[0]);


# Plot for P5Z
var_list  = ['PHY',  'PHY2', 'PIC', 'ZOO',   'ZOO2']
var_label = ['NANO', 'DIA',  'PIC', 'MICRO', 'MES']

m = mods[1]
y = year[1]
b = base[1]
tdir = f'{b}/{m}'

in_file_phyto = Dataset(f'{tdir}/ORCA2_7d_{y}0101_{y}1231_domphy_T.nc', 'r')
for i in range(0, 3):
	varName = var_list[i]
	varLab  = var_label[i]

	var_in   = in_file_phyto.variables[varName][:]
	var_glob = np.apply_over_axes(np.nanmean, var_in, [1,2]) # average over the global ocean

	axs[i].plot(wk, var_glob[:,0,0], cols[1]); axs[i].set_title(f'{varLab} depth integrated average [mol/m2]');

in_file_zoo = Dataset(f'{tdir}/ORCA2_7d_{y}0101_{y}1231_domzoo_T.nc', 'r')
for i in range(3, 5):
	varName = var_list[i]
	varLab  = var_label[i]

	var_in   = in_file_zoo.variables[varName][:]
	var_glob = np.apply_over_axes(np.nanmean, var_in, [1,2]) # average over the global ocean

	axs[i].plot(wk, var_glob[:,0,0], cols[1]); axs[i].set_title(f'{varLab} depth integrated average [mol/m2]');

for ax in axs:
	ax.grid(linestyle='--', linewidth=0.25)

plt.tight_layout()
fig.savefig(f'seasonal-summary.png')
print(f'Created seasonal summary')

