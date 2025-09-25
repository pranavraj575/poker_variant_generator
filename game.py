class Game:
    def __init__(self, cards_revealed=[0, 3, 1, 1], private_hand_size=2, eval_hand=5):
        self.cards_revealed = cards_revealed
        self.private_hand_size = private_hand_size
        self.eval_hand = eval_hand
