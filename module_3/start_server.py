#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Server startup script"""
import uvicorn
import sys
import os

if __name__ == "__main__":
    print("=" * 60)
    print("System Monitoring API Server")
    print("=" * 60)
    print("\nStarting server on http://localhost:8000")
    print("\nAvailable endpoints:")
    print("  - Swagger UI:  http://localhost:8000/docs")
    print("  - ReDoc:       http://localhost:8000/redoc")
    print("  - Health:      http://localhost:8000/api/v1/health")
    print("  - Metrics:     http://localhost:8000/api/v1/metrics/current")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60 + "\n")

    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
