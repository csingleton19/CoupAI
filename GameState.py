class GameState:
    def __init__(self):
        self.actions_log = []
        self.players_state = {}
        self.deck_size = 0
        self.winner = None

    def add_player(self, player_name):
        # Initialize state for a new player
        self.players_state[player_name] = {
            'coins': 2,  # Starting coins
            'cards': [],
            'influence': 2  # Assuming each card represents an influence
        }

    def ensure_player_initialized(self, player_name):
        if player_name not in self.players_state:
            self.players_state[player_name] = {
                "influence": 2,  # Starting influence
                "coins": 2,      # Starting coins
                "cards": []      # Starting cards
            }

    def log_action(self, player_name, action, outcome):
        self.actions_log.append({
            "player": player_name,
            "action": action,
            "outcome": outcome
        })

    def log_turn_change(self, player_name):
        self.actions_log.append({
            "turn_change_to": player_name
        })

    def set_winner(self, winner_name):
        self.winner = winner_name

    def log_challenge(self, challenger, challenged, action, result, success):
        self.actions_log.append({
            "challenger": challenger,
            "challenged": challenged,
            "action": action,
            "result": result,
            "success": success
        })

    def log_block(self, blocker, blocked, action, result, success):
        self.actions_log.append({
            "blocker": blocker,
            "blocked": blocked,
            "action": action,
            "result": result,
            "success": success
        })

    def log_influence_change(self, player_name, influence_change):
        self.ensure_player_initialized(player_name)
        self.players_state[player_name]["influence"] += influence_change

    def update_player_coins(self, player_name, coin_change):
        self.ensure_player_initialized(player_name)
        self.players_state[player_name]["coins"] += coin_change

    def update_player_cards(self, player_name, new_cards):
        # Update the cards for a player
        self.ensure_player_initialized(player_name)
        self.players_state[player_name]['cards'] = new_cards

    def update_deck_size(self, size):
        self.deck_size = size

    def get_game_state(self):
        return {
            "actions_log": self.actions_log,
            "players_state": self.players_state,
            "deck_size": self.deck_size,
            "winner": self.winner
        }
    
    def get_public_game_state(self):
        public_state = {
            "actions_log": self.actions_log[-7:],
            "players_state": {},
            "deck_size": self.deck_size,
            "winner": self.winner
        }
        for player, state in self.players_state.items():
            public_state["players_state"][player] = {
                "coins": state["coins"],
                "influence": state["influence"],
                "card_count": len(state["cards"])  # Only include card count
            }
        return public_state