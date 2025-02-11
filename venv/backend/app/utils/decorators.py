# src/utils/decorators.py
from functools import wraps
import time
from flask import request
from app.utils.logger import logger

def timing_decorator(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        logger.info(f'Route {f.__name__} took: {end-start:.2f} seconds')
        return result
    return wrap

def log_request_info():
    logger.debug(f"Request Method: {request.method}, URL: {request.url}, Data: {request.data}")
