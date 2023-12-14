import unittest
from Player import Player  # Import the relevant classes

class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player = Player("TestPlayer", None)  # Initialize a player for testing

    def test_gain_coins(self):
        self.player.gain_coins(3)
        self.assertEqual(self.player.coins, 5)  # Starting with 2 coins, now should have 5

    def test_lose_coins(self):
        self.player.lose_coins(1)
        self.assertEqual(self.player.coins, 1)  # Starting with 2 coins, now should have 1

    def test_coins_never_negative(self):
        self.player.lose_coins(3)
        self.assertEqual(self.player.coins, 0)  # Coins should not go below 0

if __name__ == '__main__':
    unittest.main()


class TestGame(unittest.TestCase):

    def setUp(self):
        # Setup a game with players
        self.players = [Player("Player1", None), Player("Player2", None)]
        self.game = Game(self.players)

    def test_is_game_over_with_multiple_players(self):
        self.assertFalse(self.game.is_game_over())

    def test_is_game_over_with_single_player(self):
        # Simulate a situation where only one player has cards
        self.players[0].cards = []
        self.assertTrue(self.game.is_game_over())

if __name__ == '__main__':
    unittest.main()


class TestActionHandler(unittest.TestCase):

    def setUp(self):
        self.players = [Player("Player1", None), Player("Player2", None)]
        self.game = Game(self.players)
        self.action_handler = ActionHandler(self.game)

    def test_income_action(self):
        player = self.players[0]
        self.action_handler.income(player)
        self.assertEqual(player.coins, 3)  # Player should gain 1 coin (starting from 2)

if __name__ == '__main__':
    unittest.main()
