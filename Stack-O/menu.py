# Hamza Dugmag
# menu.py
#

from button import *
from users import *


'''
menu draws
'''


def drawSplash():
    # title
    drawTitle('Stack - O')

    # buttons
    buttons = [Button((bx, by, bw, bh), 'Login', L_GRAY),
               Button((bx, by + pad, bw, bh), 'Register', L_GRAY),
               Button((bx, by + pad * 2, bw, bh), 'Quit', RED)]

    # draw and return each button
    for button in buttons:
        button.queue()

    return buttons


def drawLogin(un='', pw=''):
    # title
    drawTitle('Login')

    # buttons
    buttons = [Button((bx, by, bw, bh), un, L_GRAY),
               Button((bx, by + pad, bw, bh), pw, L_GRAY),
               Button((bx, by + pad * 2, bw, bh), 'Enter', ORANGE),
               Button((bx, by + pad * 3, bw, bh), 'Back', L_GRAY)]

    # draw and return each button
    for button in buttons:
        button.queue()

    return buttons


def drawRegister(un='', pw=''):
    # title
    drawTitle('Register')

    # buttons
    buttons = [Button((bx, by, bw, bh), un, L_GRAY),
               Button((bx, by + pad, bw, bh), pw, L_GRAY),
               Button((bx, by + pad * 2, bw, bh), 'Create Account', ORANGE),
               Button((bx, by + pad * 3, bw, bh), 'Back', L_GRAY)]

    # draw and return each button
    for button in buttons:
        button.queue()

    return buttons


'''
main
'''


def main():
    global mx, my, button, k

    # variable initialization
    b = drawSplash()
    menu = 0

    username = password = passAsteriks = ''
    typing = False
    passing = False

    while True:

        # user input assign
        inp = userInput(mx, my, button, k)
        if inp is None:
            # quit
            return

        else:
            mx, my, button, k = inp
            k = '' if not(typing or passing) else k

        # user input evaluation
        if button:
            button = 0

            # action
            for i in range(len(b)):

                if b[i].getButton().collidepoint(mx, my):

                    if menu == 0:
                        # change menu screen and reset variables on main menu
                        menu = i + 1
                        username = password = passAsteriks = ''
                        init.message = ''

                    # entered username and password
                    if i == 2:
                        if menu == 1:
                            # login
                            if User(username, password).login():
                                return username

                        elif menu == 2:
                            # register
                            User(username, password).register()

                    # reset typing states
                    typing = passing = False

                    # back to menu
                    menu = 0 if i == 3 else menu
                    init.message = '' if i == 3 else init.message

                    # stop checking for other buttons' collision if any button pressed
                    break

            # menu draw
            if menu == 0:
                b = drawSplash()

            elif menu == 1 or menu == 2:
                # assign typing state for username or password
                typing = True if i == 0 else False
                passing = True if i == 1 else False

                # draw
                if menu == 1:
                    b = drawLogin(username, passAsteriks)
                else:
                    b = drawRegister(username, passAsteriks)

            elif menu == 3:
                # quit
                return

        # typing
        if (typing or passing) and k != '':

            # backspace
            if ord(k) == 8:
                if typing:
                    username = username[:-1]
                else:
                    password = password[:-1]

            # other characters
            else:
                if typing:
                    username += k if len(username) < maxTextLen else ''
                else:
                    password += k if len(password) < maxTextLen * 1.5 else ''

            # draw menu with new username and password
            passAsteriks = len(password) * '*'
            if menu == 1:
                b = drawLogin(username, passAsteriks)

            elif menu == 2:
                b = drawRegister(username, passAsteriks)

            # reset key
            k = ''

        # final flip
        display.flip()
