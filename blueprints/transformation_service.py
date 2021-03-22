import os
import uuid

from flask import Blueprint, current_app, jsonify, request, session

import pandas as pd 
from pandas.api.types import is_numeric_dtype
from scipy.stats import zscore
import numpy as np

bp_transformation = Blueprint('bp_transformation', __name__)


@bp_transformation.route('/', methods=['GET'])
def transformation():
    path = session['info_dataset']['path']
    data = pd.read_csv(path)
    
    selected_features = session['selected_features']
    time_feature_name = session['time_feature']
    # time_feature_list = list(data[session['time_feature']])
    new_time_feature = list(pd.to_datetime(data[time_feature_name]))
  
    data = data.set_index(time_feature_name)
    data.index = pd.to_datetime(data.index)

    
    hour = 25
    
    data = data[selected_features]


    r = {
        'box_plot_weekdays' : {
            'text' : 'Baseado na distribuição apresentada, acredita que a relação entre os dias da semana e os dados presente na sua base, é uma informação relevante e pode ser incoporada na base pela inclusão de um novo atributo?'
        },
        'line_plot_months' : {
            'text' : 'Acredita que a média movel do seu atributo alvo é uma informação relevante e pode ser incorporada ao dados com um novo atributo chamado "media_movel_5"?'},
        'box_plot_hours' : {
            'text' : 'Baseado na distribuição apresentada, acredita que a informação sobre o périodo do dia, associada a sua base de dados é relevante e pode ser incoporada na base?'
        }
    }
    
    for cols in data.columns.values:
        r['line_plot_months'][cols] = {
            'data' : {
                f'{cols}_movel' : {},
                f'{cols}' : {},
            },
            'layout' : {
                'title': 'Média movel com uma janela de tamanho 5',
                # 'plot_bgcolor': "#1e1e1e",
                # 'paper_bgcolor': "#1e1e1e", #COLOR DO PAPER
                'autosize' : True,
                'height': 350,
                'margin': {
                    'l': 50,
                    'r': 50,
                    'b': 50,
                    't': 50,
                    'pad': 4
                }
            }
        }
        
        r['box_plot_hours'][cols] = {
            'data' : {
                'manha_1' : {
                    'y' : [],
                    'type' : 'box',
                    'name' : '6:01 - 12:00'
                },
                'manha_2' : {
                    'y' : [],
                    'type' : 'box',
                    'name' : '12:01 - 18:00'
                },
                'noite_1' : {
                    'y' : [],
                    'type' : 'box',
                    'name' : '18:01 - 00:00'
                },
                'noite_2' : {
                    'y' : [],
                    'type' : 'box',
                    'name' : '00:01 - 6:00'
                }
            },
            'layout':{
                'title': 'Distruibuição dos valores apresentados de acordo com o périodo do dia',
                'plot_bgcolor': "#1e1e1e",
                'autosize' : True,
                'height': 350,
                'margin': {
                    'l': 50,
                    'r': 50,
                    'b': 50,
                    't': 50,
                    'pad': 4
                }      
            }
        }

        r['box_plot_weekdays'][cols] = {
            'data': {
                '1' : {
                    'y': [],
                    'type' : 'box',
                    'name' : 'Segunda'
                },
                '2' :{
                    'y': [],
                    'type' : 'box',
                    'name' : 'Terça'
                },
                '3' : {
                    'y': [],
                    'type' : 'box',
                    'name' : 'Quarta'
                },
                '4' : {
                    'y': [],
                    'type' : 'box',
                    'name' : 'Quinta'
                },
                '5' : {
                    'y': [],
                    'type' : 'box',
                    'name' : 'Sexta'
                },
                '6' : {
                    'y': [],
                    'type' : 'box',
                    'name' : 'Sabado'
                },
                '0' : {
                    'y': [],
                    'type' : 'box',
                    'name' : 'Domingo'
                }
            },
            'layout': {
                'title': 'Distruibuição dos valores apresentados de acordo com os dias da semana',
                'plot_bgcolor': "#1e1e1e",
                'autosize' : True,
                'height': 350,
                'margin': {
                    'l': 50,
                    'r': 50,
                    'b': 50,
                    't': 50,
                    'pad': 4
                }
            }  
         }
    
    # new_time_feature = list(pd.to_datetime(data[time_feature_name]))

    # mask = "M"
    granularidade = "days"
    for i in new_time_feature[:5]:
        if (str(i).split(' ')[1] != "00:00:00"):
            granularidade = "hours"
            # mask = "D"


    for i in range(len(new_time_feature)):
        #Para pegar o dia da semana
        day_weekday = str(new_time_feature[i].weekday())
        
        #Para pegar agrupamentos pelo ano-mês
        day = str(new_time_feature[i]).split(' ')

        if (len(day) > 1):
            hour = int(day[1].split(':')[0])
        
        for cols in data.columns.values:
        
            r['box_plot_weekdays'][cols]['data'][day_weekday]['y'].append(data[cols].iloc[i])

            if(granularidade == "hours"):
                if (hour >= 6 and hour < 12):
                    r['box_plot_hours'][cols]['data']['manha_1']['y'].append(data[cols].iloc[i])
                elif (hour >= 12 and hour < 18) :
                    r['box_plot_hours'][cols]['data']['manha_2']['y'].append(data[cols].iloc[i])
                elif (hour >= 18 and hour < 24):
                    r['box_plot_hours'][cols]['data']['noite_1']['y'].append(data[cols].iloc[i])
                elif (hour >= 0 and hour < 6):
                    r['box_plot_hours'][cols]['data']['noite_2']['y'].append(data[cols].iloc[i])
    
    #Infos do dataset pela granularidade
    for cols in data.columns.values:
   
        aux = data[cols].rolling(6).mean()
        print(aux.values)
        r['line_plot_months'][cols]['data'][f'{cols}_média'] = {
            'x' : [i for i in list(data.index)],
            'y' : list(aux.values)[5:],
            'type' : 'scatter',
            'name' : f'{cols}_média'
        }

        r['line_plot_months'][cols]['data'][f'{cols}'] = {
            'x' : [i for i in new_time_feature],
            'y' : list(data[cols].values),
            'type' : 'scatter',
            'name' : f'{cols}'
        }

        
            
    return jsonify(r)