# Debugging & Gotchas Notes

- **XGBoost libomp runtime on macOS (Apple Silicon)**: `xgboost` requires `libomp.dylib` which was missing. Resolved by running `brew install libomp` and setting `DYLD_LIBRARY_PATH="/opt/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH"` / symlinking `/opt/homebrew/lib/libomp.dylib`.
- **Port 8000 conflict**: Port 8000 is occupied by a background uvicorn process (`trace-x`). Configured AI Placement Predictor FastAPI backend to run on port `8001` and Vite proxy to route `/api` requests to `http://127.0.0.1:8001`.
