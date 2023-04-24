.PHONY: dev bot

dev:
	python3 -m venv venv
	. ./venv/bin/activate && pip install -r requirements.txt
	cp .env.dist .env
	@echo "\n--------------------------------------------------------------------\n\nRun:\n. ./venv/bin/activate\n"

bot:
	python -m bot
