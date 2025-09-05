#!/usr/bin/env python3

import sys
import uvicorn
from src.api.routes import app
from src.core.config import settings

if __name__ == "__main__":
    try:
        settings.validate()
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except Exception as e:
        print(f"Failed to start application: {e}", file=sys.stderr)
        sys.exit(1)