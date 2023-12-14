import random
from GameLogger import GameLogger


class Player:
    def __init__(self, name, character):
        self.name = name
        self.character = character
        self.coins = 2  # Starting coins
        self.cards = []  # Starting cards (represents influence)

    def choose_action(self, game):
        """Allows the player to choose an action, including bluffing."""
        actions = ['income', 'foreign_aid', 'coup', 'tax', 'assassinate', 'steal', 'exchange']
        
        print(f"\n{self.name}'s turn. Coins: {self.coins}, Cards: {len(self.cards)}")
        for i, action in enumerate(actions):
            print(f"[{i + 1}] {action}")

        while True:  # Loop until valid input is received
            choice = input("Enter your choice: ")
            if choice.isdigit():
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(actions):
                    return actions[choice_index]
                else:
                    print("Invalid choice. Please enter a number corresponding to an action.")
            else:
                print("Invalid input. Please enter a number.")

    def choose_target(self, game):
        """Allows the player to choose a target for certain actions."""
        valid_targets = self.get_available_targets(game)

        # Check if there are valid targets
        if not valid_targets:
            print("No available targets.")
            return None

        print("Choose a target:")
        for i, player in enumerate(valid_targets):
            print(f"[{i + 1}] {player.name}")

        while True:  # Loop until valid input is received
            choice = input("Enter the number of the target player: ")
            if choice.isdigit():
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(valid_targets):
                    return valid_targets[choice_index]
                else:
                    print("Invalid choice. Please select a valid target.")
            else:
                print("Invalid input. Please enter a number.")

    def send_message(self, game_state = None):
        """ Prompt the player to send a message, considering the game state. """
        message = input(f"{self.name}, enter a message to send: ")
        return message
    
    def react_to_move(self, action, message, game_state):
        """ Human player reacts to an incoming action and message. """
        print(f"\n{self.name}, you received an action: {action} and a message: {message}")
        response = input("Enter your response: ")
        return response
    
    def has_influence(self):
        """Check if the player still has cards (influence)."""
        return len(self.cards) > 0

    def interact_with_communication_layer(self, communication_layer, game_state):
        """Interact with the CommunicationLayer for messaging."""
        # Sending a message
        message = self.send_message()
        communication_layer.send_message(self, message)

        # Optionally, you can also include receiving a message
        communication_layer.receive_message(self)

    def draw_card(self, deck):
        """
        Draws a card from the deck and adds it to the player's hand.
        """
        if deck:
            new_card = deck.pop()  # Remove a card from the top of the deck
            self.cards.append(new_card)  # Add the new card to the player's hand

    def get_available_targets(self, game):
        """Returns a list of players that can be targeted for certain actions."""
        return [player for player in game.players if player != self and player.has_cards()]

    def take_action(self, game):
        """The player takes an action using their character."""
        action = self.choose_action(game)
        target_player = None

        if isinstance(action, tuple):  # Handling AI's action and target
            action, target_player = action

        if action in ['coup', 'assassinate', 'steal']:
            target_player = game.choose_target(self)

        # Execute action through the character, passing the game and target player (if any)
        self.character.action(self, game, target_player)

    def wants_to_challenge(self, acting_player, action):
        """Determines if the player wants to challenge an action."""
        while True:
                choice = input(f"Do you want to challenge {acting_player.name}'s {action}? (yes/no): ").lower().strip()
                if choice in ['yes', 'no']:
                    return choice == 'yes'
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")

    def wants_to_block(self, acting_player, action):
        """Determines if the player wants to block an action."""
        while True:
                choice = input(f"Do you want to block {acting_player.name}'s {action}? (yes/no): ").lower().strip()
                if choice in ['yes', 'no']:
                    return choice == 'yes'
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")
    
    def gain_coins(self, amount):
        """Method for the player to gain coins."""
        self.coins += amount

    def lose_coins(self, amount):
        """Method for the player to lose coins. Ensures coins don't go negative."""
        self.coins = max(self.coins - amount, 0)

    def lose_influence(self):
        """Method for the player to lose influence. Influence represents cards in hand."""
        if self.cards:
            lost_card = self.cards.pop()  # Remove a card when losing influence
            print(f"{self.name} loses a card: {lost_card}. Remaining cards: {len(self.cards)}")
            if not self.cards:
                print(f"{self.name} has no more influence and is out of the game!")

    def has_cards(self):
        """Check if the player still has cards (influence)."""
        return bool(self.cards)
    
    
    def verify_card(self, action):
        """Verifies if the player has the card related to the action."""

        # Map actions to character names
        action_to_card_map = {
            'income': None,              # Any character can take 'income' action
            'foreign_aid': None,         # Any character can take 'foreign_aid' action
            'coup': None,                # 'Coup' can be done by anyone, doesn't require a specific card
            'tax': 'Duke',               # 'Duke' can take the 'tax' action
            'assassinate': 'Assassin',   # 'Assassin' can take the 'assassinate' action
            'steal': 'Captain',          # 'Captain' can take the 'steal' action
            'exchange': 'Ambassador',    # 'Ambassador' can take the 'exchange' action
            'block_foreign_aid': 'Duke', # 'Duke' can block 'foreign_aid'
            'block_steal': 'Captain',    # 'Captain' can block 'steal'
            'block_steal_ambassador': 'Ambassador', # 'Ambassador' can also block 'steal'
            'block_assassinate': 'Contessa',        # 'Contessa' can block 'assassinate'
    }    

        required_card = action_to_card_map.get(action, None)
        if required_card is None:  # If no specific card is required for the action
            return True  # Cannot bluff if the action doesn't require a card

        # Check if the player has the required card in their hand
        return required_card in self.cards
    
    def shuffle_in_card(self, action, deck):
        """
        Shuffles the player's card associated with the action back into the deck 
        and draws a new card from the deck.
        """
        # Map actions to character names
        action_to_card_map = {
            'income': None,              # Any character can take 'income' action
            'foreign_aid': None,         # Any character can take 'foreign_aid' action
            'coup': None,                # 'Coup' can be done by anyone, doesn't require a specific card
            'tax': 'Duke',               # 'Duke' can take the 'tax' action
            'assassinate': 'Assassin',   # 'Assassin' can take the 'assassinate' action
            'steal': 'Captain',          # 'Captain' can take the 'steal' action
            'exchange': 'Ambassador',    # 'Ambassador' can take the 'exchange' action
            'block_foreign_aid': 'Duke', # 'Duke' can block 'foreign_aid'
            'block_steal': 'Captain',    # 'Captain' can block 'steal'
            'block_steal_ambassador': 'Ambassador', # 'Ambassador' can also block 'steal'
            'block_assassinate': 'Contessa',        # 'Contessa' can block 'assassinate'
        }    

        card_to_shuffle_back = action_to_card_map.get(action, None)
        if card_to_shuffle_back and card_to_shuffle_back in self.cards:
            self.cards.remove(card_to_shuffle_back)
            deck.append(card_to_shuffle_back)
            random.shuffle(deck)
            new_card = deck.pop() if deck else None
            if new_card:
                self.cards.append(new_card)

    def choose_exchange_cards(self, num_cards_to_exchange):
        """
        Allows the player to choose which cards to exchange.
        """
        if num_cards_to_exchange > len(self.cards):
            print("Not enough cards to exchange.")
            return []

        print(f"\n{self.name}, choose {num_cards_to_exchange} card(s) to exchange.")
        for i, card in enumerate(self.cards):
            print(f"[{i + 1}] {card}")

        chosen_cards = []
        while len(chosen_cards) < num_cards_to_exchange:
            choice = input(f"Choose card {len(chosen_cards) + 1}: ")
            if choice.isdigit():
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(self.cards):
                    chosen_card = self.cards[choice_index]
                    if chosen_card not in chosen_cards:  # Ensure the same card is not selected multiple times
                        chosen_cards.append(chosen_card)
                    else:
                        print("You have already selected this card. Please choose a different card.")
                else:
                    print("Invalid choice. Please select a valid card.")
            else:
                print("Invalid input. Please enter a number.")
        return chosen_cards



    
