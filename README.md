# Binance Futures Simulation

A small Python app to simulate Binance futures strategies.

**Requirements:**
- Python 3.8+ (3.10+ recommended)
- `requirements.txt` lists project dependencies

**Setup (PowerShell)**

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. (Optional) Edit `config.py` if you need to set API keys or other settings.

**Run**

From the project root run:

```powershell
python main.py
```

**Files of interest**
- `main.py` — program entrypoint
- `config.py` — configuration (API keys, params)
- `strategy.py` — trading strategy logic
- `binance_client.py` — Binance API client wrapper

**Notes**
- The app may expect environment-specific settings in `config.py`.
- If you run into missing dependencies, confirm your active Python interpreter and that the virtualenv is activated.

If you want, I can also add a small `README` section showing how to run with different Python versions or how to run tests.
