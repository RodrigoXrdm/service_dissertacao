import os
from flask import Flask
from flask_cors import CORS

# Analysis Blueprint
from service_dissetacao.blueprints.dataset_service import bp_dataset
from service_dissetacao.blueprints.cleaning_service import bp_cleaning
from service_dissetacao.blueprints.transformation_service import bp_transformation
from service_dissetacao.blueprints.download_service import bp_download

# from flask_session import Session

def create_app():
    app = Flask(__name__, static_folder='static')

    # Create two constant. They direct to the app root folder and logo upload folder
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    FOLDER_NAME_DATASET = 'upload_folder_datasets'
    UPLOAD_FOLDER_DATASET = os.path.join(APP_ROOT, FOLDER_NAME_DATASET)
    PATH_DOWNLOAD = 'static'
    # ALL_PROCESS = []
    
    app.config['SECRET_KEY'] = 'you-will-never-guess'

    app.config['UPLOAD_FOLDER_DATASET'] = UPLOAD_FOLDER_DATASET
    app.config['APP_ROOT'] = APP_ROOT
    # app.config['PROCESS'] = []
    app.config['ALL_PROCESS'] = []
    app.config['PATH_DOWNLOAD'] = PATH_DOWNLOAD

    # app.config['SESSION_TYPE'] = 'filesystem'
    # app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

    app.config['CORS_SUPPORTS_CREDENTIALS'] = True

    # Configure session
    #Session(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.register_blueprint(bp_dataset, url_prefix='/bp_dataset')
    app.register_blueprint(bp_cleaning, url_prefix='/bp_cleaning')
    app.register_blueprint(bp_transformation, url_prefix='/bp_transformation')
    app.register_blueprint(bp_download, url_prefix='/bp_download')

    # Temporary: Populate models
    # populate_init_models(app)

    return app
