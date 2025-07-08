# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 13:39:13 2025

@author: Marcos.Perrude
"""
# main_edgar.py

import os
import xarray as xr
from shapely.geometry import mapping
from funcoes_edgar import carregar_limites,  analysisEDGAR,carregar_dataset_estimado,plot_mapa_espacial,plot_emissions_subplots, apply_mann_kendall, plot_correct_trend_map
DataDir = r"C:\Users\marcos perrude\Documents\ENS5132\Projeto03"
DataPath = os.path.join(DataDir, 'Inputs')
EDGARPath = os.path.join(DataPath, 'bkl_BUILDINGS_emi_nc')
FigPath = os.path.join(DataDir, 'figuras')



#%% Plote SP

estado = 'SC'
variavel = 'CO'
nome_arquivo = 'emissoes_totais-SC.nc'

br_uf, municipio = carregar_limites(DataPath, estado)
SC = analysisEDGAR(EDGARPath, br_uf, estado)

da =  carregar_dataset_estimado(DataPath, variavel, nome_arquivo, br_uf,estado)


# Plots espaciais e temporais
dataarrays = [da, SC]
titulos = ["Estimado", "EDGAR"]

for data, titulo in zip(dataarrays, titulos):
    plot_mapa_espacial(data, titulo, municipio, estado, FigPath)
    plot_emissions_subplots(data, titulo, estado, FigPath)

# Mann-Kendall


for data, nome_fonte in zip(dataarrays, titulos):
    print(f"Aplicando Mann-Kendall para {nome_fonte}...")
    
    # Aplica o teste
    results = apply_mann_kendall(data)
    # Plota o mapa de tendências
    plot_correct_trend_map(results, estado, FigPath, nome_fonte)
    
    
    
#%% Plote SP    
estado = 'SP'
variavel = 'CO'
nome_arquivo = 'emissoes_totais-SP.nc'

br_uf, municipio = carregar_limites(DataPath, estado)
SP = analysisEDGAR(EDGARPath, br_uf, estado)

da =  carregar_dataset_estimado(DataPath, variavel, nome_arquivo, br_uf,estado)
# SP.isel(time=0).plot()

# Plots espaciais e temporais
dataarrays = [da, SP]
titulos = ["Estimado", "EDGAR"]

for data, titulo in zip(dataarrays, titulos):
    plot_mapa_espacial(data, titulo, municipio, estado, FigPath)
    plot_emissions_subplots(data, titulo, estado, FigPath)

# Mann-Kendall


for data, nome_fonte in zip(dataarrays, titulos):
    print(f"Aplicando Mann-Kendall para {nome_fonte}...")
    
    # Aplica o teste
    results = apply_mann_kendall(data)
    # Plota o mapa de tendências
    plot_correct_trend_map(results, estado, FigPath, nome_fonte)
    
    
