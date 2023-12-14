from GameLogger import GameLogger
from GameState import GameState
import random
from AIAgent import AIAgent
from CommunicationLayer import CommunicationLayer


class Game:
    def __init__(self, players):
        self.players = players
        self.logger = GameLogger()
        self.deck = CardManager.initialize_deck()
        self.turn_manager = TurnManager(self)
        self.action_handler = ActionHandler(self)
        self.challenge_handler = ChallengeHandler(self)
        self.game_state = GameState()
        self.communication_layer = None  # Initialize as None

    def initialize_communication_layer(self):
        if len(self.players) >= 2:
            self.communication_layer = CommunicationLayer(self.players[0], self.players[1])
        else:
            raise ValueError("Not enough players to initialize communication layer")

    def action_requires_coins(self, action):
        """Check if the given action requires coins."""
        actions_requiring_coins = ['coup', 'assassinate']
        return action in actions_requiring_coins

    def start_game(self):
        self.initialize_communication_layer()
        self.logger.log("Game has started")
        # Initialize GameState for each player
        for player in self.players:
            self.game_state.add_player(player.name)

        # Distribute cards to each player and update GameState
        for player in self.players:
            player.cards = [self.deck.pop() for _ in range(2)]
            print(f"{player.name} received initial cards: {', '.join(player.cards)}")
            self.logger.log(f"{player.name} received their initial cards.")
            self.game_state.update_player_cards(player.name, player.cards)

        # Update GameState with the remaining deck size
        self.game_state.update_deck_size(len(self.deck))

        # Start the game loop
        while not self.is_game_over():
            self.turn_manager.play_turn()
            self.game_state.update_deck_size(len(self.deck))

        self.announce_winner()
        self.ask_restart_game()

    def is_game_over(self):
        # The game is over if only one or no players have cards left
        active_players = [player for player in self.players if player.has_cards()]
        return len(active_players) <= 1
    
    def run_communication_phase(self):
        for player in self.players:
            other_player = next(p for p in self.players if p != player)
            if isinstance(player, AIAgent):
                player.interact_with_communication_layer(self.communication_layer, self.game_state.get_public_game_state())
            else:
                self.communication_layer.start_exchange(player, other_player, self.game_state.get_public_game_state())

            # Print the latest entries in the communication log
            self.print_communication_log()

    def print_communication_log(self):
        print("---- Communication Log ----")
        for entry in self.communication_layer.get_communication_log()[-2:]:  # Get the last two entries
            print(f"Sender: {entry['sender']}, Receiver: {entry['receiver']}, Message: {entry['message']}")
        print("----------------------------")

    def announce_winner(self):
        winner = next((player for player in self.players if player.has_cards()), None)
        if winner:
            self.logger.log(f"Game over! The winner is {winner.name}.")
            self.game_state.set_winner(winner.name)  # Log the winner in GameState
        else:
            self.logger.log("Game over! No winner.")
            self.game_state.set_winner(None)  # No winner

        # Log final game state
        final_state = self.game_state.get_game_state()
        print(f"Final Game State: {final_state}")

    def ask_restart_game(self):
        while True:  # Loop until a valid input is received
            choice = input("Do you want to play again? (yes/no): ").lower().strip()
            if choice == 'yes':
                self.reset_game()
                break  # Break the loop if valid input is received
            elif choice == 'no':
                self.logger.log("Exiting game. Thank you for playing!")
                break  # Break the loop if valid input is received
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

    def reset_game(self):
        self.logger.log("Resetting game...")
        self.deck = CardManager.initialize_deck()
        for player in self.players:
            player.cards = []
            player.coins = 2
            # Reinitialize GameState for each player
            self.game_state.add_player(player.name)
        # Call distribute_cards with game_state
        CardManager.distribute_cards(self.players, self.deck, self.logger, self.game_state)
        self.turn_manager.current_turn = 0
        self.start_game()

    def choose_target(self, acting_player):
        valid_targets = [player for player in self.players if player != acting_player and player.has_cards()]
        print("Choose a target:")
        for i, player in enumerate(valid_targets):
            print(f"{i + 1}: {player.name}")

        while True:
            choice = input("Enter the number of the target player: ")
            if choice.isdigit():
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(valid_targets):
                    return valid_targets[choice_index]  # Return the player object, not just the name
                else:
                    print("Invalid choice. Please select a valid target.")
            else:
                print("Invalid input. Please enter a number.")



