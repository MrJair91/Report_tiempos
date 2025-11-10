import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'reporte_tiempos.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'clave_secreta_segura'
