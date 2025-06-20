#!/usr/bin/env python3

import numpy as np
import pandas as pd
import netCDF4 as nc
import matplotlib.pyplot as plt
import xarray as xr
import sys

w = pd.read_csv('models.csv')

comp = w['complexity'].tolist()
mods = w['name'].tolist()
year = w['year'].tolist()
base = w['directory'].tolist()

week = int(sys.argv[1])

## Function to identify the dominant phytoplankton
def integrate_and_identify_dominant_phytoplankton(tdir, tfil, species_order):

	'''
	Depth-integrates phytoplankton to mol/m2, and adds a variable indicating the dominant
	species at each point.

	Parameters:
	-----------
	tdir : directory of model output
	tfil : ptrc file with phytoplankton concentrations

	species_order : list of species names to include and order

	Returns:
	--------
	Dataset with:
		- depth-integrated species (mol/m2, NaN where land)
		- dominant_phyto variable (integer) or NaN where top layer is zero
	'''

	phytoplankton = xr.open_dataset(f'{tdir}/{tfil}')
	tmesh = xr.open_dataset('./mesh_mask_v5.nc')
	snam = tfil.replace("ptrc", "domphy")
	snam = f'{tdir}/{snam}'

	# Convert units from mmol/m3 to mol/m3
	selected = phytoplankton[species_order] / 1000

	# Rename tmesh dimensions to match
	e3t = tmesh['e3t_0'].rename({'t': 'time_counter', 'z': 'deptht'})
	if e3t.sizes.get('time_counter', 1) == 1:
		e3t = e3t.squeeze('time_counter', drop = True)
		e3t = e3t.expand_dims(time_counter = phytoplankton.time_counter)

	# Broadcast to match phytoplankton dimensions
	e3t_broadcasted = xr.broadcast(selected, e3t)[1]

	# Depth-integrated values (mol/m2)
	integrated = (selected * e3t_broadcasted).sum(dim = 'deptht')

	# Add metadata
	for sp in species_order:
		integrated[sp].attrs['long_name'] = f'Depth-integrated {sp} phytoplankton concentration'
		integrated[sp].attrs['units']     = 'mol m-2'
		integrated[sp].attrs['note']      = 'Converted from mmol/m3 to mol/m3 before integration using e3t_0 thickness'

	# Stack for dominant species determination
	stacked  = xr.concat([integrated[sp] for sp in species_order], dim = 'species')
	stacked  = stacked.assign_coords(species = np.arange(1, len(species_order) + 1))  # 1-based
	dominant = stacked.argmax(dim = 'species') + 1

	# Mask where top layer is zero for all species (i.e. land)
	top_layer     = selected.isel(deptht = 0)
	top_stacked   = xr.concat([top_layer[sp] for sp in species_order], dim = 'species')
	top_zero_mask = (top_stacked == 0).all(dim = 'species')

	# Mask dominant species
	dominant = dominant.where(~top_zero_mask)

	# Mask integrated species
	for sp in species_order:
		integrated[sp] = integrated[sp].where(~top_zero_mask)

	# Add dominant_species to dataset
	integrated['dominant_phyto'] = dominant
	integrated['dominant_phyto'].attrs['long_name'] = 'Index of dominant phytoplankton species'
	integrated['dominant_phyto'].attrs['description'] = f'1 = NANO, 2 = DIA, 3 = PIC; NaN = top grid cell is zero'
	integrated['dominant_phyto'].attrs['note'] = (
		'Based on maximum depth-integrated biomass (mol m-2); '
		'NaN where top depth layer contains no biomass for all species'
	)

	try:
		integrated.to_netcdf(snam)
	except:
		print('---')
		print(f'did not save - potentially {snam} already exists')

	return integrated


## Identify dominant species for each model (differs by complexity)
for i in range(0, len(mods)):
	c = comp[i]
	m = mods[i]
	y = year[i]
	b = base[i]

	tdir = f'{b}/{m}'
	tfil = f'ORCA2_7d_{y}0101_{y}1231_ptrc_T.nc'

	if c == 'p4z':
		integrate_and_identify_dominant_phytoplankton(tdir, tfil, ['PHY', 'PHY2'])
	else:
		integrate_and_identify_dominant_phytoplankton(tdir, tfil, ['PHY', 'PHY2', 'PIC'])


## Create plots
fig, axs = plt.subplots(2, 4, figsize = (16, 8), facecolor = 'w', edgecolor = 'k')
axs = axs.ravel()

bmax = 0.5 # limit for biomass

# Plot for P4Z
tvars = ['PHY',  'PHY2', 'dominant_phyto'] # variable names in netcdf
lvars = ['NANO', 'DIA',  'DOMINANT PHYTO'] # variable labels

m = mods[0]
y = year[0]
b = base[0]
tdir = f'{b}/{m}'

integ = xr.open_dataset(f'{tdir}/ORCA2_7d_{y}0101_{y}1231_domphy_T.nc')

for i in range(0,3):
	tvar = tvars[i]
	lvar = lvars[i]

	if i < 2:
		tcmap = 'viridis'
		
		q = axs[i].pcolormesh(integ[tvar][week,:,:], cmap = tcmap, vmin = 0, vmax = bmax)
		cbar = plt.colorbar(q, ax = axs[i], orientation = 'horizontal')
		
		axs[i].set_title(f'{lvar}')
	else:
		tcmap = 'Spectral'
		
		q = axs[i+1].pcolormesh(integ[tvar][week,:,:], cmap = tcmap, vmin = 1, vmax = 3)
		cbar = plt.colorbar(q, ax = axs[i+1], orientation = 'horizontal')
		cbar.set_ticks(np.arange(1,4))
		cbar.set_ticklabels(['NANO', 'DIA', 'PIC'])
		
		axs[i+1].set_title(f'{lvar}')

	axs[i].set_xticks([]); axs[i].set_yticks([])

# Plot for P5Z
tvars = ['PHY',  'PHY2', 'PIC', 'dominant_phyto'] # variable names in netcdf
lvars = ['NANO', 'DIA',  'PIC', 'DOMINANT PHYTO'] # variable labels

m = mods[1]
y = year[1]
b = base[1]
tdir = f'{b}/{m}'

integ = xr.open_dataset(f'{tdir}/ORCA2_7d_{y}0101_{y}1231_domphy_T.nc')

for i in range(4,8):
	tvar = tvars[i-4]
	lvar = lvars[i-4]

	if i < 7:
		tcmap = 'viridis'

		q = axs[i].pcolormesh(integ[tvar][week,:,:], cmap = tcmap, vmin = 0, vmax = bmax)
		cbar = plt.colorbar(q, ax = axs[i], orientation = 'horizontal')

		axs[i].set_title(f'{lvar}')
	else:
		tcmap = 'Spectral'
		
		q = axs[i].pcolormesh(integ[tvar][week,:,:], cmap = tcmap, vmin = 1, vmax = 3)
		cbar = plt.colorbar(q, ax = axs[i], orientation = 'horizontal')
		cbar.set_ticks(np.arange(1,4))
		cbar.set_ticklabels(['NANO', 'DIA', 'PIC'])
		
		axs[i].set_title(f'{lvar}')

	axs[i].set_xticks([]); axs[i].set_yticks([])

plt.suptitle(f'Depth integrated phytoplankton (mol/m2) and dominant species for week {week+1}')
plt.tight_layout()
fig.savefig(f'Dominant-species-phyto-w{week+1}.png')

