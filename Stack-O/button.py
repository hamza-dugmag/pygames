# Hamza Dugmag
# button.py
#

from init import *


class Button:

    def __init__(self, dim, text, col):
        # defaults
        self.dim = Rect(*dim)
        self.text = text
        self.col = col

        # text dim
        tSize = em.size(text)

        tw = tSize[0]
        th = tSize[1]
        tx = (dim[0] + (dim[2] // 2)) - (tw // 2)
        ty = (dim[1] + (dim[3] // 2)) - (th // 2)

        # text rect
        self.tRect = Rect(tx, ty, tw, th)

    def queue(self):
        # box
        draw.rect(SCREEN, self.col, self.dim)

        # text
        text = em.render(self.text, 1, D_GRAY)
        SCREEN.blit(text, self.tRect)

        # flip
        display.flip()

    def getButton(self):
        # return button dimension
        return self.dim
