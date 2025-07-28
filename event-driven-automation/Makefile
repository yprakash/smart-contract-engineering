PYTHONPATH := $(shell pwd):$(PYTHONPATH)

run-emitter:
	@echo "Running EventWatcher deploy script..."
	PYTHONPATH=$(PYTHONPATH) python3 script/deploy_watcher.py

run-listener:
	@echo "Running upkeep listener..."
	PYTHONPATH=$(PYTHONPATH) python3 script/upkeep_event_watcher.py

