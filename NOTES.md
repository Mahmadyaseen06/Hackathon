# Debugging & Gotchas Notes

- **XGBoost libomp runtime on macOS (Apple Silicon)**: `xgboost` requires `libomp.dylib` which was missing. Resolved by running `brew install libomp` and setting `DYLD_LIBRARY_PATH="/opt/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH"` / symlinking `/opt/homebrew/lib/libomp.dylib`.
- **Port 8000 conflict**: Port 8000 is occupied by a background uvicorn process (`trace-x`). Configured AI Placement Predictor FastAPI backend to run on port `8001` and Vite proxy to route `/api` requests to `http://127.0.0.1:8001`.
- **Skill taxonomy normalizer substring collisions**: Shorter aliases (e.g. `js` for `javascript`) collided with composite strings like `react.js`. Solved by sorting aliases in descending order of length so specific names match before short abbreviations.
- **SHAP TreeExplainer expected_value dimension**: In recent SHAP binary classifier outputs, `explainer.expected_value` can be returned as a 1D array or list rather than scalar float. Handled with `float(np.ravel(exp_val)[0])`.
