# -*- coding: utf-8 -*-
"""
Created on Sat Jun  7 11:47:49 2025

@author: Marcos.Perrude
"""

import geopandas as gpd
import os
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import contextily as cx
import numpy as np
from shapely.geometry import box

def tratDataOri (dataPath, uf):
    data = [f for f in os.listdir(dataPath) if os.path.isdir(os.path.join(dataPath, f))]
    pathUf = [f for f in data if f.endswith(uf)]
    dirUf = os.path.join(dataPath, pathUf[0])
    dataDirUf = [f for f in os.listdir(dirUf) if f.endswith('.shp')]
    dirDataDirUf = os.path.join(dirUf, dataDirUf[0])
    dataUf = gpd.read_file(dirDataDirUf)
    
    #Tratar o arquivo
    
    dataUf = dataUf.drop(dataUf.columns[13:23], axis=1)
    dataUf = dataUf.drop(dataUf.columns[17:19], axis=1)
    dataUf = dataUf.dropna()
    
    return dataUf #geoSp
 
def plotMunicipios(dataUf, uf, munBR , figPath):

    #Separar os consumos por municipios
    geoUfunido = dataUf.dissolve(by='NM_MUN', aggfunc='sum').reset_index()
    consumoCidUf = geoUfunido.groupby('NM_MUN').agg({
        'Consumo_le': 'sum',
        'Consumo_Ca': 'sum'
    }).reset_index()
    
    #Merge com as geometrias
    geoMunUf = munBR[munBR['SIGLA_UF'] == uf]
    
    consumoCidUf['NM_MUN'] = consumoCidUf['NM_MUN'].astype(str)
    geoMunUf['NM_MUN'] = geoMunUf['NM_MUN'].astype(str)

    geoUfagg = consumoCidUf.merge(
    geoMunUf[['NM_MUN', 'geometry']],
    on='NM_MUN')
    
    
    geoUfagg = gpd.GeoDataFrame(geoUfagg, geometry='geometry', crs=geoMunUf.crs)
    geoUfagg = geoUfagg.set_index('NM_MUN')
    geoUfagg = geoUfagg[(geoUfagg['Consumo_le'] > 0) & (geoUfagg['Consumo_Ca'] > 0)]
    
    # Plot e salvamento da figura
    fig, ax = plt.subplots(figsize=(10, 8))
    geoUfagg.plot(ax=ax, edgecolor  ='black',linewidth = 0.5)
    plt.title(f'Municípios da UF {uf}')
    
    plt.savefig(os.path.join(figPath, f'municipios {uf}.png'), dpi=300)
    plt.close()
    
    for col, titulo in zip(['Consumo_le', 'Consumo_Ca'], ['Lenha', 'Carvão']):
        fig, ax = plt.subplots(figsize=(10, 5))
        geoUfagg.plot(
            column=col,
            cmap='Oranges',
            legend=True,
            norm=colors.LogNorm(vmin=geoUfagg[col].min(),vmax=geoUfagg[col].max()),
            ax=ax,
            edgecolor='black'
        )
        plt.title(f'Consumo de {titulo} - {uf}')
        plt.savefig(os.path.join(figPath, f'Consumo de {titulo} por cidades.png'))
        plt.close(fig)
        # cx.add_basemap(ax, source=cx.providers.Esri.WorldPhysical, crs=geoMunUf.crs)

        
        topConsumos = geoUfagg[col].sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(10, 10))
        topConsumos.plot(kind='bar', edgecolor='black', ax=ax)
        plt.title(f'Top 10 Municípios - Consumo de {titulo} - {uf}')
        plt.xlabel('Município')
        plt.ylabel(f'Consumo de {titulo} (ton)')
        plt.xticks(rotation=45)
        plt.savefig(os.path.join(figPath, f'Histograma Top10 {titulo} {uf}.png'))
        plt.close(fig)
        
        
    return geoUfagg , print('Figuras salvas com sucesso')

