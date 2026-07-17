"""Blackjack with card-style graphics."""

import time
import random

SUITS = ['H', 'D', 'C', 'S']
SUIT_SYM = {'H': '\x03', 'D': '\x04', 'C': '\x05', 'S': '\x06'}
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
VALUES = {'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
          '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10}
RED = 0xF800
BLACK = 0x0000
CARD_W, CARD_H = 36, 50

def _hand_val(hand):
    val = sum(VALUES[r] for r, _ in hand)
    aces = sum(1 for r, _ in hand if r == 'A')
    while val > 21 and aces > 0:
        val -= 10; aces -= 1
    return val

def _draw_card(tft, x, y, rank, suit, face_down=False):
    """Draw a playing card at (x, y)."""
    is_red = suit in ('H', 'D')
    fg = RED if is_red else BLACK
    if face_down:
        tft.fill_rect(x, y, CARD_W, CARD_H, 0x001F)
        tft.rect(x, y, CARD_W, CARD_H, 0xFFFF)
        # Cross-hatch pattern
        for i in range(0, CARD_W, 6):
            tft.line(x + i, y, x + i + CARD_H, y + CARD_H, 0x4208)
        return
    tft.fill_rect(x, y, CARD_W, CARD_H, 0xFFFF)
    tft.rect(x, y, CARD_W, CARD_H, 0x0000)
    # Rank
    tft.text8(rank, x + 2, y + 2, fg, 0xFFFF)
    # Suit symbol area (center)
    if len(rank) <= 1:
        tft.text8(SUIT_SYM[suit], x + 12, y + 18, fg, 0xFFFF)
    else:
        tft.text8(SUIT_SYM[suit], x + 14, y + 18, fg, 0xFFFF)

def _new_deck():
    deck = [(r, s) for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck

def blackjack_loop(tft, read_key):
    from lib.highscores import get as _hs_get, set as _hs_set
    wins = _hs_get('BLACKJACK_WINS'); losses = 0; ties = 0
    deck = _new_deck()
    phase = 'bet'
    player = []; dealer = []
    sel = 0

    def _render():
        tft.fill(0x0000)
        # Header
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('BLACKJACK', 180, 4, 0x07FF, 0x1082)
        tft.text15(f'W:{wins} L:{losses} T:{ties}', 370, 4, 0xFFE0, 0x1082)

        # Dealer area
        tft.text8('DEALER', 10, 32, 0x8410)
        if phase == 'bet':
            _draw_card(tft, 10, 46, '?', 'S', face_down=True)
        elif phase == 'player':
            _draw_card(tft, 10, 46, dealer[0][0], dealer[0][1])
            _draw_card(tft, 52, 46, '?', 'S', face_down=True)
        else:
            for i, (r, s) in enumerate(dealer):
                _draw_card(tft, 10 + i * 42, 46, r, s)
            dv = _hand_val(dealer)
            tft.text8(f'={dv}', 10 + len(dealer) * 42 + 4, 60,
                      RED if dv > 21 else 0xFFFF)

        # Player area
        tft.text8('PLAYER', 10, 110, 0x07E0)
        for i, (r, s) in enumerate(player):
            _draw_card(tft, 10 + i * 42, 124, r, s)
        pv = _hand_val(player)
        tft.text8(f'={pv}', 10 + len(player) * 42 + 4, 138,
                  RED if pv > 21 else 0x07E0)

        # Actions
        y = 190
        if phase == 'bet':
            tft.text15('Press Enter to deal', 140, y, 0x8410, 0x0000)
        elif phase == 'player':
            acts = ['HIT', 'STAND']
            if len(player) == 2:
                acts.append('DOUBLE')
            for i, a in enumerate(acts):
                bg = 0x07FF if i == sel else 0x4208
                tft.fill_rect(10 + i * 150, y, 130, 20, bg)
                tft.text15(a, 35 + i * 150, y + 2, 0xFFFF, bg)
            tft.text8('L/R select  Enter confirm', 10, y + 26, 0x8410)
        elif phase == 'result':
            tft.text15('Enter: next  Q: quit', 140, y, 0x8410, 0x0000)

    def _new_hand():
        nonlocal player, dealer, phase, sel
        if len(deck) < 20:
            deck.extend(_new_deck())
        player = [deck.pop(), deck.pop()]
        dealer = [deck.pop(), deck.pop()]
        phase = 'player'; sel = 0
        if _hand_val(player) == 21:
            phase = 'dealer'

    def _dealer_play():
        nonlocal phase
        while _hand_val(dealer) < 17:
            dealer.append(deck.pop())
        phase = 'result'

    _render()

    while True:
        ch = read_key()
        if ch is None:
            continue
        if ch in ('q', 'Q', chr(24)):
            return
        if phase == 'bet':
            if ch == chr(10):
                _new_hand(); _render()
        elif phase == 'player':
            n = 3 if len(player) == 2 else 2
            if ch in ('\x85', chr(27)):
                sel = (sel - 1) % n; _render()
            elif ch in ('\x84', chr(9)):
                sel = (sel + 1) % n; _render()
            elif ch == chr(10):
                if sel == 0:
                    player.append(deck.pop())
                    if _hand_val(player) > 21:
                        phase = 'result'; losses += 1
                    elif _hand_val(player) == 21:
                        phase = 'dealer'
                elif sel == 1:
                    phase = 'dealer'
                elif sel == 2:
                    player.append(deck.pop())
                    if _hand_val(player) > 21:
                        phase = 'result'; losses += 1
                    else:
                        phase = 'dealer'
                if phase == 'dealer':
                    _dealer_play()
                    pv = _hand_val(player); dv = _hand_val(dealer)
                    if dv > 21 or pv > dv:
                        wins += 1
                        _hs_set('BLACKJACK_WINS', wins)
                    elif pv == dv:
                        ties += 1
                    else:
                        losses += 1
                _render()
        elif phase == 'result':
            if ch == chr(10):
                phase = 'bet'; _render()
