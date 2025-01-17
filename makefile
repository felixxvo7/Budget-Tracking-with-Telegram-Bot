# Define Python interpreter and files
PYTHON = python
BOT_HANDLER = BotHandler.py
VISUALIZATION = Visualization.py

# Target to run both the bot and visualization simultaneously
run-bot:
	$(PYTHON) $(BOT_HANDLER) 
run-dash:
	$(PYTHON) $(VISUALIZATION)

# Clean up (optional, for temp files or logs)
clean:
	rm -f *.log
