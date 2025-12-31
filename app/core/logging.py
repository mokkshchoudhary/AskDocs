import logging
import sys
import json
from app.core.config import settings

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
        }
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        return json.dumps(log_obj)

def setup_logging():
    logger = logging.getLogger("askdocs")
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    # Also configure uvicorn to use our format if needed, but for now just app logger
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING) # Reduce noise
    
    return logger

logger = setup_logging()
