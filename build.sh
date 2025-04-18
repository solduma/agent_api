arch -arm64 python3 -m venv .venv
source .venv/bin/activate
pip install poetry --index-url http://repo.hyundaicapital.com:8443/repository/pypi-public/simple/
poetry install