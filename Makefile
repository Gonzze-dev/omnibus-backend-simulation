PORT = 4990
VENV_NAME = virtual-env
VENV_PYTHON = $(VENV_NAME)/Scripts/python

run:
	$(VENV_PYTHON) -m uvicorn app.main:app --reload --port $(PORT)

run-with-out-ide:
	$(VENV_PYTHON) -m uvicorn app.main:app --reload --port $(PORT)

update-dates:
	$(VENV_PYTHON) update_dates.py

seed-terminals:
	$(VENV_PYTHON) seed_terminals.py
