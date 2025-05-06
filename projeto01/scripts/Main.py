# -*- coding: utf-8 -*-
"""
Created on Sat May  3 17:52:10 2025

@author: Marcos.Perrude
"""
from AirQualityAnalysis import airQualityAnalysis
from airQualityFigures import airQualityHist, airQualityTimeSeries, boxplot, lineplot03, TendeciaMennKendall,plotmonth
import os
from univariateStatistics import univariateStatistics


# Reconhecer pasta do repositório
repoPath = os.path.dirname(os.getcwd())
print(repoPath)

# Definindo pasta de dados
dataPath = repoPath +'\inputs'


# Cria a pasta se ela não existir... precisam colocar os dados dentro dela.
os.makedirs(dataPath, exist_ok = True)

# Lista pastas dentro de dataPath
ufs = os.listdir(dataPath)

# Loop para todos os estados
for uf in ufs:
    #
    aqData, stations, aqTable = airQualityAnalysis(uf,repoPath)
    
    os.chdir(repoPath+'\scripts')
    airQualityHist(aqData,stations,uf,repoPath)
    #airQualityTimeSeries(aqData,stations,uf,repoPath)
    univariateStatistics(aqTable,stations,uf,repoPath)
    boxplot(aqData, stations, repoPath, uf)
    
    lineplot03(aqData, stations, repoPath, uf)
    TendeciaMennKendall(aqData, stations, repoPath, uf)
    plotmonth(aqData, stations, repoPath, uf)
