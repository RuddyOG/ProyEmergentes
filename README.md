Proyecto de Emergentes:
## Requisitos
- Python 3.13.2

## Primer arranque
```powershell
# clona el repo y entra
git clone <url>
cd TecnologiasEmergentes

#1) crea tu entorno local (no se sube a git)
python -m venv .\.venv
.\.venv\Scripts\Activate.ps1

#2) instala dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt

#3) variables/config (si aplica)
copy .env.example .env

#4) preprocesa los CSV (EME-14)
python ".\backend\etl\preprocess.py"

