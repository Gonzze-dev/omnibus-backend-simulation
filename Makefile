PORT = 4990
VENV_NAME = virtual-env
VENV_PYTHON = $(VENV_NAME)/Scripts/python

run:
	$(VENV_PYTHON) -m uvicorn app.main:app --reload --port $(PORT)

run-with-out-ide:
	$(VENV_PYTHON) -m uvicorn app.main:app --reload --port $(PORT)

migrate-up:
	$(VENV_PYTHON) migrate.py up

migrate-status:
	$(VENV_PYTHON) migrate.py status

migrate-baseline:
	$(VENV_PYTHON) migrate.py baseline

update-dates:
	$(VENV_PYTHON) update_dates.py

seed-terminals:
	$(VENV_PYTHON) seed_terminals.py
