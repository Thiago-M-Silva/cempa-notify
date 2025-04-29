import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
import numpy as np
import subprocess

comando = [
    "cdo", "-f", "nc", "import_binary", "./files/Go5km-A-2025-04-21-000000-g1.ctl", "./files/saida.nc"
]

try:
    subprocess.run(comando, check=True)
    print("Conversão concluída com sucesso!")
except subprocess.CalledProcessError as e:
    print(f"Erro ao executar o comando: {e}")

ds = xr.open_dataset("./files/saida.nc") 
data = ds['t2mj'].isel(time=0)
print(ds.data_vars)

colors = [
    '#0000b2', 
    '#005ce6', 
    '#008c8c', 
    '#008000', 
    '#66b032', 
    '#ffff00', 
    '#ffaa00', 
    '#ff5500', 
    '#cc0000', 
    '#7f0000'  
]
cmap = mcolors.LinearSegmentedColormap.from_list("cempa_like", colors, N=256)

fig = plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())

contour = data.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap=cmap,
    levels=np.arange(14, 39, 1),
    cbar_kwargs={'label': '[°C]'}
)

ax.add_feature(cfeature.BORDERS, linewidth=1)
ax.add_feature(cfeature.COASTLINE, linewidth=1)
ax.add_feature(cfeature.STATES, linewidth=1)
ax.add_feature(cfeature.LAND,linewidth=1)
ax.set_extent([-54, -43, -21, -8.5]) 

plt.title("Temperatura 2m para 00z 2025/04/21", fontsize=14)
plt.suptitle("CEMPA/UFG - Previsão BRAMS iniciada em: 00z 2025/04/21", fontsize=12, color='steelblue')
plt.tight_layout()
plt.show()
