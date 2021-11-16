# Hamza Dugmag
# game.py
#

from button import *
from users import *
import dashboard
import init
import random


class Game:

    def __init__(self, username, players):
        # players
        self.username = username
        self.players = players

        # player decks
        self.decks = []

        # discard pile generated after dealt cards
        self.drawPile = self.deal()

        # discard pile
        self.discard = []

        # card drew
        self.chosen = 0

        # action available
        self.action = 'Draw: '

    def deal(self):
        # number of cards based on number of players
        cardNums = [25, 40, 50, 60]

        # generate and shuffle cards
        cards = list(range(1, cardNums[self.players] + 1))
        random.shuffle(cards)

        # initialize decks
        for player in range(self.players + 1):
            self.decks.append([])

        # distribute cards
        for deck in self.decks:
            for card in range(10):
                deck.append(cards.pop())

        return cards

    def getPoints(self):
        # reset points
        points = 0

        # add points if card greater than previous
        prev = 0
        for i in self.decks[0]:
            if i > prev:
                points += 5
                prev = i
            else:
                break

        # return points
        return points

    def draw(self, player):
        # user title
        title = self.username if player == 0 else 'Guest'
        drawTitle('Player ' + str(player + 1) + ' | ' + title)

        # card button dim
        y = 320
        w = h = 50
        buttons = []

        # card color variable initialization
        prevCard = 0
        checkCol = True

        for i in range(10):
            # get card in deck
            card = self.decks[player][i]

            # card color
            if card > prevCard and checkCol:
                col = GREEN
                prevCard = card

            else:
                col = RED
                checkCol = False

            # append button
            buttons.append(Button((i * (w + 10) + 205, y, w, h), str(card), col))

        # action button dim
        py = y + 1.4 * h
        pw = 290
        ph = 60

        # draw pile
        if self.chosen:
            drawElem = self.chosen
        else:
            drawElem = ''

        buttons.append(Button((205, py, pw, ph), self.action + str(drawElem), L_GRAY))

        # discard pile
        try:
            discardElem = self.discard[0]
        except Exception:
            discardElem = ''

        buttons.append(Button((505, py, pw, ph), 'Discard: ' + str(discardElem), L_GRAY))

        # back button
        buttons.append(Button((205, py + ph * 1.4, 590, bh), 'Back', L_GRAY))

        # draw buttons
        for button in buttons:
            button.queue()

        # return buttons
        return buttons

    def checkWin(self, deck):
        return deck[:] == sorted(deck[:])

    def rotate(self, current):
        if current != self.players:
            current += 1
        else:
            current = 0

        return current

    def play(self):
        # input variable initialization
        global mx, my, button
        button = 0

        # current player and if someone won
        current = 0
        won = False

        # action variables
        points = 0
        drew = False
        canDiscard = True
        played = False

        # card buttons
        b = self.draw(current)

        # player 1 points
        points = self.getPoints()

        while not won:
            deck = self.decks[current]

            # user input assign
            inp = userInput(mx, my, button)
            if inp is None:
                # quit
                return
            else:
                mx, my, button = inp[:-1]

            if button:
                button = 0

                # check for empty piles and soltaire
                if len(self.drawPile) == len(self.discard) == 0 == self.players:
                    # single player ends game
                    break

                # action
                for i in range(len(b)):
                    if b[i].getButton().collidepoint(mx, my):
                        if i == 10 and not drew:
                            # check for empty draw pile
                            try:
                                self.chosen = self.drawPile.pop()
                                drew = True
                            except Exception:
                                if self.players != 0:
                                    # discard and empty draw pile switch on multiplayer
                                    self.drawPile = self.discard[:]
                                    self.discard = []
                                else:
                                    # soltaire ignores action request
                                    continue

                        elif i == 11 and canDiscard:
                            if drew:
                                # discard chosen card
                                self.discard.insert(0, self.chosen)
                                self.chosen = 0
                                played = True
                            else:

                                try:
                                    # choose card on top of discard pile
                                    self.chosen = self.discard.pop(0)
                                    drew = True
                                    canDiscard = False
                                    self.action = 'Play: '
                                except Exception:
                                    # ignore attempt to use empty discard pile
                                    pass

                        elif i == 12:
                            # quit game
                            return self.back()

                        elif 0 <= i <= 9 and drew:
                            # retrieve card about to change
                            oldCard = self.decks[current][i]

                            # switch card
                            self.decks[current][i] = self.chosen

                            # place old card in discard if more than 1 player
                            if self.players != 0:
                                self.discard.insert(0, oldCard)

                            # reset chosen
                            self.chosen = 0

                            # pronounce played
                            played = True

                        # stop checking for other collisions since collided
                        break

                points = self.getPoints()

                # check for winning state
                won = self.checkWin(deck)
                if won:
                    break

                if played:
                    # rotate players
                    current = self.rotate(current)

                    # reset action variables
                    drew = False
                    canDiscard = True
                    played = False
                    self.action = 'Draw: '

                # draw respective deck
                b = self.draw(current)

        # update statistics
        User(self.username).update(points)

        # show win screen
        init.message = 'Fatal Python error: Cannot recover from stack overflow. %s scored %i points.' % (self.username, points)
        self.draw(current)

        # user input assign until back / quit
        while True:
            inp = userInput(mx, my, button)
            if inp is None:
                # quit
                return
            else:
                mx, my, button = inp[:-1]

            if b[12].getButton().collidepoint(mx, my):
                # reset message and quit
                init.message = ''
                return self.back()

    def back(self):
        return dashboard.Dash(self.username).main()
