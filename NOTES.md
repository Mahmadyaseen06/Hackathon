# Debugging & Gotchas Notes

- **XGBoost libomp runtime on macOS (Apple Silicon)**: `xgboost` requires `libomp.dylib` which was missing. Resolved by running `brew install libomp` and setting `DYLD_LIBRARY_PATH="/opt/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH"` / symlinking `/opt/homebrew/lib/libomp.dylib`.
- **Port 8000 conflict**: Port 8000 is occupied by a background uvicorn process (`trace-x`). Configured AI Placement Predictor FastAPI backend to run on port `8001` and Vite proxy to route `/api` requests to `http://127.0.0.1:8001`.
- **SHAP TreeExplainer expected_value dimension**: In recent SHAP binary classifier outputs, `explainer.expected_value` can be returned as a 1D array or list rather than scalar float. Handled with `float(np.ravel(exp_val)[0])`.
- **React component missing useState import**: `StudentDiagnostics.jsx` used `useState` without explicit import from `'react'`, throwing a runtime ReferenceError. Fixed by adding `import React, { useState } from 'react';` and wrapping the main application in a React `ErrorBoundary`.
- **FastAPI root route 404**: Accessing `http://127.0.0.1:8001/` returned `{"detail": "Not Found"}` because only `/api/*` endpoints were registered. Added `@app.get("/")` index route providing navigation links to `/docs`, `/api/health`, and frontend URL.