def plotMunicipioEspecifico(dataUf,cidade,munBR, figPath ):

    # munCidade = munBR[munBR['NM_MUN'] == cidade]
    cidadeUf = dataUf[dataUf['NM_MUN'] == cidade]
    
    for col, titulo in zip(['Consumo_le', 'Consumo_Ca'], ['Lenha', 'Carvão']):
       
        fig, ax = plt.subplots(figsize=(10, 10))
        cidadeUf.plot(column=col, cmap='Reds', linewidth=0.5, ax=ax, edgecolor='0.8', legend=True)
        plt.title(f'Consumo de {titulo} na cidade de {cidade}')
        # cx.add_basemap(ax, source=cx.providers.Esri.WorldPhysical, crs=munCidade.crs)
        plt.show()
        plt.savefig(os.path.join(figPath, f'Consumo de {titulo} na cidade de {cidade}.png'))
        plt.close(fig)
        
        
        fig, ax = plt.subplots(figsize=(10, 10))
        cidadeUf.hist(ax=ax , column= col ,bins=20,  edgecolor='black', log=True)
        plt.title(f'Histograma de consumo de {titulo} na cidade de {cidade}')
        plt.xlabel(f'Consumo de {titulo} (ton)')
        plt.ylabel('Frequência')
        plt.savefig(os.path.join(figPath, f'Consumo de {titulo} por cidades.png'))
        plt.close(fig)
        
        # topConsumos = cidadeUf[col].sort_values(ascending=False).head(10)
        # fig, ax = plt.subplots(figsize=(10, 10))
        # topConsumos.plot(kind='bar', edgecolor='black', ax=ax)
        # plt.title(f'Top 10 Zonas - Consumo de {titulo} na cidade de {cidade}')
        # plt.ylabel(f'Consumo de {titulo} (ton)')
        # plt.xticks(rotation=45)
        # plt.savefig(os.path.join(figPath, f'Histograma Top10 na cidade de {cidade}.png'))
        # plt.close(fig)
        
    return cidadeUf
        
def gradeConsumoCidade (dataCidade, cidade, munBR,figPath) :
       
    minx, miny, maxx, maxy = dataCidade.total_bounds
    munCidade = munBR[munBR['NM_MUN'] == 'São Paulo']
    x_coords = np.arange(minx, maxx, 0.05)
    y_coords = np.arange(miny, maxy, 0.05)
    grid_cells = [box(x, y, x + 0.05, y + 0.05) for x in x_coords for y in y_coords]
    gridGerado = gpd.GeoDataFrame(geometry=grid_cells, crs='EPSG:4674')
    
    
    intersec = gpd.sjoin(dataCidade,gridGerado, how='inner', predicate='intersects')
    intersec = intersec.merge(
            gridGerado[['geometry']],
            left_on='index_right', right_index=True, suffixes=('', '_right')
        )
    
    intersec_area = intersec.geometry.intersection(intersec['geometry_right']).area
    peso = intersec_area / intersec.geometry.area
    
    for col, titulo in zip(['Consumo_le', 'Consumo_Ca'], ['Lenha', 'Carvão']):
        ponderado = intersec[col] * peso
        soma_ponderada = ponderado.groupby(intersec["index_right"]).sum()
        gridGerado.loc[soma_ponderada.index, col] = soma_ponderada.values.astype(float)
    
        fig, ax = plt.subplots(figsize=(10, 8))
        munCidade.boundary.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1)
        # Plot do grid com consumo
        
        gridGerado.plot(column=col, cmap='Oranges',ax=ax, legend=True, edgecolor='none')
        plt.title(f'Grid de consumo de {titulo} na cidade de {cidade}')
        plt.savefig(os.path.join(figPath, f'Grid de consumo de {titulo} na cidade de {cidade}.png'))
        plt.close(fig)
    
    return print('Figuras salvas com sucesso')
        
        