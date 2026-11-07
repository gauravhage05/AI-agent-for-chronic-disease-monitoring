import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    WATSONX_APIKEY = os.getenv("WATSONX_APIKEY", "").strip()
    WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "").strip()
    WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com").strip()
    GRANITE_MODEL_ID = os.getenv("GRANITE_MODEL_ID", "ibm/granite-3-8b-instruct").strip()
    CLOUDANT_URL = os.getenv("CLOUDANT_URL", "").strip()
    CLOUDANT_APIKEY = os.getenv("CLOUDANT_APIKEY", "").strip()
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1")

    @classmethod
    def is_watsonx_configured(cls):
        return bool(cls.WATSONX_APIKEY and cls.WATSONX_PROJECT_ID)
