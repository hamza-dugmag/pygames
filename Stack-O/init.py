# Hamza Dugmag
# init.py
#

from pygame import *
init()

# display
SIZE = (WIDTH, HEIGHT) = (1000, 700)
SCREEN = display.set_mode(SIZE)

# input
mx = my = button = 0
k = ''

# colors
BLACK = (0, 0, 0)
D_GRAY = (20, 20, 20)
L_GRAY = (220, 220, 220)

RED = (255, 100, 90)
ORANGE = (255, 140, 60)
GREEN = (105, 255, 35)

# font and text
em = font.SysFont('Calbri', 22)
em_5 = font.SysFont('Calbri', 14)
em2 = font.SysFont('Calbri', 32, False, True)

maxTextLen = 18
minTextLen = 4

message = ''

# button dim
bw = 250
bh = 30
bx = (WIDTH // 2) - (bw // 2)
pad = bh + (bh // 2)
by = (HEIGHT // 2) - ((bh + pad) // 2)


def genText(s, font, ty, col=L_GRAY):
    # title dim
    size = font.size(s)
    text = font.render(s, 1, col)

    tw = size[0]
    th = size[1]
    tx = (WIDTH // 2) - (tw // 2)

    # draw title
    tRect = Rect(tx, ty, tw, th)
    SCREEN.blit(text, tRect)


def drawTitle(title):
    # window caption
    display.set_caption(title)

    # background
    draw.rect(SCREEN, D_GRAY, (0, 0, WIDTH, HEIGHT))

    # texts
    genText(title, em2, 250)
    genText(message, em_5, 290, RED)
    genText('Developed by Hamza Dugmag', em_5, 650)

    # flip
    display.flip()


def userInput(mx, my, button, k=''):

    for ev in event.get():

        # quit
        if ev.type == QUIT:
            return None

        # mouse
        elif ev.type == MOUSEBUTTONDOWN:

            if ev.button == 1:
                mx, my = ev.pos
                button = 1

            else:
                button = 0

        # keyboard
        elif ev.type == KEYDOWN:

            if 97 <= ev.key <= 122 or ev.key in [8, 32] or 48 <= ev.key <= 57:
                k = chr(ev.key)

    return (mx, my, button, k)
