import os
import uuid

from flask import Blueprint, current_app, jsonify, request, session

import pandas as pd 
from pandas.api.types import is_numeric_dtype


bp_dataset = Blueprint('bp_dataset', __name__)

# session['time_feature'] = ''
# session['selected_features'] = []

ALLOWED_EXTENSIONS = ["csv"]

@bp_dataset.route('/')
def hello():
    return jsonify(session['info_dataset'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def change_filename_to_unique(filename):
    name, ext = filename.split('.')
    return f'{name}-{uuid.uuid4()}.{ext}'


@bp_dataset.route('/load_dataset', methods=['POST'])
def load_dataset():

    if request.method == 'POST':
        file = request.files['file_dataset']

        if not allowed_file(file.filename):
            return {
                "message":
                "file with extension not allowed try {}".format(
                    " or ".join(ALLOWED_EXTENSIONS))
            }

        unique_filename = change_filename_to_unique(file.filename)
        
        full_filename = os.path.join(
            current_app.config['UPLOAD_FOLDER_DATASET'], unique_filename)
        
        file.save(full_filename)

        # Save dataset in database
        new_dataset = get_info_columns_dataset(full_filename, unique_filename)

      
        session['info_dataset'] = new_dataset

        return jsonify(new_dataset['columns'])
    else:
        return {"message": "try a POST request"}

def get_info_columns_dataset(full_filename, unique_filename):

    df_dataset = pd.read_csv(full_filename)

    # Create obj columns
    info_dataset = {'columns' : [], 'columns_name' : []}

    for name in df_dataset.columns:

        info_dataset['columns_name'].append(str(name))

        type_column = df_dataset[name].dtypes
        quantity_miss_values = int(df_dataset[name].isnull().sum())
        print(name, quantity_miss_values, type(quantity_miss_values))

        if is_numeric_dtype(type_column):
            describe = df_dataset[name].describe()
            max_value = int(describe['max'])
            min_value = int(describe['min'])
            std_value = describe['std']

            print(name, max_value, min_value, std_value)

            new_column = {'name': name, 'type': str(type_column), 
                         'qtd_miss_values' : quantity_miss_values, 'max_value' :max_value, 
                         'min_value' : min_value, 'std_value' : std_value}
        else:
           new_column = {'name': name, 'type': str(type_column), 
                         'qtd_miss_values' : quantity_miss_values}
        info_dataset['columns'].append(new_column)


    folder_name_dataset = full_filename.split('/')[-2]
    info_dataset['path'] = f'{folder_name_dataset}/{unique_filename}'
    info_dataset['size_in_bytes'] = os.path.getsize(full_filename)

    return info_dataset

@bp_dataset.route('/get_columns_name', methods=['GET'])
def get_columns_name():
    return jsonify(session['info_dataset']['columns_name'])

@bp_dataset.route('/calc_corr', methods=['POST'])
def calc_corr():
    if request.method == 'POST':

        current_app.config['ALL_PROCESS'].clear()

        if request.is_json:
            data = request.get_json()
        
            
            target_feature = data['target_feature']

            session['target_feature'] = target_feature

            # Testar de se path estar dentro session
            path = session['info_dataset']['path']
            df_dataset = pd.read_csv(path)

            corr_df = df_dataset.corr()

            corr_target = corr_df[target_feature]

            columns_corrs = []

            for column in session['info_dataset']['columns']:
                if column['name'] in list(corr_target.keys()):
                    column['corr'] = corr_target[column['name']]
                    columns_corrs.append(column)
    
            return jsonify(columns_corrs)

@bp_dataset.route('/select_features', methods=['POST'])
def define_features():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()

            print(data)
            
            selected_features = data['selected_features']

            print(selected_features)
            
            session['time_feature'] = data['time_feature']
            
            session['selected_features'] = list(selected_features)
            
            return jsonify(session['selected_features'])


   