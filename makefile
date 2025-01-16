# Define Python interpreter and files
PYTHON = python
BOT_HANDLER = BotHandler.py
VISUALIZATION = Visualization.py

# Target to run both the bot and visualization simultaneously
run:
	$(PYTHON) $(VISUALIZATION)& \
	$(PYTHON) $(BOT_HANDLER) 

# Clean up (optional, for temp files or logs)
clean:
	rm -f *.log
