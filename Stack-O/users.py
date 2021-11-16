# Hamza Dugmag
# users.py
#

import init


class User:

    def __init__(self, username='', password=''):
        # initialize variables
        self.username = username
        self.password = password

    def login(self):
        if len(self.username) >= init.minTextLen <= len(self.password):

            # open database
            db = open('players.dat', 'r')

            for line in db:
                # ignore line if empty
                if line.count(',') == 0:
                    continue

                field = line.rstrip('\n').split(',')
                if field[0] + field[1] == self.username + self.password:
                    # found user
                    init.message = ''
                    db.close()
                    return True

            # user does not exist
            init.message = 'User does not exist'
            db.close()

        else:
            # invalid field lengths
            init.message = 'Fields must be at least ' + str(init.minTextLen) + ' characters long'

    def register(self):
        if len(self.username) >= init.minTextLen <= len(self.password):

            # open database
            db = open('players.dat', 'r+')

            for line in db:
                # ignore line if empty
                if line.count(',') == 0:
                    continue

                field = line.rstrip('\n').split(',')
                if field[0] == self.username:
                    # halt continuation since found an existing user
                    init.message = 'User already exists'
                    db.close()
                    return

            # create user
            db.write('\n' + self.username + ',' + self.password + ',0,0')

            # construct message and close file
            init.message = 'User created successfully'
            db.close()

        else:
            # invalid field lengths
            init.message = 'Fields must be at least ' + str(init.minTextLen) + ' characters long'

    def delete(self):
        # open database
        db = open('players.dat')
        lines = db.read().splitlines()

        for line in range(len(lines)):
            # ignore line if empty
            if lines[line].count(',') == 0:
                continue

            field = lines[line].rstrip('\n').split(',')
            if field[0] == self.username:
                # change line to empty and stop checking for other lines
                lines[line] = ''
                break

        # reopen file as write to overwrite changed lines
        open('players.dat', 'w').write('\n'.join(lines))

        # construct message and close file
        init.message = 'User deleted successfully'
        db.close()

    def reset(self):
        # open database
        db = open('players.dat')
        lines = db.read().splitlines()

        for line in range(len(lines)):
            # ignore empty line
            if lines[line].count(',') == 0:
                continue

            field = lines[line].rstrip('\n').split(',')
            if field[0] == self.username:
                # change stats to 0
                field[2] = field[3] = '0'
                lines[line] = ','.join(field)
                break

        # reopen file as write to overwrite changed lines
        open('players.dat', 'w').write('\n'.join(lines))

        # construct message and close file
        init.message = 'Statistics resetted successfully'
        db.close()

    def update(self, points):
        # open database
        db = open('players.dat')
        lines = db.read().splitlines()

        for line in range(len(lines)):
            # ignore empty line
            if lines[line].count(',') == 0:
                continue

            field = lines[line].rstrip('\n').split(',')
            if field[0] == self.username:
                # update stats
                field[2] = str(int(field[2]) + points)
                field[3] = str(int(field[3]) + 1)
                lines[line] = ','.join(field)
                break

        # reopen file as write to overwrite changed lines
        open('players.dat', 'w').write('\n'.join(lines))

        # close file
        db.close()

    def getLeaderboard(self):
        # initialize leaderboard array
        leader = []

        # open database
        db = open('players.dat')
        lines = db.read().splitlines()

        for line in range(len(lines)):
            # ignore empty line
            if lines[line].count(',') == 0:
                continue

            field = lines[line].rstrip('\n').split(',')

            # get stats
            user = field[0]
            pointSum = int(field[2])
            gamesPlayed = int(field[3])

            try:
                avg = round(pointSum / gamesPlayed, 1)
            except Exception:
                # error from division by zero
                avg = 0

            # append stats to leaderboard
            leader.append([avg, user])

            # sort leaderboard based on average points
            leader.sort()

            if len(leader) == 5:
                # stop appending after leaderboard has 5 players
                break

        # close file and return leaderboard
        db.close()
        return leader
