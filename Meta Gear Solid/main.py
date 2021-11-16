# Developed by Hamza Dugmag
# Sprites created by third-party
# ISCU1 Summative Project
# Created 01/20/2018
# Modified 01/24/2018
# Follows PEP-8 code design standards
#

# ============================================================= Initialization

# import
from pygame import *
from random import *
from math import *

# pygame initialization
init()

# display window
SIZE = (WIDTH, HEIGHT) = (1000, 700)
SCREEN = display.set_mode(SIZE)
DEBUG = False

# user input defaults
mx = my = 0
button = 0
k = 0

# ============================================================= Resources

# player sprites
PLAYER_SPRITES = {
    'UP': image.load('sprites/player/player_up.png'),
    'DOWN': image.load('sprites/player/player_down.png'),
    'RIGHT': image.load('sprites/player/player_right.png'),
    'LEFT': image.load('sprites/player/player_left.png')
}

# enemy sprites
ENEMY_SPRITES = {
    'UP': image.load('sprites/enemy/enemy_up.png'),
    'DOWN': image.load('sprites/enemy/enemy_down.png'),
    'RIGHT': image.load('sprites/enemy/enemy_right.png'),
    'LEFT': image.load('sprites/enemy/enemy_left.png')
}

# colors
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
L_RED = (255, 100, 90)
BLUE = (0, 0, 255)

# shades
WHITE = (255, 255, 255)
L_GRAY = (220, 220, 220)
D_GRAY = (20, 20, 20)
BLACK = (0, 0, 0)


# ============================================================= Character

class Character:

    def __init__(self, x, y, sprites, isEnemy=False):
        '''
        DESCRIPTION
        Initializes Character class instance

        INPUT
        self: class instance
        x: absolute start x location
        y: absolute start y location

        OUTPUT
        None
        '''

        # image variables
        self.sprites = sprites
        self.img = self.sprites[choice(['UP', 'DOWN', 'RIGHT', 'LEFT'])]
        self.isEnemy = isEnemy

        # locomotion variables
        self.walk = 1
        self.sprint = 2
        self.vel = self.walk

        self.x = x
        self.y = y

        self.dir = {
            'UP': False,
            'DOWN': False,
            'RIGHT': False,
            'LEFT': False
        }

        # health variables
        self.health = 100
        self.isDead = False
        self.updateHitbox()

        # weapon variables
        self.suppr = 100
        self.isFiring = False

    def move(self):
        '''
        DESCRIPTION
        Changes character location and sprite via x and y values

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        if self.dir['UP']:
            self.y -= self.vel
            self.img = self.sprites['UP']

        elif self.dir['DOWN']:
            self.y += self.vel
            self.img = self.sprites['DOWN']

        elif self.dir['RIGHT']:
            self.x += self.vel
            self.img = self.sprites['RIGHT']

        elif self.dir['LEFT']:
            self.x -= self.vel
            self.img = self.sprites['LEFT']

        # horizontal collision detection with end of map
        if self.x < 0:
            self.x = 0

        elif self.x + self.w > WIDTH:
            self.x = WIDTH - self.w

        # vertical collision detection with end of map
        if self.y < 0:
            self.y = 0

        elif self.y + self.h > HEIGHT:
            self.y = HEIGHT - self.h

    def updateHitbox(self):
        '''
        DESCRIPTION
        Updates hitbox rectangle according to image

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # get image dimensions
        self.hitbox = self.img.get_rect()

        # retrieve image width and height
        self.w = self.hitbox[2]
        self.h = self.hitbox[3]

        # create hitbox
        self.hitbox = Rect(self.x, self.y, self.w, self.h)

    def pullTrigger(self):
        '''
        DESCRIPTION
        Spawns bullet based on direction facing

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # dull out suppressor
        self.isFiring = True
        self.suppr -= 5 if self.suppr > 0 else 0

        # calculate bullet spawn and destination
        if self.img == self.sprites['UP']:
            ox = self.x + (self.w // 2)
            oy = self.y
            tx = ox
            ty = 0

        elif self.img == self.sprites['DOWN']:
            ox = self.x + (self.w // 2)
            oy = self.y + self.h
            tx = ox
            ty = HEIGHT

        elif self.img == self.sprites['RIGHT']:
            ox = self.x + self.w
            oy = self.y + 8
            tx = WIDTH
            ty = self.y

        else:
            ox = self.x
            oy = self.y + 8
            tx = 0
            ty = self.y

        # spawn bullets
        Bullet(ox, oy, tx, ty, self.isEnemy)

    def tick(self):
        '''
        DESCRIPTION
        Called every frame to update and draw character

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        self.isFiring = False

        # move and update hitbox
        self.move()
        self.updateHitbox()

        # draw character
        SCREEN.blit(self.img, self.hitbox)

        if DEBUG:
            # draw hitbox
            draw.rect(SCREEN, RED, self.hitbox, 1)


