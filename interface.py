import random
from Character import Character, Duke, Assassin, Captain, Ambassador, Contessa
from GameManagement import Game, TurnManager, ActionHandler, ChallengeHandler, CardManager
from Player import Player
from AIAgent import AIAgent  # Import AIAgent
from GameLogger import GameLogger
from CommunicationLayer import CommunicationLayer  # Import CommunicationLayer
from GameState import GameState  # Import GameState

def main_menu():
    print("Welcome to the Game!")
    print("1: Start New Game")
    print("2: Exit")
    choice = input("Enter your choice: ")
    return choice

def create_game():
    num_human_players = int(input("Enter the number of human players (0 or 1): "))

    # Initialize the game with an empty players list
    game = Game([])

    players = []
    if num_human_players == 1:
        human_name = input("Enter your name: ")
        human_character = choose_character()  # Assume this returns a Character object
        human_player = Player(human_name, human_character)
        players.append(human_player)

        ai_name = "AI_Opponent"
        ai_character = choose_character()  # Assume this returns a Character object
        ai_player = AIAgent(ai_name, ai_character, game)  # Pass the game reference here
        players.append(ai_player)
    elif num_human_players == 0:
        for i in range(2):  # Creating two AI players
            ai_name = f"AI_Opponent_{i+1}"
            ai_character = choose_character()  # Assume this returns a Character object
            ai_player = AIAgent(ai_name, ai_character, game)  # Pass the game reference here
            players.append(ai_player)

    # Now set the players in the game
    game.players = players

    game.initialize_communication_layer()  # Initialize the communication layer after players are set
    return game

def choose_character():
    characters = ['Duke', 'Assassin', 'Captain', 'Ambassador', 'Contessa']
    return Character(random.choice(characters), 'color')

def play_game(game):
    game.start_game()

    while not game.is_game_over():
        for player in game.players:
            if player.has_cards():
                action = player.choose_action(game.game_state)

                # Determine the target player for actions that need one
                target_player = None
                if action in ['coup', 'assassinate', 'steal']:
                    target_player = choose_target(game, player) 

                # Check if the action can be blocked and if the target is an AIAgent
                if action_can_be_blocked(action) and isinstance(target_player, AIAgent):
                    game_state = game.game_state.get_public_game_state()
                    if target_player.wants_to_block(action, game_state):
                        print(f"{target_player.name} decides to block the {action} action.")
                        continue  # Skip the action handling if blocked

                handle_action(action, player, game, target_player)

                if game.is_game_over():
                    break

            game.turn_manager.next_turn()

    game.announce_winner()

def action_can_be_blocked(action):
    blockable_actions = {'foreign_aid', 'steal', 'assassinate'}
    return action in blockable_actions

def player_action(player, game):
    print(f"\n{player.name}'s turn. Coins: {player.coins}, Cards: {', '.join(player.cards)}")
    print("Choose an action:")
    actions = ["income", "foreign_aid", "coup", "tax", "assassinate", "steal", "exchange"]
    for i, action in enumerate(actions):
        print(f"{i + 1}: {action}")

    while True:
        choice = input("Enter your action: ")
        if choice.isdigit() and 1 <= int(choice) <= len(actions):
            return actions[int(choice) - 1]
        else:
            print("Invalid action. Please try again.")


def ai_action(ai_player, game, game_state):
    action = ai_player.choose_action(game_state)
    print(f"{ai_player.name} (AI) chooses {action}")
    handle_action(action, ai_player, game)


def handle_action(action, player, game, target_player=None):
    print(f"Handling action: {action} for player: {player.name}")
    
    if action == "income":
        game.action_handler.income(player)
    elif action == "foreign_aid":
        game.action_handler.foreign_aid(player)
    elif action == "coup":
        if target_player:
            game.action_handler.coup(player, target_player)
    elif action == "tax":
        game.action_handler.tax(player)
    elif action == "assassinate":
        if target_player:
            game.action_handler.assassinate(player, target_player)
    elif action == "steal":
        if target_player:
            game.action_handler.steal(player, target_player)
    elif action == "exchange":
        game.action_handler.exchange(player)
    else:
        print(f"Received an unknown action: {action}")
        print("Invalid action. Please try again.")

def choose_target(game, acting_player):
    # Check if the acting player is an AIAgent
    if isinstance(acting_player, AIAgent):
        # Use AIAgent's own method to choose a target
        return acting_player.choose_target(game)
    else:
        # For human players, use the Game class's method to choose a target
        return game.choose_target(acting_player)

if __name__ == '__main__':
    while True:
        choice = main_menu()
        if choice == '1':
            game = create_game()  # Now it returns both players and the game
            play_game(game)  # Pass both players and the game object
        elif choice == '2':
            break
        else:
            print("Invalid choice. Please try again.")