class TurnManager:
    def __init__(self, game):
        self.game = game
        self.current_turn = 0

    def play_turn(self):
        if self.game.is_game_over():
            self.game.announce_winner()
            return

        turn_player = self.game.players[self.current_turn]

        if not turn_player.has_influence():
            self.game.logger.log(f"{turn_player.name} has no influence and is out of the game.")
            self.next_turn()
            return

        self.game.logger.log(f"{turn_player.name}'s turn begins.")
        action_successful, challenge_failed, action_blocked = self.perform_action(turn_player)

        # Move to the next turn if the action was successful, if a challenge failed, or if an action was blocked
        if action_successful or challenge_failed or action_blocked:
            self.game.run_communication_phase()
            self.next_turn()

    def perform_action(self, turn_player):
        while True:
            action = turn_player.choose_action(self.game.game_state)
            if action not in self.game.action_handler.valid_actions:
                self.game.logger.log(f"Invalid action: {action}. Please try again.")
                continue

            target_player = None
            if action in ['coup', 'assassinate', 'steal']:
                target_player = turn_player.choose_target(self.game)

            action_result = self.game.action_handler.handle_action(action, turn_player, target_player)
            action_successful, reason = action_result if isinstance(action_result, tuple) else (action_result, 'success' if action_result else 'unspecified')
            self.game.game_state.log_action(turn_player.name, action, reason)
            self.game.logger.log(f"Action Result: {action_result}, Successful: {action_successful}, Reason: {reason}")

            challenge_failed = reason == 'challenge_failed'
            action_blocked = reason == 'blocked'
            return action_successful, challenge_failed, action_blocked

    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % len(self.game.players)
        self.game.logger.log(f"Turn moves to player index {self.current_turn}.")
        self.game.game_state.current_turn = self.current_turn

    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % len(self.game.players)
        self.game.logger.log(f"Turn moves to player index {self.current_turn}.")



