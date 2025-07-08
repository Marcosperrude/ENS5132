# -*- coding: utf-8 -*-
"""
Created on Tue Jul  8 10:16:18 2025

@author: Marcos.Perrude
"""

# funcoes_edgar.py

import os
import xarray as xr
import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from shapely.geometry import mapping
from tqdm import tqdm
from scipy.stats import kendalltau
import matplotlib.colors as colors
import cartopy.feature as cfeature
from shapely.geometry import mapping

def carregar_limites(DataPath, estado):
    br_uf = gpd.read_file(os.path.join(DataPath, 'BR_UF_2023', 'BR_UF_2023.shp'))
    municipios_br = gpd.read_file(os.path.join(DataPath, 'BR_Municipios_2024', 'BR_Municipios_2024.shp'))

    # Selecionar apenas municípios do estado desejado
    municipios_estado = municipios_br[municipios_br['SIGLA_UF'] == estado]

    return br_uf, municipios_estado


def carregar_dataset_estimado(DataPath, variavel,nome_arquivo,br_uf,estado):

    caminho_arquivo = os.path.join(DataPath, nome_arquivo)
    ds = xr.open_dataset(caminho_arquivo)

    da = xr.DataArray(
        data=ds[variavel].values,
        dims=["time", "lat", "lon"],
        coords={"time": ds['time'], "lat": ds['lat'], "lon": ds['lon']},
        name="emissions"
    )

    da = da.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=False)
    da = da.rio.write_crs("EPSG:4326", inplace=False)
    geodf_estado = br_uf.query("SIGLA_UF == @estado")
    da = da.rio.clip(geodf_estado.geometry.apply(mapping), geodf_estado.crs, all_touched=True)
   
    return da

def analysisEDGAR(EDGARPath, br_uf, estado):
    dataList = sorted([f for f in os.listdir(EDGARPath) if f.endswith('.nc')])
    datasets = [xr.open_dataset(os.path.join(EDGARPath, fname),
                                chunks={'time': 1}) for fname in dataList]
    xds = xr.concat(datasets, dim='time')
    
    da0 = xr.DataArray(
        data=xds['emissions'],
        dims=["time", "lat", "lon"],
        coords={"time": xds['time'], "lat": xds['lat'], "lon": xds['lon']},
        name="emissions"
    ).rio.write_crs("EPSG:4326", inplace=False)
    
    if estado == 'BR':
        clipped = da0.rio.clip(br_uf.geometry.apply(mapping), br_uf.crs, all_touched=True)
    else:
        geodf_estado = br_uf.query("SIGLA_UF == @estado")
        clipped = da0.rio.clip(geodf_estado.geometry.apply(mapping),
                               geodf_estado.crs, all_touched=True)
    
    clipped.load()
    clipped.to_netcdf(f'Clip_{estado}.nc')
    return clipped

def plot_mapa_espacial(data, titulo, municipio, estado, FigPath):
    fig, ax = plt.subplots(figsize=(10, 7))
    pcm = ax.pcolor(data['lon'], data['lat'],
                    np.mean(data.values, axis=0), 
                    shading='auto', cmap='plasma')
    municipio.boundary.plot(ax=ax, edgecolor='black', linewidth=0.5)
    fig.colorbar(pcm, ax=ax, orientation='vertical', label='Emissões Médias (Ton/mês)')
    ax.set_title(titulo)
    plt.tight_layout()
    os.makedirs(os.path.join(FigPath, estado), exist_ok=True)
    fig.savefig(os.path.join(FigPath, estado, f"Mapa - {titulo} de CO em {estado}.png"), dpi=1500)

def plot_emissions_subplots(data, nome, estado, FigPath):
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), constrained_layout=True)
    time = data['time'].values
    emissoes_medias = data.mean(dim=["lat", "lon"]).values
    anos_frac = np.array([t.year + t.month/12 for t in pd.to_datetime(time)])

    coef = np.polyfit(anos_frac, emissoes_medias, deg=1)
    tendencia = np.polyval(coef, anos_frac)

    axes[0].plot(anos_frac, emissoes_medias, label=nome)
    axes[0].plot(anos_frac, tendencia, linestyle='--', color='red', label='Tendência linear')
    axes[0].set_title(f'Série Histórica - {nome} ({estado})')
    axes[0].legend()
    axes[0].grid(True)

    dataMonth = data.groupby('time.month').mean(dim=['time', 'lat', 'lon'])
    axes[1].plot(dataMonth['month'], dataMonth.values, marker='o', label=nome)
    axes[1].set_title('Média mensal')
    axes[1].legend()
    axes[1].grid(True)

    os.makedirs(os.path.join(FigPath, estado), exist_ok=True)
    fig.savefig(os.path.join(FigPath, estado, f"Analises - {nome} de CO em {estado}.png"), dpi=1000)

def mann_kendall_test(x):
    x = x[~np.isnan(x)]
    if len(x) < 2:
        return np.nan, np.nan, np.nan
    tau, p_value = kendalltau(range(len(x)), x)
    slopes = [(x[j] - x[i]) / (j - i) for i in range(len(x)) for j in range(i+1, len(x))]
    sens_slope = np.median(slopes) if slopes else np.nan
    return tau, p_value, sens_slope

def apply_mann_kendall(data_array):
    shape = data_array.shape[1:]
    tau_map, p_map, trend_map = np.full(shape, np.nan), np.full(shape, np.nan), np.full(shape, np.nan)
    for i in tqdm(range(shape[0])):
        for j in range(shape[1]):
            ts = data_array[:, i, j].values
            tau, p, trend = mann_kendall_test(ts)
            tau_map[i, j], p_map[i, j], trend_map[i, j] = tau, p, trend
    return xr.Dataset({
        'tau': (('lat', 'lon'), tau_map),
        'p_value': (('lat', 'lon'), p_map),
        'trend': (('lat', 'lon'), trend_map)
    }, coords={'lat': data_array.lat, 'lon': data_array.lon})

def plot_correct_trend_map(results, estado, FigPath,nome_fonte):
    significance_level=0.01
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linestyle=':')
    sig = results.p_value < significance_level
    rgb = np.zeros((*results.tau.shape, 3))
    rgb[sig & (results.tau > 0)] = [1, 0.3, 0.3]
    rgb[sig & (results.tau < 0)] = [0.3, 0.3, 1]
    rgb[~sig] = [0.7, 0.7, 0.7]
    ax.imshow(rgb, extent=[results.lon.min(), results.lon.max(),
                           results.lat.min(), results.lat.max()],
              transform=ccrs.PlateCarree(), origin='lower')
    sm = plt.cm.ScalarMappable(cmap='coolwarm', norm=colors.Normalize(vmin=-1, vmax=1))
    sm.set_array([])
    plt.colorbar(sm, ax=ax, label='Tau de Kendall')
    
    plt.title(f'Tendência de Emissões de CO - {nome_fonte} ({estado})\n(p < {significance_level})')
    estadoPath = os.path.join(FigPath, estado)
    os.makedirs(estadoPath, exist_ok=True)
    fig.savefig(os.path.join(estadoPath, f"Mann-Kendall_{nome_fonte}_{estado}.png"), dpi=1000)