from GameLogger import GameLogger


class Character:
    def __init__(self, name, color):
        self.name = name
        self.color = color

    def action(self, acting_player, game, target_player=None):
        pass

    def counteraction(self, acting_player, game):
        pass

class Duke(Character):
    def __init__(self):
        super().__init__('Duke', 'purple')

    def action(self, acting_player, game, target_player=None):
        game.execute_action('tax', acting_player)

    def counteraction(self, acting_player, game):
        game.execute_counteraction('block_foreign_aid', acting_player, self)

class Assassin(Character):
    def __init__(self):
        super().__init__('Assassin', 'black')

    def action(self, acting_player, game, target_player):
        game.execute_action('assassinate', acting_player, target_player)

    def counteraction(self, acting_player, game):
        pass  # Assassin has no counteraction

class Captain(Character):
    def __init__(self):
        super().__init__('Captain', 'blue')

    def action(self, acting_player, game, target_player):
        game.execute_action('steal', acting_player, target_player)

    def counteraction(self, acting_player, game):
        game.execute_counteraction('block_steal', acting_player, self)

class Ambassador(Character):
    def __init__(self):
        super().__init__('Ambassador', 'green')

    def action(self, acting_player, game, target_player=None):
        game.execute_action('exchange', acting_player)

    def counteraction(self, acting_player, game):
        game.execute_counteraction('block_steal', acting_player, self)

class Contessa(Character):
    def __init__(self):
        super().__init__('Contessa', 'red')

    def counteraction(self, acting_player, game):
        game.execute_counteraction('block_assassinate', acting_player, self)

