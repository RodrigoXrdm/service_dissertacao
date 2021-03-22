import os
import uuid

from flask import Blueprint, current_app, jsonify, request, session

import pandas as pd 
from pandas.api.types import is_numeric_dtype
from scipy.stats import zscore
import numpy as np

bp_cleaning = Blueprint('bp_cleaning', __name__)


@bp_cleaning.route('/missing_values', methods=['GET'])
def missing_values():
    path = session['info_dataset']['path']

    print(path)
    data = pd.read_csv(path)

    selected_features = []

    while(selected_features == []):
        try:
            selected_features = session['selected_features']
        except:
            pass
    
    time_feature = list(data[session['time_feature']])
    data = data[selected_features]

    
    aux_sum_na = sum_na(data,time_feature)
    aux_solutions_mv = solutions_missing_values(data,time_feature)

    r = {'bar_graph' : aux_sum_na, 'line_graph' : aux_solutions_mv}

    return jsonify(r)

def sum_na(data, time_feature):
     
    r = {
        'data' : [{
            'x': [],
            'y': [],
            'type': 'bar'
        }],

        'layout' : {
            'title' : 'Quantidade de instâncias nulas',
            'autosize': True,
            'height': 365,
            'margin': {
                'l': 50,
                'r': 50,
                'b': 50,
                't': 50,
                'pad': 4
            }

        }
    }

    for cols in data.columns.values:
        r['data'][0]['x'].append(str(cols))
        r['data'][0]['y'].append(int(data[cols].isna().sum()))
        
    return r

def solutions_missing_values(df, time_feature):
   

    df_dropna = df.dropna()
    df_fill_mean = df.fillna(df.mean())
    df_fill_median = df.fillna(df.median())
    

    
    
    r = {'methods': { 
            'fill_mean' : {'data' : [],'layout': {}}, 
            'fill_median' : {'data' : [],'layout': {}}
        }, 
        'null_values': {}}
    
    for cols in df.columns.values:
        r['null_values'][cols] = list(df[cols].isna())
    
      
    for cols in df_fill_mean.columns.values:
        null_time_features = [time_feature[x] for x in range(len(time_feature)) if list(df[cols].isna() )[x] == True]
        
        r['methods']['fill_mean']['data'].append({
            'x' : time_feature,
            'y' : list(df_dropna[cols].values),
            'name' : cols,
            'type' : 'scatter',
                  
        })
        r['methods']['fill_mean']['data'].append({
            'x' : null_time_features,
            'y' : list(df_fill_mean[cols][df[cols].isna()].values),
            'name' : f"NaN Values {cols}",
            'type' : 'marker',
            'marker' : {
                'color' : '#8FCED8' 
            }
        })

    null_time_features = [time_feature[x] for x in range(len(time_feature)) if list(df[cols].isna() )[x] == True]

    # print([list(map(int,list(df_dropna[cols].isna())))])
    r['methods']['fill_mean']['layout'] = {
        'title' : 'Preenchendo os valores nulos com a média',
        'autosize': False,
        'height': 300,
        'margin': {
            'l': 50,
            'r': 50,
            'b': 50,
            't': 50,
            'pad': 4
        }
    }
 
    for cols in df_fill_median.columns.values:
        r['methods']['fill_median']['data'].append({
            'x' : time_feature,
            'y' : list(df_fill_median[cols].values),
            'name' : cols,
            'type' : 'scatter',
            # 'mode' : 'lines+markers'l
        })
        r['methods']['fill_median']['data'].append({
            'x' : null_time_features,
            'y' : list(df_fill_median[cols][df[cols].isna()].values),
            'name' : f"NaN Values {cols}",
            'type' : 'marker',
            'marker' : {
                'color' : '#8FCED8' 
            }
        })

    r['methods']['fill_median']['layout'] = {
        'title' : 'Preenchendo os valores nulos com a mediana',
        'autosize': False,
        'height': 300,
        'margin': {
            'l': 50,
            'r': 50,
            'b': 50,
            't': 50,
            'pad': 4
        }
    }
    
    return r

@bp_cleaning.route('/duplicated', methods=['GET'])
def duplicateds():
    r = {'headers' : [], 'duplicates': []}

    selected_features = session['selected_features']
    selected_features.append(session['time_feature'])
    #headers
    for i in selected_features:
        aux = {'text' : i, 'value': i}
        r['headers'].append(aux)
    
    path = session['info_dataset']['path']
    data = pd.read_csv(path)

    data_duplicated = data.duplicated(keep=False)

    df = data[data_duplicated]

    tam = len(df)

    if(tam > 1):
        for i in range(0,tam,2):
            if(len(r['duplicates']) < 3):
                aux = []

                aux_d1 = {}
                for cols in df.columns.values:
                    aux_d1[cols] = df[cols][i]
                aux.append(aux_d1)

                aux_d2 = {} 
                for cols in df.columns.values:
                    aux_d2[cols] = df[cols][i+1]
                aux.append(aux_d2)

                r['duplicates'].append(aux)
    
    
    return jsonify(r)

@bp_cleaning.route('/outliers', methods=['GET'])
def outiliers():
    types = ['float64','int64','int','float']
    
    r = { 
        'barGraph' : {
            'data' : [{
                'x': [],
                'y': [],
                'type': 'bar'
            }],

            'layout' : {
                'title' : 'Numero de Valores Nulos',
                'autosize': True,
                'height': 300,
                'margin': {
                    'l': 50,
                    'r': 50,
                    'b': 50,
                    't': 50,
                    'pad': 4
                }

            }
        },
        'lineGraph' : {'data' : [],'layout': {}}
    }

    path = session['info_dataset']['path']
    data = pd.read_csv(path)
    time_feature = list(data[session['time_feature']])
    data = data[session['selected_features']]

    for cols in data.columns.values:
        c_type = data[cols].dtypes
        if c_type in types:
            r['barGraph']['data'][0]['x'].append(str(cols))

            z_scores = zscore(data[cols].values)
            abs_z_scores = np.abs(z_scores)
            filtered_entries = (abs_z_scores < 3)

            aux_sum_out = 0
            for i in range(len(filtered_entries)):
                filtered_entries[i] = bool(filtered_entries[i])
                if(filtered_entries[i] == False):
                    aux_sum_out += 1
                    filtered_entries[i] = True
                else:
                    filtered_entries[i] = False

            r['barGraph']['data'][0]['y'].append(aux_sum_out)

            r['lineGraph']['data'].append({
                'x' : time_feature,
                'y' : list(data[cols].values),
                'name' : cols,
                'type' : 'scatter'
            })
            null_time_features = [time_feature[x] for x in range(len(time_feature)) if filtered_entries[x] == True]

            r['lineGraph']['data'].append({
                'x' : null_time_features,
                'y' : list(data[cols][filtered_entries].values),
                'name' : f"Outliers {cols}",
                'type' : 'marker',
                'marker' : {
                    'color' : 'Red' 
                }
            })

            

    r['lineGraph']['layout'] = {
        'title' : 'outliers',
        'autosize': False,
        'height': 300,
        'margin': {
            'l': 50,
            'r': 50,
            'b': 50,
            't': 50,
            'pad': 4
        }
    }
            # r[cols] = [list(filtered_entries)]
    return jsonify(r)

@bp_cleaning.route('/')
def hello():
    return jsonify(session['info_dataset'])
    