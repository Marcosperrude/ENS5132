# -*- coding: utf-8 -*-
"""
Created on Sat May  3 19:48:45 2025

@author: Marcos.Perrude
"""

import pandas as pd
import numpy as np
import os

def airQualityAnalysis(uf,repoPath):

    #def AirQualityAnalysis(uf,repoPath):
    uf='PE'
    dataDir = repoPath+'\\inputs\\'+ uf
    dataList = os.listdir(dataDir)
    allFiles =[]
        # Loop na lista dataList 
    for fileInList in dataList:
        print(fileInList)
        dfConc = pd.read_csv(dataDir + '\\' + fileInList,encoding='latin1')
        allFiles.append(dfConc)
        
    aqData = pd.concat(allFiles)
    aqData = pd.DataFrame(aqData)
    
    #Criando Datatime
    datetimeDf = pd.to_datetime(aqData.Data, format='%Y-%m-%d')  
    aqData['datetime'] = datetimeDf
    aqData = aqData.set_index(aqData['datetime'])
    aqData['year'] = aqData.index.year
    aqData['month'] = aqData.index.month
    aqData['day'] = aqData.index.day
    horas  = aqData.Hora.str.split(':')
    horaDf = []
    for hora in horas:
        horaDf.append(hora[0])
    aqData['hour'] = horaDf
    aqData['datetime'] = pd.to_datetime(
        aqData[['year', 'month','day','hour']],format='%Y%m%d %H')
    aqData = aqData.set_index(aqData['datetime'])
        
    #Defnindo as estações do ano
    aqData['Season'] = np.nan
    aqData['Season'][(aqData.month==12) | (aqData.month==1) | 
                          (aqData.month==2) ] = 'Verão'
    aqData['Season'][(aqData.month==3) | (aqData.month==5) | 
                          (aqData.month==4) ] = 'Outono'
    aqData['Season'][(aqData.month==6) | (aqData.month==7) | 
                          (aqData.month==8) ] = 'Inverno'
    aqData['Season'][(aqData.month==9) | (aqData.month==10) | 
                          (aqData.month==11) ] = 'Primavera'

    stations = np.unique(aqData.Estacao)
    
    # criando pasta para salvar os dado
    os.makedirs(repoPath+'\\outputs\\'+uf,exist_ok=True)

    statGroup = aqData.groupby(['Estacao','Poluente']).describe()
    
    # Salvando em csv
    statGroup.to_csv(repoPath+'/outputs/'+uf+'/basicStat_ALL.csv')
    
    # Coloca o índice da matriz como a coluna datetime
    aqData = aqData.set_index(pd.DatetimeIndex(aqData['datetime']))
    
    # Criando uma tabela de dados com cada poluente em colunas diferentes.
    aqTable = aqData.reset_index(drop=True).pivot_table(
        columns='Poluente',
        index=['Estacao','datetime'],
        values='Valor')

    return aqData, stations, aqTable
