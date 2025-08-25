#!/bin/sh
# Start backend
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &

# Start frontend static server
serve -s frontend/out -l 3000

# Keep container running
wait
