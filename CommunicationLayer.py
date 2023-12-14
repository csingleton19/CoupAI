import time
from threading import Timer
from AIAgent import AIAgent

class CommunicationLayer:
    def __init__(self, player1, player2, max_exchanges=2, timeout_seconds=30):
        self.player1 = player1
        self.player2 = player2
        self.max_exchanges = max_exchanges
        self.timeout_seconds = timeout_seconds
        self.communication_log = []

    def format_communications(self, game_state = None):
        """
        Formats the communication log entries for display or processing.
        """
        formatted_communications = []
        for entry in self.communication_log[-2:]:  # Get the last two communications
            formatted_entry = {
                'sender': entry['sender'],
                'receiver': entry['receiver'],
                'action': entry['action'],
                'message': entry['message']
            }
            formatted_communications.append(formatted_entry)

        return formatted_communications

    def create_message_prompt(self, game_state, decision_type, additional_info=None):
        """
        Creates a prompt for messaging and communication decisions.
        """
        readable_game_state = self.format_communications(game_state)
        prompt = f"""Game state: {readable_game_state}\nDecision type: {decision_type}\nAdditional info: {additional_info}\n 
                  
                  You are the communication layer of an AIAgent that plays Coup. 
                  Your job is to process information sent by your opponent and respond, or initiate dialogue with your opponent. 
                  Lying, bluffing, and not responding are all acceptable actions as your main goal is to win.
                  Do not provide information about your hand unless you are bluffing. Don't trust everything your opponent says.
        """

        return prompt

    def send_message(self, sender, message):
        """ Logs a message sent by a player. """
        self.log_communication(sender.name, "Broadcast", "message", message)

    def receive_message(self, receiver):
        """ Handles receiving a message for a player. """
        messages_to_receiver = [msg for msg in self.communication_log if msg['receiver'] == receiver.name]
        if messages_to_receiver:
            last_message = messages_to_receiver[-1]
            print(f"Message to {receiver.name}: {last_message['message']}")
        else:
            print(f"No new messages for {receiver.name}")

    def start_exchange(self, initiating_player, responding_player, game_state):
        exchange_count = 0
        while exchange_count < self.max_exchanges:
            # Initiating player sends a message with a timeout
            initiating_message = self._send_with_timeout(initiating_player, game_state)
            self.log_communication(initiating_player.name, "Broadcast", "message", initiating_message)

            # Responding player reacts to the message with a timeout
            responding_message = self._send_with_timeout(responding_player, game_state, initiating_message)
            self.log_communication(responding_player.name, "Broadcast", "message", responding_message)

            exchange_count += 1

    def _send_with_timeout(self, player, game_state, message=None):
        # Set a timer for the player to send a message
        timeout = Timer(self.timeout_seconds, self.handle_timeout)
        timeout.start()

        # Player sends a message or reacts to a message
        if message:
            response = player.react_to_move(None, message, game_state)
        else:
            response = player.send_message(game_state)

        timeout.cancel()  # Cancel the timeout after the player sends a message
        return response

    def handle_timeout(self):
        print("Timeout occurred. Moving to next player's turn.")

    def log_communication(self, sender, receiver, action, message):
        self.communication_log.append({
            'sender': sender,
            'receiver': receiver,
            'action': action,
            'message': message
        })

    def get_communication_log(self):
        return self.communication_log

    def handle_timeout(self):
        print("Timeout occurred. Moving to next player's turn.")