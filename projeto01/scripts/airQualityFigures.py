# -*- coding: utf-8 -*-
"""
Created on Mon May  5 23:39:13 2025

@author: Marcos.Perrude
"""

import matplotlib.pyplot as plt
import os
import numpy as np
from scipy import stats
import statsmodels.api as sm
import pandas as pd
import seaborn as sns
import pymannkendall as mk

def airQualityHist(aqData,stations,uf,repoPath):
    os.makedirs(os.path.join(repoPath, "figuras", uf), exist_ok=True)
    
    for st in stations:
        fig, ax = plt.subplots()
        aqData[aqData.Estacao==st].hist('Valor',by='Poluente', ax=ax)
        fig.savefig(os.path.join(repoPath, "figuras", uf, f"hist_{st}.png"))
        
def airQualityTimeSeries(aqData, stations, uf, repoPath):
    os.makedirs(os.path.join(repoPath, "figuras", uf), exist_ok=True)
    
    for st in stations:
        pollutants = np.unique(aqData[aqData.Estacao == st].Poluente)
        fig, ax = plt.subplots(pollutants.size)

        for ii, pol in enumerate(pollutants):
            data = aqData[(aqData.Estacao == st) & (aqData.Poluente == pol)].Valor
            if pollutants.size > 1:
                ax[ii].plot(data)
            else:
                ax.plot(data)
        
        save_path = os.path.join(repoPath, "figuras", uf, f"plot_{st}.png")
        fig.savefig(save_path)

def normalityCheck(aqTableAlvo, repoPath, uf, stationAlvo, pol):
    os.makedirs(os.path.join(repoPath, "figuras", uf), exist_ok=True)

    fig, ax = plt.subplots(3)
    ax[0].hist(np.log(aqTableAlvo[pol].dropna()), facecolor='red')
    ax[0].set_title('Log')
    ax[0].set_ylabel('Frequência')
    
    ax[1].hist(stats.boxcox(aqTableAlvo[pol].dropna())[0], facecolor='green')
    ax[1].set_title('Boxcox')
    ax[1].set_ylabel('Frequência')
    
    ax[2].hist(aqTableAlvo[pol].dropna())
    ax[2].set_title('Dado original')
    ax[2].set_ylabel('Frequência')

    fig.tight_layout()
    save_path = os.path.join(repoPath, "figuras", uf, f"histogramDataNormalization_{pol}_{stationAlvo}.png")
    fig.savefig(save_path)
    return fig

def trendFigures(data, result):
    fig, ax = plt.subplots(2)
    sm.graphics.tsa.plot_acf(data, lags=5, ax=ax[0])
    ax[0].set_title('Autocorrelação ACF')

    trend_line = np.arange(len(data)) * result.slope + result.intercept
    data.plot(ax=ax[1])
    ax[1].plot(data.index, trend_line)
    ax[1].legend(['data', 'trend line'])
    ax[1].set_title('Tendência')

    return fig

def timeSeriesForecast(complete_data, repoPath, uf, pol, stationAlvo):
    from pmdarima.arima import auto_arima

    os.makedirs(os.path.join(repoPath, "figuras", uf), exist_ok=True)

    stepwise_model = auto_arima(
        complete_data, start_p=1, start_q=1, max_p=3, max_q=3, m=12,
        seasonal=True, error_action='ignore'
    )
    print(stepwise_model.aic())

    train = pd.DataFrame({'train': complete_data.iloc[0:int(complete_data.shape[0]*0.7)]})
    test = pd.DataFrame({'test': complete_data.iloc[int(complete_data.shape[0]*0.7):]})

    stepwise_model.fit(train)
    future_forecast = pd.DataFrame({'future_forecast': stepwise_model.predict(n_periods=test.shape[0])})

    fig, axes = plt.subplots()
    pd.concat([complete_data, future_forecast], axis=1).plot(ax=axes)

    save_path = os.path.join(repoPath, "figuras", uf, f"timeSeriesForecast_{pol}_{stationAlvo}.png")
    fig.savefig(save_path)
    return fig


def boxplot(aqData, stations, repoPath, uf):
    os.makedirs(os.path.join(repoPath, "figuras", uf), exist_ok=True)
    pollutants = aqData['Poluente'].unique()
    
    for pol in pollutants:
        for st in stations:
            try:
                # Filtra os dados para o poluente e estação atual
                a = aqData[(aqData.Poluente == pol) & (aqData.Estacao == st)].copy()
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.boxplot(data=a, x='month', y='Valor', ax=ax)
                ax.set_title(f"Boxplot mensal - Poluente: {pol} | Estação: {st}")
                ax.set_xlabel("Mês")
                ax.set_ylabel(f"Valor ({a['Unidade'].iloc[0]})")
                fig.tight_layout()
                
                # Salva a figura
                save_path = os.path.join(repoPath, "figuras", uf, f"plot_{st}_{pol}.png")
                fig.savefig(save_path)
                
            except ValueError as e:
                print(f"Erro ao processar Poluente: {pol} | Estação: {st} - {e}")

def lineplot03(aqData,stations,repoPath,uf):
    os.makedirs(os.path.join(repoPath, "figuras", uf), exist_ok=True)
    aqData03 = aqData.query('Poluente == "O3"') 
    fig, ax = plt.subplots(6, sharex=True, figsize=(20, 10))
    
    for i, est in enumerate(stations):
        aqData03_est = aqData03[aqData03['Estacao'] == est]
        media_diaria = aqData03_est['Valor'].resample('D').mean()
        min_diaria = aqData03_est['Valor'].resample('D').min()
        max_diaria = aqData03_est['Valor'].resample('D').max()
        
        ax[i].plot(media_diaria.index, media_diaria, color= 'blue')
        ax[i].fill_between(media_diaria.index, min_diaria, max_diaria, color='blue', alpha=0.2)
        ax[i].set_title(f"{est}")
        ax[i].legend()
        fig.tight_layout()
        save_path = os.path.join(repoPath, "figuras", uf, "Emissoes de 03")
        fig.savefig(save_path)
        
        
        
    
def TendeciaMennKendall (aqData,stations,repoPath,uf):  
    os.makedirs(os.path.join(repoPath, "figuras", uf), exist_ok=True)
    aqData03 = aqData.query('Poluente == "O3"')
    
    fig, ax = plt.subplots(6, sharex=True, figsize=(20, 10))
    for i, est in enumerate(stations):
        aqData03_est = aqData03[aqData03['Estacao'] == est]
        media_diaria = aqData03_est['Valor'].resample('D').mean().dropna()
        res = mk.original_test(media_diaria)
        trend_line = np.arange(len(media_diaria)) * res.slope + res.intercept
        ax[i].plot(media_diaria)
        ax[i].plot(media_diaria.index, trend_line)
        ax[i].legend([ 'Tendencia Mann-Kendall'])
        ax[i].set_title(f"{est}")
        fig.tight_layout()
        save_path = os.path.join(repoPath, "figuras", uf, "tendencia")
        fig.savefig(save_path)
        print('Análise \n', res)
    
def plotmonth(aqData,stations,repoPath,uf):
    aqData03 = aqData.query('Poluente == "O3"')
    fig, ax = plt.subplots(6, sharex=True, figsize=(20, 15))
    for i, est in enumerate(stations):
        aqData03_est = aqData03[aqData03['Estacao'] == est]
        m = aqData03_est.groupby('month')['Valor'].mean()
        ax[i].plot(m)
        ax[i].set_title(f"{est}")
        fig.tight_layout()
        save_path = os.path.join(repoPath, "figuras", uf, "analise mes")
        fig.savefig(save_path)
    
    
    
    