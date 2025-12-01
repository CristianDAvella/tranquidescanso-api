import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user_api:van3m6CF2VGKrXOu83VLUf1sBOCmcasd@dpg-d4mr30muk2gs7398arjg-a.virginia-postgres.render.com/tranquidescanso_nqep"
)

# Configuración general
APP_NAME = "TRANQUIDESCANSO API"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False") == "True"
