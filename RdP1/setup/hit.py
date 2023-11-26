import numba
from numba import types, typed, njit
from numba.experimental import jitclass
import numpy as np


@njit
def numbatst(i):
    return 2*i


@njit
def tstwrapper(i):
    return numbatst(i)


player_jitspecs = [
    ('buffer', types.DictType(types.int64, types.int64)),
    ('current_hand', types.DictType(types.int64, types.int64)),
    ('score', types.int64),
]

@jitclass(player_jitspecs)
class Player:

    def __init__(self) -> None:
        self.buffer = typed.Dict.empty(types.int64, types.int64)
        self.current_hand = typed.Dict.empty(types.int64, types.int64)
        self.score = 0
    
    def get_draw_decision(self) -> bool:
        return len(self.current_hand) < 5

    
    def get_take_decision(self, card) -> bool:
        return 10
    
    
    def hand2buffer(self):
        for i, j in self.current_hand.items():
            self.buffer[i] = j + self.buffer.get(i, 0)
        self.current_hand.clear()


player_type = Player.class_type.instance_type


hitenv_jitspecs = [
    ('list_of_lists', types.ListType(types.ListType(types.int64))),
    ('quantities', types.ListType(types.int64)),
    ('queue', types.optional(types.List(types.int64))),
    ('players', types.ListType(player_type)),
    ('remaining_cards', types.DictType(types.int64, types.int64)),
]


@jitclass(hitenv_jitspecs)
class HitEnvironment:

    def __init__(self, list_of_lists, quantities):
        # assert length list of lists == length quantities
        self.list_of_lists = list_of_lists
        self.quantities = quantities
        self.queue = None
        self.players = typed.List.empty_list(player_type)
        self.remaining_cards = typed.Dict.empty(types.int64, types.int64)

    def init_players(self, n):
        for _ in range(n):
            self.players.append(Player())

    def draw(self):
        if self.queue:
            card = self.queue.pop()
            self.remaining_cards[card] -= 1
            return card
        raise StopIteration
    
    def make_queue(self):
        for i, quantity in zip(self.list_of_lists, self.quantities):
            for n in l:
                self.remaining_cards[n] = quantity
                for _ in range(quantity):
                    self.queue.append(n)

        self.queue = [n for l, quantitiy in zip(self.list_of_lists, self.quantities) for n in l for i in range(quantitiy)]
        self.remaining_cards
    
    def shuffle_queue(self):
        a = np.arange(len(self.queue))
        np.random.shuffle(a)
        self.queue = [self.queue[i] for i in a]

    def play(self, player: Player):
        player.hand2buffer()
        num_cards = 0
        while player.get_draw_decision():
            card = self.draw()
            if (num_cards > 2) and (card in list(player.current_hand.keys())):
                player.current_hand.clear()
                break
            player.current_hand[card] = player.current_hand.get(card, 0) + 1
            for o_player in self.players:
                if card in o_player.current_hand:
                    take = player.get_take_decision(card)
                    take = min(o_player.current_hand[card], take)
                    player.current_hand[card] += take
                    o_player.current_hand[card] -= take
            num_cards += player.current_hand[card]

    def play_until_end(self):
        while True:
            for player in self.players:
                self.play(player)

    def next(self):
        for player in self.players:
            self.play(player)
        return [player.current_hand for player in self.players]


@njit
def sum_values(player):
    card = 1
    return ((sum(player.current_hand.values()) > 3) and (card in player.current_hand))


def init_iterate_hit(hitenv):
    hitenv.make_queue()
    hitenv.shuffle_queue()
    hitenv.init_players(2)

    while True:
        try:
            l = hitenv.next()
        except StopIteration:
            l = [player.buffer for player in hitenv.players]
            break
        print(len(hitenv.queue))
        for d in l:
            print(dict(d))


if __name__ == '__main__':
    list_of_lists1 = typed.List.empty_list(types.List(types.int64))
    list_of_lists = []
    print(list_of_lists)

    list_of_lists.append([1, 2, 3, 4, 5])
    list_of_lists.append([6, 7, 8, 9, 10])

    quantities = typed.List([7, 11])
    assert len(list_of_lists) == len(quantities)
    numbalol = typed.List.empty_list(types.ListType(types.int64))
    for l in list_of_lists:
        numba_l = typed.List.empty_list(types.int64)
        for i in l:
            numba_l.append(i)
        numbalol.append(numba_l)
    
    hitenv = HitEnvironment(list_of_lists=numbalol, quantities=quantities)

    init_iterate_hit(hitenv)

    print(hitenv.queue)
