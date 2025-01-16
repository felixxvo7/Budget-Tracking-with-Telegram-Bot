# Define Python interpreter and files
PYTHON = python
BOT_HANDLER = BotHandler.py
VISUALIZATION = Visualization.py

# Target to run the Telegram bot
run-bot:
	$(PYTHON) $(BOT_HANDLER)

# Target to run the Dash visualization
run-visualization:
	$(PYTHON) $(VISUALIZATION)

# Target to run both the bot and visualization simultaneously
run-all:
	$(PYTHON) $(BOT_HANDLER) & \
	$(PYTHON) $(VISUALIZATION)

# Clean up (optional, for temp files or logs)
clean:
	rm -f *.log
