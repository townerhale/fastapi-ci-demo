# run.py
#!/usr/bin/env python3
import os
import uvicorn

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    # Enable autoreload by default for local dev; disable with RELOAD=false
    reload = os.getenv("RELOAD", "true").lower() in ("1", "true", "yes", "on")

    # Run: python run.py   (or)   HOST=127.0.0.1 PORT=8000 python run.py
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
