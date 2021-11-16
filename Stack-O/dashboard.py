# Hamza Dugmag
# dashboard.py
#

from button import *
from users import *
from game import *
import init


class Dash:

    def __init__(self, username):
        # assign username
        self.username = username

    def logout(self):
        # return to main menu rather than quitting
        return True

    '''
    draws
    '''

    def drawMain(self):
        # title
        drawTitle('Welcome ' + self.username)

        # buttons
        buttons = [Button((bx, by, bw, bh), 'Soltaire', L_GRAY),
                   Button((bx, by + pad, bw, bh), 'Multiplayer', L_GRAY),
                   Button((bx, by + pad * 2, bw, bh), 'Leaderboard', L_GRAY),
                   Button((bx, by + pad * 3, bw, bh), 'Settings', L_GRAY),
                   Button((bx, by + pad * 4, bw, bh), 'Log Out', RED)]

        # draw and render
        for button in buttons:
            button.queue()

        # return buttons for input checking
        return buttons

    def drawLocal(self):
        # title
        drawTitle('Multiplayer')

        # buttons
        buttons = [Button((bx, by, bw, bh), '2 Players', L_GRAY),
                   Button((bx, by + pad, bw, bh), '3 Players', L_GRAY),
                   Button((bx, by + pad * 2, bw, bh), '4 Players', L_GRAY),
                   Button((bx, by + pad * 3, bw, bh), 'Back', RED)]

        # draw and render
        for button in buttons:
            button.queue()

        # return buttons for input checking
        return buttons

    def drawLeader(self):
        # title
        drawTitle('Leaderboard')

        # scores
        leader = User().getLeaderboard()[::-1]

        for i in range(len(leader)):
            # construct text
            user = leader[i][1]
            score = str(leader[i][0])
            score = '0.0' if score == '0' else score
            text = user + ': ' + score

            # show score in leaderboard
            Button((bx, by + pad * i, bw, bh), text, L_GRAY).queue()

        # back button
        back = Button((bx, by + pad * 5, bw, bh), 'Back', RED)
        back.queue()

        # return back button
        return [back]

    def drawSettings(self):
        # title
        drawTitle('Settings')

        # buttons
        buttons = [Button((0, 0, 0, 0), '', L_GRAY),
                   Button((bx, by, bw, bh), 'Reset Statistics', L_GRAY),
                   Button((bx, by + pad, bw, bh), 'Delete Account', RED),
                   Button((bx, by + pad * 2, bw, bh), 'Back', L_GRAY)]

        # draw and render
        for button in buttons:
            button.queue()

        # return buttons input checking
        return buttons

    '''
    main
    '''

    def main(self):
        # variable initialization
        global mx, my, button
        button = 0
        menu = 0
        b = self.drawMain()

        # menus to draw based on menu index
        menus = [self.drawMain,
                 self.drawMain,
                 self.drawLocal,
                 self.drawLeader,
                 self.drawSettings
                 ]

        while True:

            # user input assign
            inp = userInput(mx, my, button)
            if inp is None:
                # quit
                return
            else:
                mx, my, button = inp[:-1]

            if button:
                button = 0

                for i in range(len(b)):
                    if b[i].getButton().collidepoint(mx, my):

                        if menu == 0:
                            # button clicking on main dash changes menu state
                            menu = i + 1

                        elif menu == 2:
                            # back to dashboard
                            if i == 3:
                                menu = 0
                                init.message = ''
                                break

                            # play
                            return Game(self.username, i + 1).play()

                        elif menu == 3:
                            # back to dashboard
                            menu = 0
                            init.message = ''

                        elif menu == 4:

                            if i == 1:
                                # reset statistics
                                User(self.username).reset()

                            elif i == 2:
                                # delete user and logout
                                User(self.username).delete()

                                return self.logout()

                            elif i == 3:
                                # back to dashboard
                                menu = 0
                                init.message = ''

                        # stop checking for other buttons' collision if any button pressed
                        break

                if menu == 1:
                    return Game(self.username, 0).play()

                if menu == 5:
                    init.message = 'Logged off successfully'
                    return self.logout()

                # menu draw
                b = menus[menu]()

                # final flip
                display.flip()
