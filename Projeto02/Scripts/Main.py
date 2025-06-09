# -*- coding: utf-8 -*-
"""
Created on Wed May 28 14:02:42 2025

@author: Marcos Perrude e Mariana Tiemmy
"""

#%% BIBLIOTECA 
import geopandas as gpd 
from spacialAnalysis import plotMunicipios, tratDataOri , plotMunicipioEspecifico, gradeConsumoCidade
import os

repoPath = os.path.dirname(os.getcwd())
dataPath = repoPath +'\Inputs'
OuPath = repoPath +'\Onputs'
figPath = repoPath + '\Figuras'

#Municipios do Brasil
munBR = gpd.read_file(dataPath + '\\BR_Municipios_2024\\BR_Municipios_2024.shp')
#%% Análise do estado
cidade = 'São Paulo'
sigla = 'SP'

dataSP = tratDataOri(dataPath, sigla)
plotMunicipios(dataSP,sigla, munBR, figPath)

#%% Análsie de uma cidade específica

cidadeSp = plotMunicipioEspecifico(dataSP, cidade, munBR, figPath)
gradeConsumoCidade(cidadeSp, cidade, munBR, figPath)





