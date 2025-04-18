python -m venv .venv
source .venv/bin/activate
pip install poetry --index-url http://repo.hyundaicapital.com:8443/repository/pypi-public/simple/
poetry source add fossera http://repo.hyundaicapital.com:8443/repository/pypi-public/simple/
poetry install