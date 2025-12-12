import os
import time
import logging
from logging.handlers import RotatingFileHandler
import sys
from typing import List

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse, Response


### Конфигурация
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models")
LOG_FILE = os.getenv("LOG_FILE", "/app/logs/app.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


### Логгер
logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    LOG_FILE, maxBytes=1 * 1024 * 1024, backupCount=5, encoding="utf-8"
)

formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] '
    '[app_version=%(app_version)s model_version=%(model_version)s] '
    '%(message)s'
)

handler.setFormatter(formatter)
logger.addHandler(handler)

class VersionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.app_version = os.getenv("APP_VERSION", "blue")
        record.model_version = os.getenv("MODEL_VERSION", "v1.0.0")
        return True

logger.addFilter(VersionFilter())


## FastAPI
class UserRequest(BaseModel):
    x: List[float]

app = FastAPI()

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    method = request.method

    logger.info(f"Incoming request: {method} {path}")

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as exc:
        logger.exception(
            f"Unhandled exception while processing {method} {path}: {exc}"
        )
        status_code = 500
        response = JSONResponse(
            status_code=status_code,
            content={"status": "error", "detail": "Internal server error"},
        )

    latency = time.time() - start_time
    logger.info(
        f"Request handled: {method} {path} -> {status_code} "
        f"(latency={latency:.4f}s)"
    )

    return response


### Эндпоинты 

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {
        "status": "ok",
        "app_version": os.getenv("APP_VERSION", "blue"),
        "model_version": os.getenv("MODEL_VERSION", "v1.0.0"),
    }

@app.get("/health")
def health():
    logger.info("Health check called")
    return {
        "status": "ok", 
        "app_version": os.getenv("APP_VERSION", "blue"),
        "version": os.getenv("MODEL_VERSION", "v1.0.0")
    }

@app.post("/predict")
def predict(request: UserRequest):
    logger.info(f"/predict called with payload length={len(request.x)}")
    
    try:
        model_version = os.getenv("MODEL_VERSION", "v1.0.0")
        model_path = os.path.join(
            MODEL_PATH,
            f"model_{model_version}.pkl"
        )
        logger.info(f"Loading model from {model_path}")
        model = joblib.load(model_path)
        
        if len(request.x) != 4:
            raise ValueError(f"Expected 4 features, got {len(request.x)}")
        
        df = pd.DataFrame([{
                "sepal length (cm)": request.x[0],
                "sepal width (cm)": request.x[1],
                "petal length (cm)": request.x[2],
                "petal width (cm)": request.x[3]
            }])
        
        probas = model.predict_proba(df)
        preds = np.argmax(probas, axis=1)
        
        pred = model.classes_[preds[0]]
        confidence = probas[0][pred]
        
        logger.info(
            f"/predict success: prediction={pred}, confidence={confidence:.2f}"
        )
        
        return {
            "status": "ok", 
            "prediction": int(pred), 
            "confidence": float(confidence), 
            "app_version": os.getenv("APP_VERSION", "blue"),
            "version": os.getenv("MODEL_VERSION", "v1.0.0")
        }
    except Exception as e:
        logger.exception(f"/predict failed: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "detail": str(e),
                "app_version": os.getenv("APP_VERSION", "blue"),
                "version": os.getenv("MODEL_VERSION", "v1.0.0")
            },
        )