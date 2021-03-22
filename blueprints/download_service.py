import os
import uuid

from flask import Blueprint, current_app, jsonify, request, session, send_from_directory
from flask import send_file, redirect, url_for

import pandas as pd 
from pandas.api.types import is_numeric_dtype
from scipy.stats import zscore
import numpy as np

bp_download = Blueprint('bp_download', __name__)


# @app.route('/download')
def downloadFile (path):
    #For windows you need to use drive name [ex: F:/Example.pdf]
    return send_file(path, as_attachment=True)

@bp_download.route('/add_process', methods=['POST'])
def add_process():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()

            process = data['process']

            if process in current_app.config['ALL_PROCESS']:
                return jsonify('Ação já definida!')
            else:
                current_app.config['ALL_PROCESS'].append(process)
                return jsonify(current_app.config['ALL_PROCESS'])

@bp_download.route('/remove_process', methods=['POST'])
def remove_process():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()

            process = data['process']

            if process in current_app.config['ALL_PROCESS']:
                current_app.config['ALL_PROCESS'].remove(process)
                return jsonify(current_app.config['ALL_PROCESS'])
            else:
                return jsonify('Processo não encontrado')

def create_weekdays(days):
    date_days = pd.to_datetime(days)

    week_list = []
    for i in date_days:
        week_list.append(i.weekday())

    return week_list


def moment_day(days):
    date_days = pd.to_datetime(days)

    day_or_night = []
    for i in date_days:
        hours = str(i).split(' ')[1]
        hour = int(hours.split(':')[0])
        
        if (hour >= 6 and hour < 12):
            day_or_night.append(0)
        elif (hour >= 12 and hour < 18) :
            day_or_night.append(1)
        elif (hour >= 18 and hour < 24):
            day_or_night.append(2)
        elif (hour >= 0 and hour < 6):
            day_or_night.append(3)

    return day_or_night

@bp_download.route('/create_csvs', methods=['GET'])
def create_csvs():

    process_keys = current_app.config['ALL_PROCESS']

    
    path = session['info_dataset']['path']
    time_feature = session['time_feature']
    target_feature = session['target_feature']

    path_base = path.split('.')[0]
    data = pd.read_csv(path)

    csvs = []
   
    ## Limpeza
    if('fill_mean' in process_keys):
        csvs.append('clear_by_mean')
        data = data.fillna(data.mean)
        data.to_csv(f'{path_base}-clear_by_mean.csv')
        
    if('fill_median' in process_keys):
        csvs.append('clear_by_median')
        data = data.fillna(data.median)
        data.to_csv(f'{path_base}-clear_by_median.csv')
        
    if('dropna' in process_keys):
        csvs.append('clear_by_dropna')
        data = data.dropna()
        data.to_csv(f'{path_base}-clear_by_dropna.csv')
        
    
    ## Outliers
    if('outliers' in process_keys):
        csvs.append('outliers')
        data = data.fillna(data.mean)
        data.to_csv(f'{path_base}-outliers.csv')
        

    ## Duplicates
    if('duplicates_last' in process_keys):
        csvs.append('outliers')
        data = data.drop_duplicates(keep='last')
        data.to_csv(f'{path_base}-duplicate.csv')
        
    if('duplicates_first' in process_keys):
        csvs.append('outliers')
        data = data.drop_duplicates()
        data.to_csv(f'{path_base}-duplicate.csv')
        

    #Transformations
    if('weekdays' in process_keys):
        csvs.append('weekdays')
        data['dias_da_semana'] = create_weekdays(data[time_feature])
        data.to_csv(f'{path_base}-weekdays.csv')
    if('hours' in process_keys):
        csvs.append('hours')
        data['dia_ou_noite'] = moment_day(data[time_feature])
        data.to_csv(f'{path_base}-hours.csv')
    if('rolling' in process_keys):
        csvs.append('rolling')
        data['media_movel_5'] = data[target_feature].rolling(6).mean()
        data.to_csv(f'{path_base}-rolling.csv')

    data.to_csv(f'{path_base}-final.csv')
    return jsonify(csvs)
    # return redirect(url_for('bp_download.download_file'))


@bp_download.route('/get_csvs', methods=['GET'])
def get_csvs():
    return jsonify(current_app.config['ALL_PROCESS'])

@bp_download.route('/uploads/<path:filename>', methods=['GET'])
def download_file(filename):
    path = session['info_dataset']['path']

    path_base = path.split('.')[0]
    return send_file(f'{path_base}-{filename.split("+")[-1]}.csv', mimetype='application/x-csv', attachment_filename='summary_report.csv', as_attachment=True)

@bp_download.route('/download_final', methods=['GET'])
def download_file_final():
    path = session['info_dataset']['path']

    path_base = path.split('.')[0]
    return send_file(f'{path_base}-final.csv', mimetype='application/x-csv', attachment_filename='summary_report.csv', as_attachment=True)