class ActionHandler:
    def __init__(self, game):
        self.game = game
        self.valid_actions = {'income', 'foreign_aid', 'coup', 'tax', 'assassinate', 'steal', 'exchange'}

    def handle_action(self, action, player, target_player=None):
        # Existing debug print statement
        print(f"Handling action: {action} for player: {player.name}, type: {type(action)}")

        # Check action and call the corresponding method
        if action == "income":
            return self.income(player)
        elif action == "foreign_aid":
            return self.foreign_aid(player)
        elif action == "coup":
            return self.coup(player, target_player)
        elif action == "tax":
            return self.tax(player)
        elif action == "assassinate":
            return self.assassinate(player, target_player)
        elif action == "steal":
            return self.steal(player, target_player)
        elif action == "exchange":
            return self.exchange(player)
        else:
            # Log the invalid action
            self.game.logger.log(f"Invalid action attempted: {action} by {player.name}")
            self.game.game_state.log_action(player.name, action, 'invalid')
            return False, 'invalid_action'

    def income(self, player):
        self.game.logger.log(f"{player.name} takes Income action.")
        player.gain_coins(1)
        self.game.game_state.update_player_coins(player.name, player.coins)  # Update GameState
        self.game.game_state.log_action(player.name, 'income', 'success')
        return True, 'success'

    def foreign_aid(self, player):
        self.game.logger.log(f"{player.name} attempts Foreign Aid action.")
        for potential_blocker in self.game.players:
            if potential_blocker != player and potential_blocker.wants_to_block(player, 'foreign_aid'):
                if self.game.challenge_handler.resolve_block(player, potential_blocker, 'foreign_aid'):
                    self.game.game_state.log_action(player.name, 'foreign_aid', 'blocked')
                    return False, 'blocked'
        
        player.gain_coins(2)
        self.game.game_state.update_player_coins(player.name, player.coins)  # Update GameState
        self.game.game_state.log_action(player.name, 'foreign_aid', 'success')
        return True, 'success'

    def coup(self, player, target=None):
        self.game.logger.log(f"{player.name} attempts Coup action.")
        if player.coins < 7:
            self.game.logger.log(f"{player.name} does not have enough coins to perform a Coup.")
            self.game.game_state.log_action(player.name, 'coup', 'insufficient_coins')
            return False, 'insufficient_coins'

        if target is None:
            self.game.logger.log("No target specified for Coup.")
            self.game.game_state.log_action(player.name, 'coup', 'no_target')
            return False, 'no_target'

        player.lose_coins(7)
        self.game.game_state.update_player_coins(player.name, player.coins)  # Update GameState

        target.lose_influence()
        self.game.game_state.update_player_cards(target.name, target.cards)  # Update GameState
        self.game.game_state.log_action(player.name, 'coup', 'success')
        return True, 'success'
    
    def tax(self, player):
        self.game.logger.log(f"{player.name} attempts Tax action.")
        if self.game.challenge_handler.resolve_challenge(player, 'tax'):
            self.game.game_state.log_action(player.name, 'tax', 'challenge_failed')
            return (False, 'challenge_failed')

        player.gain_coins(3)
        self.game.game_state.update_player_coins(player.name, player.coins)  # Update GameState
        self.game.game_state.log_action(player.name, 'tax', 'success')
        return True

    def assassinate(self, player, target=None):
        self.game.logger.log(f"{player.name} attempts Assassinate action.")
        if player.coins < 3:
            self.game.logger.log(f"{player.name} does not have enough coins to perform an Assassination.")
            self.game.game_state.log_action(player.name, 'assassinate', 'insufficient_coins')
            return False, 'insufficient_coins'

        if target is None:
            self.game.logger.log("No target specified for Assassinate.")
            self.game.game_state.log_action(player.name, 'assassinate', 'no_target')
            return False, 'no_target'

        player.lose_coins(3)
        self.game.game_state.update_player_coins(player.name, player.coins)  # Update GameState

        # Pass the target player object instead of just the name
        if not self.game.challenge_handler.resolve_block(player, target, 'assassinate'):
            target.lose_influence()
            self.game.game_state.log_action(player.name, 'assassinate', 'success')
            self.game.game_state.update_player_cards(target.name, target.cards)  # Update GameState
            return True, 'success'
        else:
            self.game.game_state.log_action(player.name, 'assassinate', 'blocked')
            return False, 'blocked'

    def steal(self, player, target=None):
        self.game.logger.log(f"{player.name} attempts Steal action.")

        if target is None:
            self.game.logger.log("No target specified for Steal.")
            self.game.game_state.log_action(player.name, 'steal', 'no_target')
            return False, 'no_target'

        for potential_blocker in self.game.players:
            if potential_blocker != player and potential_blocker.wants_to_block(player, 'steal'):
                if self.game.challenge_handler.resolve_block(player, potential_blocker, 'steal'):
                    self.game.game_state.log_action(player.name, 'steal', 'blocked')
                    return False, 'blocked'

        stolen_amount = min(target.coins, 2)
        player.gain_coins(stolen_amount)
        target.lose_coins(stolen_amount)
        self.game.game_state.update_player_coins(player.name, player.coins)
        self.game.game_state.update_player_coins(target.name, target.coins)
        self.game.game_state.log_action(player.name, 'steal', 'success')
        return True, 'success'

    def exchange(self, player):
        self.game.logger.log(f"{player.name} attempts Exchange action.")
        if self.game.challenge_handler.resolve_challenge(player, 'exchange'):
            self.game.game_state.log_action(player.name, 'exchange', 'challenge_failed')
            return False, 'challenge_failed'

        num_cards_to_exchange = min(len(player.cards), 2)  # Number of cards to exchange
        chosen_cards = player.choose_exchange_cards(num_cards_to_exchange)

        for card in chosen_cards:
            player.cards.remove(card)
            self.game.deck.append(card)

        player.cards.extend([self.game.deck.pop() for _ in range(num_cards_to_exchange)])
        random.shuffle(self.game.deck)  # Shuffle the deck after the exchange

        self.game.game_state.update_player_cards(player.name, player.cards)  # Update GameState
        self.game.game_state.log_action(player.name, 'exchange', 'success')
        return True  # Successful exchange




