.PHONY: dev bot

dev:
	python3 -m venv venv
	. ./venv/bin/activate && pip install -r requirements.txt
	cp -n .env.dist .env || true
	@echo "\n--------------------------------------------------------------------\n\nRun:\n. ./venv/bin/activate\n"

bot:
	uvicorn server:app --host=0.0.0.0 --reload
