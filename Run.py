import threading
from BotHandler import bot  # Import your Telegram bot instance
from Visualization import visual_by_month  # Import the Dash visualization function

def run_dash_app():
    """
    Start the Dash app (Visualization) in a separate thread.
    """
    try:
        visual_by_month()  # Start the Dash visualization server
    except Exception as e:
        print(f"Error starting Dash app: {e}")

if __name__ == '__main__':
    # Start Dash app in a separate thread
    dash_thread = threading.Thread(target=run_dash_app, daemon=True)
    dash_thread.start()  # Run Dash server in the background

    # Log messages to indicate the server and bot status
    print("Dash app is running at http://127.0.0.1:8050/")
    print("Telegram bot is now active...")

    # Start Telegram bot polling
    try:
        bot.polling()
    except Exception as e:
        print(f"Error running the bot: {e}")