class ChallengeHandler:
    def __init__(self, game):
        self.game = game

    def resolve_block(self, acting_player, blocking_player, action):
        self.game.logger.log(f"{acting_player.name} is facing a block attempt by {blocking_player.name} on {action}.")

        challenge_decision = acting_player.wants_to_challenge(blocking_player, 'block')
        if challenge_decision:
            self.game.logger.log(f"{acting_player.name} challenges {blocking_player.name}'s block!")
            challenge_result = self.challenge_action(blocking_player, acting_player, 'block')
            self.game.game_state.log_block(blocking_player.name, acting_player.name, action, 'challenged', challenge_result)
            return challenge_result

        # Assuming block success if not challenged
        block_success = True
        self.game.game_state.log_block(blocking_player.name, acting_player.name, action, 'unchallenged', block_success)
        return block_success  # Block is successful if not challenged

    def resolve_challenge(self, acting_player, action):
        self.game.logger.log(f"Resolving challenges against {acting_player.name}'s action: {action}")
        for player in self.game.players:
            if player != acting_player:
                if player.wants_to_challenge(acting_player, action):
                    self.game.logger.log(f"{player.name} challenges {acting_player.name}'s {action}!")
                    challenge_result = self.challenge_action(acting_player, player, action)
                    if challenge_result is None:
                        self.game.logger.log("Error resolving challenge. Continuing without resolution.")
                        self.game.game_state.log_challenge(player.name, acting_player.name, action, 'error', None)
                        return False
                    self.game.game_state.log_challenge(player.name, acting_player.name, action, 'completed', challenge_result)
                    return challenge_result
        return False  # No challenge occurred

    def challenge_action(self, acting_player, challenging_player, action):
        self.game.logger.log(f"{acting_player.name} is being challenged by {challenging_player.name} on {action}.")
        is_bluffing = not acting_player.verify_card(action)

        if is_bluffing:
            self.game.logger.log(f"{acting_player.name} was bluffing during {action}!")
            acting_player.lose_influence()
            self.game.game_state.log_challenge(challenging_player.name, acting_player.name, action, 'bluff', True)
            self.game.game_state.log_influence_change(acting_player.name, -1)
            return True
        else:
            self.game.logger.log(f"{acting_player.name} was not bluffing during {action}!")
            challenging_player.lose_influence()
            self.game.game_state.log_challenge(challenging_player.name, acting_player.name, action, 'truth', False)
            self.game.game_state.log_influence_change(challenging_player.name, -1)
            # Shuffle and draw a new card for the acting player, if they have less than 2 cards
            if len(acting_player.cards) < 2:
                acting_player.shuffle_in_card(action, self.game.deck)
                acting_player.draw_card(self.game.deck)
            return False


class CardManager:
    @staticmethod
    def initialize_deck():
        characters = ['Duke', 'Assassin', 'Captain', 'Ambassador', 'Contessa']
        deck = characters * 3
        random.shuffle(deck)
        return deck

    @staticmethod
    def distribute_cards(players, deck, logger, game_state):
        for player in players:
            player.cards = [deck.pop() for _ in range(2)]
            print(f"{player.name} received initial cards: {', '.join(player.cards)}")
            logger.log(f"{player.name} received their initial cards.")
            # Update GameState with the number of cards without revealing them
            game_state.update_player_cards(player.name, len(player.cards))

