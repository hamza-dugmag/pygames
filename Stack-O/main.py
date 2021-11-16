# Hamza Dugmag
# main.py
#

from pygame import quit
import menu
import dashboard


def run(running):
    if running:
        # start with main menu
        user = menu.main()
        if user is not None:
            # draw dashboard on successful log in
            playing = dashboard.Dash(user).main()

            # reopen main menu on logoff, otherwise quit
            return run(playing)

    # quit
    return


# run game
run(True)

# quit game
quit()
