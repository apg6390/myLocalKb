# Running myLocalKb

Use this after the one-time setup is complete.

## Windows PowerShell

Open PowerShell in the project folder:

```powershell
cd C:\Apurv\code_projects\claude\myLocalKb
```

Start Ollama in one PowerShell window:

```powershell
ollama serve
```

Leave that window open.

Open a second PowerShell window and start the app:

```powershell
cd C:\Apurv\code_projects\claude\myLocalKb
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

## If `uvicorn` Is Missing

If you see:

```text
No module named uvicorn
```

install the project dependencies into the Python you are using:

```powershell
cd C:\Apurv\code_projects\claude\myLocalKb
python -m pip install -r requirements.txt
```

Then run again:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

## Recommended Python Version

Use Python 3.11 or 3.12. If your default `python` is Python 3.14 and dependencies fail to install, install Python 3.12 and run:

```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

## Stop the App

In the PowerShell window running Uvicorn, press:

```text
Ctrl+C
```

