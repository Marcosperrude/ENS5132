# -*- coding: utf-8 -*-
"""
Created on Mon May  5 15:07:00 2025

@author: Marcos.Perrude
"""

import numpy as np
import matplotlib.pyplot as plt
import pymannkendall as mk
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd
import os
from airQualityFigures import normalityCheck, trendFigures,timeSeriesForecast
from datetime import datetime
# Análise de sazonalidade
import warnings
warnings.filterwarnings('ignore')

def markham_index(monthly_values):
    monthly_values = np.array(monthly_values)
    mean_value = np.nanmean(monthly_values)
    numerator = np.nansum(np.abs(monthly_values - mean_value))
    denominator = 2 * np.nansum(monthly_values)
    msi = (numerator / denominator) * 100
    return msi


def timeSeriesDecompose(aqTableAlvo, pol, uf, repoPath, stationAlvo):
    dataDecompose = aqTableAlvo[[pol, 'datetime']]
    dataDecomposeMonthly = dataDecompose.groupby(pd.PeriodIndex(dataDecompose['datetime'], freq="M"))[pol].mean()
    dataDecomposeMonthly = pd.Series(np.array(dataDecomposeMonthly), index=pd.PeriodIndex(dataDecomposeMonthly.index))
    full_index = pd.period_range(start=dataDecomposeMonthly.index.min(), end=dataDecomposeMonthly.index.max(), freq='M')
    complete_data = dataDecomposeMonthly.reindex(full_index)
    complete_data = complete_data.interpolate().dropna()
    complete_data.index = complete_data.index.to_timestamp()

    res = seasonal_decompose(complete_data, period=12)

    os.makedirs(os.path.join(repoPath, 'figuras', uf), exist_ok=True)
    fig, axes = plt.subplots(ncols=1, nrows=4, sharex=True)
    res.observed.plot(ax=axes[0], legend=False, color='blue')
    axes[0].set_ylabel('Observed')
    res.trend.plot(ax=axes[1], legend=False, color='red')
    axes[1].set_ylabel('Trend')
    res.seasonal.plot(ax=axes[2], legend=False, color='yellow')
    axes[2].set_ylabel('Seasonal')
    res.resid.plot(ax=axes[3], legend=False, color='gray')
    axes[3].set_ylabel('Residual')

    fig_path = os.path.join(repoPath, 'figuras', uf, f'decompose_{pol}_{stationAlvo}.png')
    fig.savefig(fig_path)

    return res, complete_data


def univariateStatistics(aqTable, stations, uf, repoPath):
    os.makedirs(os.path.join(repoPath, 'outputs', uf), exist_ok=True)
    
    trend, h, p, z, Tau, s, var_s, slope, intercept = [], [], [], [], [], [], [], [], []
    MarkhamIndex = []
    st, pols = [], []

    for stationAlvo in stations:
        print(stationAlvo + '==========')
        aqTableNew = aqTable.reset_index()
        aqTableAlvo = aqTableNew[aqTableNew.Estacao == stationAlvo].dropna(axis=1, how='all')
        pollutants = aqTableAlvo.columns[2:]

        for pol in pollutants:
            print(pol + '------------')

            dataDecomposeMonthly = aqTableAlvo.groupby(
                pd.PeriodIndex(aqTableAlvo['datetime'], freq="M"))[pol].agg(np.nanmean)

            full_index = pd.period_range(
                start=datetime(int(pd.DatetimeIndex(dataDecomposeMonthly.index.to_timestamp()).year.min()), 1, 1),
                end=datetime(int(pd.DatetimeIndex(dataDecomposeMonthly.index.to_timestamp()).year.max()), 12, 31),
                freq='M')

            complete_data = dataDecomposeMonthly.reindex(full_index)

            try:
                res, complete_data = timeSeriesDecompose(aqTableAlvo, pol, uf, repoPath, stationAlvo)
                timeSeriesForecast(complete_data, repoPath, uf, pol, stationAlvo)
            except:
                print('Não foi possível decompor a série de dados')

            try:
                result = mk.original_test(aqTableAlvo.groupby(pd.PeriodIndex(
                    aqTableAlvo['datetime'], freq="A"))[pol].median())

                trend.append(result.trend)
                h.append(result.h)
                p.append(result.p)
                z.append(result.z)
                Tau.append(result.Tau)
                s.append(result.s)
                var_s.append(result.var_s)
                slope.append(result.slope)
                intercept.append(result.intercept)
                st.append(stationAlvo)
                pols.append(pol)
                msi = markham_index(complete_data)
                MarkhamIndex.append(msi)
                print(f"Markham Seasonality Index: {msi:.2f}")

                trendFigures(aqTableAlvo.groupby(pd.PeriodIndex(
                    aqTableAlvo['datetime'], freq="A"))[pol].median(), result)

            except:
                trend.append(np.nan)
                h.append(np.nan)
                p.append(np.nan)
                z.append(np.nan)
                Tau.append(np.nan)
                s.append(np.nan)
                var_s.append(np.nan)
                slope.append(np.nan)
                intercept.append(np.nan)
                st.append(stationAlvo)
                pols.append(pol)
                MarkhamIndex.append(np.nan)

    univariateStats = pd.DataFrame({
        'station': st,
        'pollutant': pols,
        'trend': trend,
        'h': h,
        'p': p,
        'z': z,
        'Tau': Tau,
        's': s,
        'var_s': var_s,
        'slope': slope,
        'intercept': intercept,
        'MarkhamIndex': MarkhamIndex
    })

    output_path = os.path.join(repoPath, 'outputs', uf, 'univariateStats.csv')
    univariateStats.to_csv(output_path, index=False)

    return univariateStats