class Enemy(Character):

    _instances = []
    _lowered = False
    _anyCombat = False

    def __init__(self, x, y):
        '''
        DESCRIPTION
        Initializes Enemy class instance

        INPUT
        self: class instance
        x: absolute start x location
        y: absolute start y location

        OUTPUT
        None
        '''

        # append enemy instance to instances
        Enemy._instances.append(self)

        # Character initialization
        Character.__init__(self, x, y, ENEMY_SPRITES, True)

        # artificial intelligence
        self.state = {
            'PATROL': True,
            'ALERT': False,
            'COMBAT': False
        }

        self.inVision = 0
        self.notCombat = 0
        self.combatTime = 0
        self.alertTime = 0

        self.createSense()
        self.resetLocomotion()

    def resetLocomotion(self):
        '''
        DESCRIPTION
        Assigns random values to patrol times

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # random direction for patrol
        self.changeDir(choice(['UP', 'DOWN', 'RIGHT', 'LEFT']))

        # steps
        self.steps = 0
        self.stepsToTake = randint(50, 150)
        self.waitTime = randint(100, 400)

    def changeState(self, state):
        '''
        DESCRIPTION
        Changes AI state

        INPUT
        state: AI state to set to True

        OUTPUT
        None
        '''

        # reset all states to False
        for key in self.state.keys():
            self.state[key] = False

        # change given state to True
        self.state[state] = True

    def createSense(self):
        '''
        DESCRIPTION
        Creates peripheral and audible areas for AI sensing

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # peripheral area dimensions
        if self.state['PATROL']:
            dim = 150
        else:
            dim = 250

        x = self.x + (self.w // 2) - (dim // 2)
        y = self.y + (self.h // 2) - (dim // 2)

        # create peripheral Rect
        self.peripheral = Rect(x, y, dim, dim)

        # audible area dimesnions
        dim *= 2

        x = self.x + (self.w // 2) - (dim // 2)
        y = self.y + (self.h // 2) - (dim // 2)

        # creater audible Rect
        self.audible = Rect(x, y, dim, dim)

    def changeDir(self, d=None):
        '''
        DESCRIPTION
        Sets direction moving in

        INPUT
        self: class instance
        d (None): direction to move to

        OUTPUT
        None
        '''

        # reset all directions
        for key in self.dir.keys():
            self.dir[key] = False

        # set given direction to True if valid
        if d is not None:
            self.dir[d] = True

    def drawState(self, col):
        '''
        DESCRIPTION
        Draws visual representation of AI state

        INPUT
        self: class instance
        col: color of rectangle

        OUTPUT
        None
        '''

        # box width and height
        dim = 5

        # draw color coded rectangle
        draw.rect(SCREEN, col, (
            self.x + (self.w // 2) - (dim // 2),
            self.y - 10,
            dim,
            dim
        ))

    def sense(self):
        '''
        DESCRIPTION
        Changes AI state based on player location

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # combat if seen player for a period
        if self.inVision >= 100:
            self.changeState('COMBAT')
            return

        # alert if player firing without suppressor in peripheral area
        if self.audible.colliderect(player.hitbox):
            if player.isFiring and player.suppr <= 0 or player.vel == player.sprint:
                self.changeState('ALERT')

        # alert if seen bullet
        for bullet in Bullet._instances:
            if self.peripheral.colliderect(bullet.hitbox):
                self.changeState('ALERT')

        # alert if seen bullet
        if self.peripheral.colliderect(player.hitbox) and not player.hiding:
            self.changeState('ALERT')
            self.inVision += 1

        else:
            # reset time for seen player if escaped vision
            self.inVision = 0

    def fire(self):
        '''
        DESCRIPTION
        Fires weapon randomly to prevent firing on each frame

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # stop movement
        self.changeDir()

        # all enemies not not combatting
        for enemy in Enemy._instances:
            enemy.notCombat = 0

        # pull trigger at random frame
        if randint(0, 50) == 0:
            self.pullTrigger()

    def gotoPlayer(self):
        '''
        DESCRIPTION
        Moves towards player and fires when valid

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # player coordinates
        tx = player.x
        ty = player.y

        # enemy coordinates
        ox = self.x
        oy = self.y

        # difference between coordinates
        dx = ox - tx
        dy = oy - ty

        # fire horizontally
        if dy == 0:
            if ox < tx:
                if self.img == self.sprites['RIGHT'] and abs(dx) <= 250:
                    self.fire()
                else:
                    self.changeDir('RIGHT')
            elif ox > tx:
                if self.img == self.sprites['LEFT'] and abs(dx) <= 250:
                    self.fire()
                else:
                    self.changeDir('LEFT')

        # fire vertically
        elif dx == 0:
            if oy > ty:
                if self.img == self.sprites['UP'] and abs(dy) <= 250:
                    self.fire()
                else:
                    self.changeDir('UP')
            elif oy < ty:
                if self.img == self.sprites['DOWN'] and abs(dy) <= 250:
                    self.fire()
                else:
                    self.changeDir('DOWN')

        # move to player dimensions
        elif dx > 0 and dy != 0:
            if dy > 0:
                self.changeDir('LEFT')

            else:
                self.changeDir('DOWN')

        elif dx < 0 and dy != 0:
            if dy > 0:
                self.changeDir('UP')

            else:
                self.changeDir('RIGHT')

    def tick(self):
        '''
        DESCRIPTION
        Called every frame to update and draw enemy

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # Character tick function
        Character.tick(self)

        # create sense perimeters
        self.createSense()

        # check if any is in combat
        Enemy._anyCombat = False
        for enemy in Enemy._instances:
            if enemy.state['COMBAT']:
                Enemy._anyCombat = True
                break

        # check if enemy is dead
        if self.health <= 0:
            self.isDead = True

        if self.isDead:
            # remove enemy instance from instances list if dead
            try:
                Enemy._instances.remove(self)
            except Exception:
                pass

        if not self.state['COMBAT']:
            # grade may be lowered again
            if not Enemy._anyCombat:
                Enemy._lowered = False

            # sense for player to enter combat
            self.sense()

            # reset combat variables
            self.notCombat = 0
            self.combatTime = 0

            # idle
            if self.steps >= self.waitTime:
                self.resetLocomotion()

            # walk in random direction
            elif self.steps >= self.stepsToTake:
                self.changeDir()

            # increment steps taken
            self.steps += 1

            # draw state
            if self.state['PATROL']:
                self.drawState(GREEN)
            else:
                self.drawState(YELLOW)

                # patrol back again if coast is clear
                self.alertTime += 1
                if self.alertTime >= 500:
                    self.alertTime = 0
                    self.changeState('PATROL')

        else:
            Enemy._anyCombat = True

            # draw combat state
            self.drawState(RED)

            # increase time combatting
            self.combatTime += 1

            # increase time of not combatting if not seeing player
            if not self.peripheral.colliderect(player.hitbox):
                self.notCombat += 1

            else:
                self.notCombat = 0

            # move to player and fire
            self.gotoPlayer()

            # inform other enemies of player presence after certain time
            if self.combatTime >= 300:
                for enemy in Enemy._instances:
                    # lower grade
                    if not Enemy._lowered:
                        Enemy._lowered = True
                        global gradeIdx, grades
                        gradeIdx += 1 if gradeIdx != len(grades) - 1 else 0

                    enemy.changeState('COMBAT')

                    try:
                        com.changeState('COMBAT')
                    except Exception:
                        pass

            # become alerted if have not combatted player for period
            if self.notCombat >= 750:
                for enemy in Enemy._instances:
                    enemy.changeState('ALERT')

                    try:
                        com.changeState('ALERT')
                    except Exception:
                        pass

                    enemy.inVision = 0

        if DEBUG:
            # draw sense areas
            draw.rect(SCREEN, RED, self.peripheral, 1)
            draw.rect(SCREEN, RED, self.audible, 1)

            # health bar
            draw.rect(SCREEN, RED, (self.x, self.y + self.h + 10, self.health // 2, 10))


class Commander(Enemy):

    def __init__(self, x, y):
        '''
        DESCRIPTION
        Initializes Commander class instance

        INPUT
        self: class instance
        x: absolute start x location
        y: absolute start y location

        OUTPUT
        None
        '''

        # Enemy initialization
        Enemy.__init__(self, x, y)
        Enemy._instances.remove(self)

        # override health
        self.health = 200

        # objective image
        self.objective = image.load('sprites/misc/objective.png')
        self.oRect = self.objective.get_rect()

        self.ow = self.oRect[2]
        self.oh = self.oRect[3]

    def tick(self):
        '''
        DESCRIPTION
        Called every frame to update objective on commander

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # Enemy tick function
        Enemy.tick(self)

        # assign objective to a random generator on killed and alert all enemies
        if self.isDead:
            choice(Generator._instances).isObj = True

            for enemy in Enemy._instances:
                if enemy.state['PATROL']:
                    enemy.changeState('ALERT')

        # show objective
        ox = self.x + (self.w // 2) - (self.ow // 2)
        oy = self.y + (self.h // 2) - (self.oh // 2)
        SCREEN.blit(self.objective, Rect(ox, oy, self.ow, self.oh))


class Player(Character):

    def __init__(self, x, y):
        '''
        DESCRIPTION
        Initializes Player class instance

        INPUT
        self: class instance
        x: absolute start x location
        y: absolute start y location

        OUTPUT
        None
        '''

        # Character initialization
        Character.__init__(self, x, y, PLAYER_SPRITES, False)

        # override health
        self.health = 255

        self.interacting = False
        self.hiding = False

        self.loweredGrade = False

    def setSpeed(self, t):
        '''
        DESCRIPTION
        Sets character speed

        INPUT
        self: class instance
        t: type of locomotion (walk / sprint)

        OUTPUT
        None
        '''

        # whether player can sprint
        canSprint = False
        for d in self.dir.keys():
            if self.dir[d]:
                canSprint = True
                break

        if t == 'WALK':
            # walk
            self.vel = self.walk

        elif t == 'SPRINT' and canSprint:
            # sprint
            self.vel = self.sprint

    def setDir(self, k, pressed=True):
        '''
        DESCRIPTION
        Sets direction states

        INPUT
        self: class instance
        k: the key pressed / released
        pressed (True): whether key was pressed or released

        OUTPUT
        None
        '''

        if k == K_w:
            player.dir['UP'] = pressed

        elif k == K_s:
            player.dir['DOWN'] = pressed

        elif k == K_d:
            player.dir['RIGHT'] = pressed

        elif k == K_a:
            player.dir['LEFT'] = pressed

    def tick(self):
        '''
        DESCRIPTION
        Called every frame to update and draw player

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # lower grade if ran out of suppressor
        if self.suppr <= 0 and not self.loweredGrade:
            global gradeIdx
            gradeIdx += 1 if gradeIdx != len(grades) - 1 else 0
            self.loweredGrade = True

        # Character tick function
        Character.tick(self)

        # player is not destroying generator
        player.interacting = False

        # end game if dead
        global done

        if player.health <= 0:
            done = True


# ============================================================= Props

class Bullet:

    _instances = []

    def __init__(self, x, y, tx, ty, enemyBullet):
        '''
        DESCRIPTION
        Initializes Bullet class instance

        INPUT
        self: class instance
        dmg: bullet damage
        trnq (False): ability to tranquilize

        OUTPUT
        None
        '''

        # append bullet to instances
        Bullet._instances.append(self)

        # damage
        self.dmg = randint(20, 30)
        self.enemyBullet = enemyBullet

        # original spawn location
        self.ox = x
        self.oy = y

        # current location
        self.x = self.ox
        self.y = self.oy

        # destination
        self.tx = tx
        self.ty = ty

        # life
        self.vel = 15
        self.life = 25
        self.age = 0

        # image
        self.img = image.load('sprites/misc/bullet.png')
        self.updateHitbox()

    def updateHitbox(self):
        '''
        DESCRIPTION
        Updates hitbox rectangle according to bullet image

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # get image dimensions
        self.hitbox = self.img.get_rect()

        # retrieve image width and height
        self.w = self.hitbox[2]
        self.h = self.hitbox[3]

        # create hitbox
        self.hitbox = Rect(self.x, self.y, self.w, self.h)

    def checkCollision(self):
        '''
        DESCRIPTION
        Checks bullet collision with all objects in world and applies functionality

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        if self.enemyBullet:

            if self.hitbox.colliderect(player.hitbox):
                # damage player if enemy bullet and keep health positive, then delete bullet
                player.health -= self.dmg if self.dmg < player.health else player.health
                Bullet._instances.remove(self)

        else:
            shotEnemy = False

            # add commander to enemy list
            enemies = Enemy._instances[:]
            if not com.isDead:
                enemies += [com]

            for enemy in enemies:
                # damage enemy and set state to combat if player bullet, then delete bullet
                if self.hitbox.colliderect(enemy.hitbox) and not shotEnemy:
                    try:
                        Bullet._instances.remove(self)
                    except Exception:
                        pass

                    shotEnemy = True
                    enemy.health -= self.dmg
                    enemy.changeState('COMBAT')
                    enemy.notCombat = 0

    def tick(self):
        '''
        DESCRIPTION
        Called every frame to update and draw bullet

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # increment bullet age
        self.age += 1

        # update bullet location
        self.x += int(self.vel * (self.tx - self.ox) /
                      dist(self.ox, self.oy, self.tx, self.ty))

        self.y += int(self.vel * (self.ty - self.oy) /
                      dist(self.ox, self.oy, self.tx, self.ty))

        # delete bullet after life span reached
        if self.age >= self.life:
            Bullet._instances.remove(self)

        # update hitbox and check for collision
        self.updateHitbox()
        self.checkCollision()

        # draw bullet
        SCREEN.blit(self.img, self.hitbox)


class Generator:

    _instances = []

    def __init__(self, x, y):
        '''
        DESCRIPTION
        Initializes Generator class instance

        INPUT
        self: class instance
        x: absolute start x location
        y: absolute start y location

        OUTPUT
        None
        '''

        # append bullet to instances
        Generator._instances.append(self)

        # image
        self.img = image.load('sprites/misc/generator.png')
        self.imgRect = self.img.get_rect()

        # hitbox
        self.x = x
        self.y = y
        self.w = self.imgRect[2]
        self.h = self.imgRect[3]

        self.hitbox = Rect(self.x, self.y, self.w, self.h)

        # whether generator is the next objective
        self.isObj = False

        # objective image
        self.objective = image.load('sprites/misc/objective.png')
        self.oRect = self.objective.get_rect()

        self.ow = self.oRect[2]
        self.oh = self.oRect[3]

    def destroy(self):
        '''
        DESCRIPTION
        Assigns objective to another generator

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # set another generator as objective if defused by player
        if self.hitbox.colliderect(player.hitbox) and player.interacting and self.isObj:
            Generator._instances.remove(self)

            try:
                choice(Generator._instances).isObj = True
            except Exception:
                # set exit as objective if no more generators
                global lz
                lz = LZ(randint(0, WIDTH), randint(0, HEIGHT - 40))

            # alert all enemies
            for enemy in Enemy._instances:
                if enemy.state['PATROL']:
                    enemy.changeState('ALERT')

    def tick(self):
        '''
        DESCRIPTION
        Called every frame to update objective on generator

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # blit generator
        SCREEN.blit(self.img, self.hitbox)

        # show objective if is
        if self.isObj:
            ox = self.x + (self.w // 2) - (self.ow // 2)
            oy = self.y + (self.h // 2) - (self.oh // 2)
            SCREEN.blit(self.objective, Rect(ox, oy, self.ow, self.oh))

        # remove generator if destroyed
        self.destroy()

        if DEBUG:
            # draw generator hitbox
            draw.rect(SCREEN, RED, self.hitbox, 1)


class Hiding:

    _instances = []

    def __init__(self, x, y):
        '''
        DESCRIPTION
        Initializes Hiding class instance

        INPUT
        self: class instance
        x: absolute start x location
        y: absolute start y location

        OUTPUT
        None
        '''

        # append bullet to instances
        Hiding._instances.append(self)

        # image
        self.img = image.load('sprites/misc/hiding.png')
        self.imgRect = self.img.get_rect()

        # hitbox
        self.x = x
        self.y = y
        self.w = self.imgRect[2]
        self.h = self.imgRect[3]

        self.hitbox = Rect(self.x, self.y, self.w, self.h)

        # objective image
        self.objective = image.load('sprites/misc/objective.png')
        self.oRect = self.objective.get_rect()

        self.ow = self.oRect[2]
        self.oh = self.oRect[3]

    def tick(self):
        '''
        DESCRIPTION
        Called every frame to draw missing bit

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # blit missing bit
        SCREEN.blit(self.img, self.hitbox)

        if DEBUG:
            # draw generator hitbox
            draw.rect(SCREEN, RED, self.hitbox, 1)


class LZ:

    def __init__(self, x, y):
        '''
        DESCRIPTION
        Initializes LZ class instance

        INPUT
        self: class instance
        x: absolute start x location
        y: absolute start y location

        OUTPUT
        None
        '''

        # image
        self.img = image.load('sprites/misc/landing_zone.png')
        self.imgRect = self.img.get_rect()

        # hitbox
        self.x = x
        self.y = y
        self.w = self.imgRect[2]
        self.h = self.imgRect[3]

        self.hitbox = Rect(self.x, self.y, self.w, self.h)

    def tick(self):
        '''
        DESCRIPTION
        Called every frame to update and draw LZ

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # blit generator
        SCREEN.blit(self.img, self.hitbox)

        # end game if player escaped
        if self.hitbox.colliderect(player.hitbox) and player.interacting:
            global done
            done = True

        if DEBUG:
            # draw generator hitbox
            draw.rect(SCREEN, RED, self.hitbox, 1)


# ============================================================= Menu


# font
em = font.SysFont('Calbri', 22)
em_5 = font.SysFont('Calbri', 14)
em2 = font.SysFont('Calbri', 32, False, True)

# button dimensions
bw = 250
bh = 30
bx = (WIDTH // 2) - (bw // 2)
pad = bh + (bh // 2)
by = (HEIGHT // 2) - ((bh + pad) // 2)


class Button:

    def __init__(self, dim, text, col):
        '''
        DESCRIPTION
        Initializes Button class instance

        INPUT
        self: class instance
        dim: button dimensions (x, y, w, h)
        text: button text
        col: button background color

        OUTPUT
        None
        '''

        # defaults
        self.dim = Rect(*dim)
        self.text = text
        self.col = col

        # text dimensions
        tSize = em.size(text)

        tw = tSize[0]
        th = tSize[1]
        tx = (dim[0] + (dim[2] // 2)) - (tw // 2)
        ty = (dim[1] + (dim[3] // 2)) - (th // 2)

        # text Rect
        self.tRect = Rect(tx, ty, tw, th)

    def queue(self):
        '''
        DESCRIPTION
        Draw button

        INPUT
        self: class instance

        OUTPUT
        None
        '''

        # box draw
        draw.rect(SCREEN, self.col, self.dim)

        # text blit
        text = em.render(self.text, 1, D_GRAY)
        SCREEN.blit(text, self.tRect)


def genText(string, font, ty, col=L_GRAY, tx=None):
    '''
    DESCRIPTION
    Draw button

    INPUT
    string: string text
    font: font file
    ty: text y coordinate
    col: text color

    OUTPUT
    None
    '''

    # text dimensions
    size = font.size(string)
    text = font.render(string, 1, col)

    tw = size[0]
    th = size[1]

    if tx is None:
        tx = (WIDTH // 2) - (tw // 2)

    # blit text
    tRect = Rect(tx, ty, tw, th)
    SCREEN.blit(text, tRect)


def drawTitle(title):
    '''
    DESCRIPTION
    Draws screen title

    INPUT
    title: screen title

    OUTPUT
    None
    '''

    # set window caption
    display.set_caption(title)

    # draw background
    draw.rect(SCREEN, D_GRAY, (0, 0, WIDTH, HEIGHT))

    # blit title and developer
    genText(title, em2, 250)
    genText('Developed by Hamza Dugmag', em_5, 650)


def drawMenu():
    '''
    DESCRIPTION
    Draws main menu screen

    INPUT
    None

    OUTPUT
    List of Button instances to check for mouse collision later
    '''

    # draw title
    drawTitle('ISCU1 SUMMATIVE')

    # create buttons
    buttons = [Button((bx, by, bw, bh), 'PLAY', L_GRAY),
               Button((bx, by + pad, bw, bh), 'INSTRUCTIONS', L_GRAY),
               Button((bx, by + pad * 2, bw, bh), 'QUIT', L_RED)]

    # draw buttons
    for button in buttons:
        button.queue()

    # return button list
    return buttons


def menu():
    '''
    DESCRIPTION
    Checks for user input in the main menu

    INPUT
    None

    OUTPUT
    None
    '''

    # user input variables
    global mx, my
    global button

    # set menu to main menu and draw
    menuIdx = 0
    menu = drawMenu()

    while True:

        # iterate over user input
        for ev in event.get():

            if ev.type == QUIT:
                # quit game
                return

            # mouse input
            elif ev.type == MOUSEBUTTONDOWN:
                # set mouse position and button clicked for menu interaction
                mx, my = ev.pos
                button = ev.button

        if menuIdx == 0:
            # draw main menu
            menu = drawMenu()

            if button == 1:
                # reset button on clicked
                button = 0

                # iterate over each valid button
                for b in range(len(menu)):

                    # check if user clicked a button
                    if menu[b].dim.collidepoint(mx, my):

                        if b == 0:
                            # play button runs game
                            game()

                            # redraw menu on main game exit
                            menu = drawMenu()

                        elif b == 1:
                            # change menu index on instructions
                            menuIdx = 1

                        else:
                            # quit button quits game
                            return

        elif menuIdx == 1:
            # draw instructions
            SCREEN.blit(image.load('sprites/instructions.png'), Rect(0, 0, 1000, 700))

            if button == 3:
                # return to main menu on right mouse button
                menuIdx = 0

        # tick flip
        display.flip()


# ============================================================= Game

def dist(x1, y1, x2, y2):
    '''
    DESCRIPTION
    Calculates distance between two points

    INPUT
    x1: x coordinate 1
    y1: y coordinate 1
    x2: x coordinate 2
    y2: y coordinate 2

    OUTPUT
    Integer: distance between (x1, y1) and (x2, y2)
    '''

    # return distance
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5


grades = ['S', 'A', 'B', 'C', 'D', 'F']
gradeIdx = 0


def drawHUD():
    '''
    DESCRIPTION
    Renders heads-up display

    INPUT
    None

    OUTPUT
    None
    '''

    # dimension calculation
    w = 255
    h = 10

    y1 = HEIGHT - (h * 1.25) * 4
    y2 = y1 + (h * 1.25)

    x = WIDTH - w - (HEIGHT - y2)

    # player variable retrieval
    hp = player.health
    suppr = player.suppr

    # health bar
    draw.rect(SCREEN, WHITE, (x, y1, w, h), 5)
    draw.rect(SCREEN, D_GRAY, (x, y1, w, h))

    draw.rect(SCREEN, (255 - hp, hp, 0), (x, y1, hp, h))

    # suppressor bar
    draw.rect(SCREEN, WHITE, (x, y2, w, h), 5)
    draw.rect(SCREEN, D_GRAY, (x, y2, w, h))

    draw.rect(SCREEN, L_GRAY, (x, y2, suppr * 2.55, h))

    # get current grade
    grade = grades[gradeIdx]

    # grade color
    if gradeIdx == 0:
        gradeCol = GREEN
    elif gradeIdx <= 2:
        gradeCol = YELLOW
    else:
        gradeCol = RED

    # show grade
    genText('Performance: ' + grade, em_5, y1 - 20, gradeCol, x)


player = None
com = None
lz = None
done = False


def game():
    '''
    DESCRIPTION
    Game loop; checks for user input in game and updates visuals every frame

    INPUT
    None

    OUTPUT
    None
    '''

    # reset game variables
    global done
    global gradeIdx
    done = False
    gradeIdx = 0

    # world creation
    global player
    global com
    global lz

    player = Player(10, HEIGHT - 40)
    com = Commander(randint(30, WIDTH), randint(0, HEIGHT - 40))

    for _ in range(10):
        Enemy(randint(50, WIDTH), randint(0, HEIGHT - 40))

    for _ in range(3):
        Generator(randint(50, WIDTH), randint(0, HEIGHT - 40))

    for _ in range(randint(7, 10)):
        Hiding(randint(0, WIDTH), randint(0, HEIGHT - 40))

    # clock
    frame = time.Clock()

    while not done:
        # maintain frames per second at 60 fps
        frame.tick(60)

        # reset screen
        draw.rect(SCREEN, (50, 50, 125), (0, 0, WIDTH, HEIGHT))

        # iterate over user input
        for ev in event.get():

            # quit game
            if ev.type == QUIT:
                done = True

            # mouse input
            elif ev.type == MOUSEBUTTONDOWN:

                # left mouse button click fires weapon
                if ev.button == 1:
                    player.pullTrigger()

            # key pressed
            elif ev.type == KEYDOWN:
                k = ev.key
                player.setDir(k, True)

                # sprint
                if k == K_LSHIFT:
                    player.setSpeed('SPRINT')

            # key released
            elif ev.type == KEYUP:
                k = ev.key
                player.setDir(k, False)

                # stop sprinting
                if k == K_LSHIFT:
                    player.setSpeed('WALK')

                # destroy generator
                if k == K_SPACE:
                    player.interacting = True

        # call all tick functions
        player.hiding = False
        for hiding in Hiding._instances:
            hiding.tick()

            if hiding.hitbox.colliderect(player.hitbox):
                player.hiding = True

        for bullet in Bullet._instances:
            bullet.tick()

        if not com.isDead:
            com.tick()

        for enemy in Enemy._instances:
            enemy.tick()

        for generator in Generator._instances:
            generator.tick()

        if lz is not None:
            lz.tick()

        player.tick()

        # draw heads-up display
        drawHUD()

        # tick flip
        display.flip()

    # clear world
    Enemy._instances = []
    Generator._instances = []
    Hiding._instances = []
    lz = None

    # return to main menu
    return


# launch main menu
menu()

# terminate pygame
quit()
