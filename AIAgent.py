from GameState import GameState
from Player import Player
from openai import OpenAI
import random

from dotenv import load_dotenv
import os

load_dotenv()  # This loads the variables from the .env file into the environment

# Creates access for the API key with os.getenv
openai_api_key = os.getenv('OPENAI_API_KEY')

class AIAgent(Player):

    valid_actions = {'income', 'foreign_aid', 'coup', 'tax', 'assassinate', 'steal', 'exchange'}

    def __init__(self, name, character, game):
        super().__init__(name, character)  # Pass both name and character to the superclass
        self.game = game
        self.api_key = openai_api_key  # Make sure openai_api_key is defined or imported
        self.last_failed_action = None
        self.game = game #store the game reference

    def make_decision(self, game_state, decision_type, additional_info=None):
        readable_game_state = self.format_game_state(game_state)
        print("Debug: GameState information fed to AI:")
        print(game_state)
        prompt = self.create_prompt(game_state, decision_type, additional_info)
        response = self.query_gpt(prompt)
        decision = self.parse_response(decision_type, response)

        if decision_type == 'action_decision' and decision == self.last_failed_action:
            decision = self.get_alternative_action()

        return decision
    
    def format_game_state(self, game_state):
        print("Debug: Formatting game state")  # Debug statement
        print("Debug: game_state['players_state']:", game_state['players_state'])  # Print players_state

        formatted_state = {
            'deck_size': game_state['deck_size'],
            'players': {}
        }

        for player_name, player_info in game_state['players_state'].items():
            print(f"Debug: player_info for {player_name}:", player_info)  # Debug for each player's info

            card_count = len(player_info['cards']) if 'cards' in player_info and isinstance(player_info['cards'], list) else 0

            formatted_state['players'][player_name] = {
                'coins': player_info['coins'],
                'card_count': card_count,
                'influence': player_info['influence']
            }

        formatted_state['recent_actions'] = game_state['actions_log'][-5:]  # Last 5 actions
        return formatted_state

    def get_alternative_action(self):
        valid_actions = {'coup', 'tax', 'income', 'foreign_aid', 'assassinate', 'steal', 'exchange'}
        if self.last_failed_action in valid_actions:
            valid_actions.remove(self.last_failed_action)
        return random.choice(list(valid_actions))

    def create_prompt(self, game_state, decision_type, additional_info=None):
        prompt = f"""Game state: {game_state} /n Decision type: {decision_type} /n Additional info: {additional_info} /n

        Please provide a clear and precise action choice, considering the intricate dynamics of Coup. 
        Start the sentence with "The best action is to [insert action]"

        As an AI expert in Coup, your goal is to strategically outmaneuver (read: crush) your opponents. Consider the following:
        - Your current cards and their abilities.
        - The coins you have and the actions they enable.
        - Your opponents' potential cards based on their actions and your deductions.
        - The risk associated with each potential action, considering possible challenges and counteractions from opponents.
        - The actions that have been most recently played and how they might influence opponents' strategies.

        Based on the current game state and these considerations, what is the best course of action to take? 
        This action should maximize your chances of winning, using a combination of strategy, bluffing, and tactical responses to opponents' moves.
        Only consider actions at first (tax, coup, assassinate, etc), and only consider reactions (challenges, blocks, etc) when prompted.

        
    """
        return prompt

    def query_gpt(self, prompt):
        client = OpenAI(api_key=self.api_key)
        response = client.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=2500
        )
        return response.choices[0].text

    def parse_response(self, decision_type, response):
        if decision_type == 'action_decision':
            return self.extract_action_from_response(response)
        elif decision_type == 'challenge_decision':
            return 'challenge' if 'challenge' in response.lower() else 'no_challenge'
        elif decision_type == 'block_decision':
            return 'block' if 'block' in response.lower() else 'no_block'
        elif decision_type == 'reaction_decision':
            return self.extract_reaction_decision(response)
        elif decision_type == 'bluff_decision':
            return 'bluff' if 'bluff' in response.lower() else 'no_bluff'
        else:
            return None

    def extract_action_from_response(self, response):
        valid_actions = {'coup', 'tax', 'income', 'foreign_aid', 'assassinate', 'steal', 'exchange'}
        words = response.split()
        for i, word in enumerate(words):
            if word.lower() in valid_actions:
                return word.lower()
            elif i + 1 < len(words):
                two_word_action = f"{word.lower()} {words[i + 1].lower()}"
                if two_word_action in valid_actions:
                    return two_word_action
        return random.choice(list(valid_actions))  # Fallback to a random valid action

    def extract_reaction_decision(self, response):
        valid_reactions = {'challenge', 'block', 'no_challenge', 'no_block'}
        for word in response.split():
            if word.lower() in valid_reactions:
                return word.lower()
        return random.choice(list(valid_reactions))  # Fallback to a random valid reaction
    
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
                    if challenge_result is None:
                        print("Challenge resolution error: No clear outcome")
                    return challenge_result
        return False  # No challenge occurred
    
    def determine_valid_actions(self, game_state):
        """
        Determines which actions are valid based on the current game state.
        """
        valid_actions = set(self.valid_actions)
        coins = game_state['players_state'][self.name]['coins']

        # Remove actions that require more coins than the AI currently has
        if coins < 7:
            valid_actions.discard('coup')  # Remove 'coup' if insufficient coins
        if coins < 3:
            valid_actions.discard('assassinate')  # Remove 'assassinate' if insufficient coins

        return valid_actions

    def choose_action(self, game_state):

        if isinstance(game_state, GameState):
            readable_game_state = game_state.get_public_game_state()
        else:
            readable_game_state = game_state  # assuming it's already a dictionary

        action = self.make_decision(readable_game_state, "action_decision")
        print(f"AI initially chose action: {action}")  # Debug print

        # Check if the action is valid
        if action not in self.valid_actions:
            print(f"Action {action} is invalid, choosing an alternative action.")  # Debug print
            self.last_failed_action = action
            action = self.get_alternative_action()
        print(f"AI final action choice: {action}")  # Debug print
        return action

    def choose_target(self, game):
        """AI logic to choose a target."""
        valid_targets = self.get_available_targets(game)

        # AI decision-making logic to select a target from valid_targets
        # A target is randomly selected because of the fact that there is only 1 target
        selected_target = random.choice(valid_targets) if valid_targets else None

        return selected_target

    def wants_to_challenge(self, acting_player, action):
        """ Determines if the AI wants to challenge an action. """
        game_state = self.game.game_state.get_public_game_state()
        decision = self.make_decision(game_state, 'challenge_decision', {"acting_player": acting_player, "action": action})
        print(f"AI decision to challenge {acting_player.name}'s {action}: {decision}")
        return decision == 'challenge'

    def wants_to_block(self, acting_player, action):
        """ Determines if the AI wants to block an action. """
        game_state = self.game.game_state.get_public_game_state()
        decision = self.make_decision(game_state, "block_decision", {"action": action})
        return decision == 'block'

    def choose_exchange_cards(self, num_cards_to_exchange):
        """
        AI logic to choose cards to exchange. This example randomly selects cards.
        """
        if not self.cards or num_cards_to_exchange <= 0:
            return []
        
        # Randomly choose cards to exchange, this could be done better using AI logic
        return random.sample(self.cards, min(num_cards_to_exchange, len(self.cards)))
    def has_influence(self):
        """Check if the AI agent still has influence (cards) in the game."""
        return len(self.cards) > 0
    
    def make_move(self, game_state):
        # Generate a prompt for the AI to decide on an action and a message
        communication_prompt = self.game.communication_layer.create_message_prompt(
            game_state, decision_type='action_decision', additional_info=None)

        # Query the AI model using the generated prompt
        response = self.query_gpt(communication_prompt)

        if ';' in response:
            action, message = response.split(';', 1)  # Split only on the first semicolon
            return action.strip(), message.strip()
        else:
            # Handle the case where the response format is not as expected
            print("Unexpected response format from AI. Response:", response)
            # Fallback to a random valid action and a default message
            random_action = random.choice(list(self.valid_actions))
            default_message = 'No comment'
            return random_action, default_message
    
    def interact_with_communication_layer(self, communication_layer, game_state):
        """AI agent's interaction with the CommunicationLayer for messaging."""
        # AI generates and sends a message
        message = self.send_message(game_state)
        communication_layer.send_message(self, message)

        # AI reacts to a received message (this part remains as is)
        action = None 
        response = self.react_to_move(action, message, game_state)

    def send_message(self, game_state):
        # Use the existing method from CommunicationLayer to create a prompt for the message
        message_prompt = self.game.communication_layer.create_message_prompt(
            game_state, decision_type='message_decision', additional_info=None)

        # Query the AI model using the generated prompt
        message = self.query_gpt(message_prompt).strip()
        return message
    
    def react_to_move(self, action, message, game_state):
        # Generate a prompt for the AI to decide on a response
        reaction_prompt = self.game.communication_layer.create_message_prompt(
            game_state, decision_type='reaction_decision', additional_info={'action': action, 'message': message})

        # Query the AI model using the generated prompt
        response = self.query_gpt(reaction_prompt).strip()

        return response


