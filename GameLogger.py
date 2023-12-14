class GameLogger:
    def __init__(self):
        self.logs = []

    def log(self, message):
        """Logs a message."""
        self.logs.append(message)
        print(message)  # Optionally, print the message in real-time

    def get_logs(self):
        """Returns all the logs."""
        return self.logs
