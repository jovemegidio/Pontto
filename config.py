import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'chave-padrao-dev')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///ponto.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NOME_EMPRESA = os.environ.get('NOME_EMPRESA', 'Minha Empresa')
    CARGA_HORARIA_DIARIA = int(os.environ.get('CARGA_HORARIA_DIARIA', 8))
