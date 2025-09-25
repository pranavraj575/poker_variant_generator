from deck import AbsDeck
import numpy as np


def choose(n, k):
    if k < 0 or k > n: return 0
    return np.prod(np.arange(k) + n - k + 1)/np.prod(np.arange(k) + 1)


def log_choose(n, k):
    if k < 0 or k > n: return -np.inf
    return np.sum(np.log(np.arange(k) + n - k + 1)) - np.sum(np.log(np.arange(k) + 1))


class HandType:
    """
    type of hand, used to determine probabilities of obtaining a hand (combinatorially)
    if a game includes various hand types, these can be ranked by probability of obtaining
    """
    def __init__(self, size=5):
        self.size = size

    def count(self, deck: AbsDeck):
        return np.exp(self.log_count(deck=deck))

    def log_count(self, deck: AbsDeck):
        raise NotImplementedError

    def log_probability(self, deck: AbsDeck, normalize=False):
        if normalize:
            # log(count/total number of (unordered) choices)
            # log(count)-log(deck size choose hand size)
            # log(count)-log((deck size)*(deck size - 1)*...*(deck size-hand size + 1)) + log((hand size)!)
            # log(count)-log(deck size)+log(deck size - 1)+...+log(deck size-hand size + 1) + log(hand size)+log(hand size-1) + ...
            return (self.log_count(deck=deck) -
                    np.sum(np.log(np.arange(self.size) + deck.total_cards - self.size + 1)) +
                    np.sum(np.log(np.arange(self.size) + 1)))
        else:
            return self.log_count(deck=deck)


class kOfAKindChain(HandType):
    """
    exactly k_1,k_2,... copies of a card (not at least)
    TODO: ignoring wild cards for now
    """

    def __init__(self, k_arr, size=5):
        super().__init__(size=size)
        # map of value to number of occurrences
        # i.e. in 2 pair (k_arr=[2,2]), this is {2:2}, and in royal flush, this is {3:1,2:1}
        self.counter = {val: k_arr.count(val) for val in k_arr}
        if 1 not in self.counter:
            self.counter[1] = 0
        self.counter[1] += self.size - sum(k_arr)

    def log_count(self, deck: AbsDeck):
        # choose identities of the k1,k2,... cards, and the remaining cards
        # then choose suits for all
        s = 0
        identies_chosen = 0
        for val, count in self.counter.items():
            # choose identities for these cards, then suits for each
            # (identities left Choose count)*(suits Choose val)^count
            s += log_choose(deck.count - identies_chosen, count) + count*log_choose(deck.suits, val)
            identies_chosen += count
        return s


class kOfAKind(HandType):
    """
    exactly k copies of a card (not at least k)
    other cards will be non-copies
    """

    def __init__(self, k, size=5):
        super().__init__(size=size)
        self.k = k

    def log_count(self, deck: AbsDeck):
        if self.k > deck.suits + deck.wild or self.k > self.size:
            return -np.inf
        if deck.wild > 0:
            s = 0
            # partition on number of wild cards drawn up to k
            for wilds in range(min(deck.wild, self.k)):
                # number of ways to choose wild cards * ways to choose a card to copy * number of ways to choose k-wilds suits
                kay = choose(deck.wild, wilds)*deck.count*choose(deck.suits, self.k - wilds)
                # choose remaining cards by selecting handsize-k distinct cards (avoiding flush)
                s += kay*choose(deck.count - 1, self.size - self.k)*(deck.suits**(self.size - self.k))
            if deck.wild >= self.k:
                # in this case, can potentially draw all wild cards
                s += choose(deck.wild, self.k)
            return np.log(s)
        else:
            # can do this in log space
            kay = np.log(deck.count) + log_choose(deck.suits, self.k)
            return kay + log_choose(deck.count - 1, self.size - self.k) + (self.size - self.k)*np.log(deck.suits)


class StraightFlush(HandType):
    """
    TODO: ignoring wild cards for now
    """

    def __init__(self, ace_loop=True, size=5):
        super().__init__(size=size)
        self.ace_loop = ace_loop

    def log_count(self, deck: AbsDeck):
        starting_positions = deck.count - self.size + 1 + self.ace_loop
        return np.log(starting_positions*deck.suits)


class Straight(HandType):
    """
    TODO: ignoring wild cards for now
    """

    def __init__(self, avoid_straight_flush=True, ace_loop=True, size=5):
        super().__init__(size=size)
        self.avoid_straight_flush = avoid_straight_flush
        self.ace_loop = ace_loop

    def log_count(self, deck: AbsDeck):
        starting_positions = deck.count - self.size + 1 + self.ace_loop
        if self.avoid_straight_flush:
            # each starting position has 4 straight flushes in a standard deck
            return np.log(starting_positions*(deck.suits**self.size - deck.suits))
        else:
            return np.log(starting_positions) + self.size*np.log(deck.suits)


class Flush(HandType):
    """
    TODO: ignoring wild cards for now
    """

    def __init__(self, avoid_straight_flush=True, ace_loop=True, size=5):
        super().__init__(size=size)
        self.avoid_straight_flush = avoid_straight_flush
        self.ace_loop = ace_loop

    def log_count(self, deck: AbsDeck):
        if self.avoid_straight_flush:
            starting_positions = deck.count - self.size + 1 + self.ace_loop
            # every suit has # starting positions straight flushes
            return np.log(deck.suits*(choose(deck.count, self.size) - starting_positions))
        else:
            return np.log(deck.suits) + log_choose(deck.count, self.size)


class HighCard(HandType):
    """
    log count for this will be inf, as this is the worst hand
    """

    def __init__(self, size=5):
        super().__init__(size=size)

    def log_count(self, deck: AbsDeck):
        return np.inf


if __name__ == '__main__':
    # matches https://allmathconsidered.wordpress.com/2017/05/23/the-probabilities-of-poker-hands/
    for hand in [StraightFlush(size=5),
                 kOfAKind(k=4, size=5),
                 kOfAKindChain(k_arr=[3, 2], size=5),
                 Flush(avoid_straight_flush=True, ace_loop=True, size=5),
                 Straight(avoid_straight_flush=True, ace_loop=True, size=5),
                 kOfAKind(k=3, size=5),
                 kOfAKindChain(k_arr=[2, 2], size=5),
                 kOfAKind(k=2, size=5),
                 ]:
        print(int(round(hand.count(deck=AbsDeck().new_deck()))))
