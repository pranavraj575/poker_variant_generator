class AbsDeck:
    def __init__(self, count=13, suits=4, wild=0):
        self.count = count
        self.suits = suits
        self.wild = wild
        self.non_wild = self.count*self.suits
        self.total_cards = self.non_wild + self.wild

    def new_deck(self):
        return Deck(count=self.count, suits=self.suits, wild=self.wild)


class Deck(AbsDeck):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
