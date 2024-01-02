import pygame
from pygame_utils import drawText
import random
from enum import Enum
from pygame.locals import *
from termcolor import colored


# constants 
pygame.font.init()
titleFont = pygame.font.Font('freesansbold.ttf', 12)

class bcolors:
    HANDCARDS = '\033[94m'
    OKCYAN = '\033[96m'
    LIMBSTATE = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    NEWTURN = '\033[1m'
# class Game:
#     W = 640
#     H = 640
#     SIZE = W, H

#     def __init__(self):
#         pygame.init()
#         self.screen = pygame.display.set_mode(Game.SIZE)
#         pygame.display.set_caption("Pygame Tiled Demo")
#         self.running = True
#         self.board = Board()

#     def run(self):
#         while self.running:
#             for event in pygame.event.get():
#                 if event.type == QUIT:
#                     self.running = False

#                 elif event.type == KEYDOWN:
#                     if event.key == K_l:
#                         self.load_image(file)
#             self.board.load(self.screen)
#             pygame.display.update()
        

#     def load_image(self, file):
#         self.file = file
#         self.image = pygame.image.load(file)
#         self.rect = self.image.get_rect()

#         self.screen = pygame.display.set_mode(self.rect.size)
#         pygame.display.set_caption(f'size:{self.rect.size}')
#         self.screen.blit(self.image, self.rect)
#         pygame.display.update()


class LimbStatus(Enum):
    FREE = 0
    UNAVAILABLE = 1


class Deck:
    def __init__(self, cards):
        self.cards = cards

    def shuffleDeck(self):
        random.shuffle(self.cards)

class Hand:
    def __init__(self, size, targetDeck):
        self.cards = []
        self.targetDeck = targetDeck
        for i in range(size):
            self.cards.append(targetDeck.cards.pop())
        print(colored("Setup complete!", "red"))
    def display(self):
        for i in self.cards:
            print(colored(" " + i.name, "blue"))
    
    def guiDisplay(self, game):
        for i in range(len(self.cards)):
            game.screen.blit(self.cards[i].image, (252 + (68 * (i - 2)), 500))


class Player:
    def __init__(self, name, deck, game, opponent=None):
        self.name = name
        self.limbs = {
            "arm1": LimbStatus.FREE,
            "arm2": LimbStatus.FREE,
            "leg1": LimbStatus.FREE, 
            "leg2": LimbStatus.FREE, 
            "head": LimbStatus.FREE,
            "torso": LimbStatus.FREE
        }
        self.deck = deck
        self.game = game
        self.opponent = opponent
        self.hand = Hand(5, self.deck) 

    def checkValid(self, requirements):
        for x in requirements:
            if self.limbs[x] != requirements[x]:
                return False
        return True

    def refreshHand(self):
        for x in self.hand.cards:
            x.updateValid(self.game, self, self.opponent)


    def playCard(self, cardIndex):
        targetCard = self.hand.cards[cardIndex]
        if targetCard.valid:
            targetCard.play(self.game, self, self.opponent)
        else:
            print(colored("Not valid.", "red"))
        self.deck.cards.append(self.hand.cards.pop(cardIndex))
        self.hand.cards.append(self.deck.cards.pop(0))
        return isinstance(targetCard, SubmissionCard)

    def display(self):
        for i in self.limbs: 
            print(colored(i + " " + ("Free" if self.limbs[i] == LimbStatus.FREE else "Unavailable"), "green"))
    
    def showHand(self):
        self.hand.guiDisplay(self.game)


class Position:
    def __init__(self, name):
        self.name = name


class MovementCard:
    def __init__(self, name, positionOptions, limbRequirementsPlayer, limbRequirementsTarget, limbChangesPlayer, limbChangesTarget):
        self.positionOptions = positionOptions
        self.limbRequirementsPlayer = limbRequirementsPlayer
        self.limbRequirementsTarget = limbRequirementsTarget
        self.valid = False
        self.limbChangesPlayer = limbChangesPlayer
        self.limbChangesTarget = limbChangesTarget
        self.name = name 

        self.image = pygame.Surface((64, 128))
        self.image.fill((127, 127, 127))
        text = titleFont.render(self.name, True, "black")
        drawText(self.image, self.name, "black", (2, 4, 60, 32), titleFont)
        # self.image.blit(self.titleSurface, (2, 8))

    def updateValid(self, game, player, target):
        if game.position in self.positionOptions and player.checkValid(self.limbRequirementsPlayer) and target.checkValid(self.limbRequirementsTarget):
            self.valid = True
        else:
            self.valid = False


    def play(self, game, player, target):
        for x in self.limbChangesPlayer:
            player.limbs[x] = self.limbChangesPlayer[x]

        for x in self.limbChangesTarget:
            target.limbs[x] = self.limbChangesTarget[x]

class TransitionCard(MovementCard):
    def __init__(self, name, positionOptions, limbRequirementsPlayer, limbRequirementsTarget, limbChangesPlayer, limbChangesTarget, position):
        super().__init__(name, positionOptions, limbRequirementsPlayer, limbRequirementsTarget, limbChangesPlayer, limbChangesTarget)
        self.position = position


    def play(self, game, player, target):
        super().play(game, player, target)
        game.initiative = player
        game.position = self.position

class SubmissionCard(MovementCard):
    def __init__(self, name, positionOptions, limbRequirementsPlayer, limbRequirementsTarget, limbChangesPlayer, position):
        super().__init__(name, positionOptions, limbRequirementsPlayer, limbRequirementsTarget, limbChangesPlayer)
        self.limbChangesPlayer = {}
        self.limbChangesTarget = {}

    def play(self, game, player, target):
        print("Game ends!")

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 640))
        self.screen.fill((255, 255, 255))
        pygame.display.set_caption("Pygame Tiled Demo")
        self.running = True

        def generateLeftArmPins(length):
            return [MovementCard("Left Arm Pin", ["Closed Guard", "Open Guard", "Half Guard"], {"arm1": LimbStatus.FREE}, {"arm1": LimbStatus.FREE}, {}, {"arm1": LimbStatus.UNAVAILABLE}) for i in range(length)]

        def generateRightArmPins(length):
            return [MovementCard("Right Arm Pin", ["Closed Guard", "Open Guard", "Half Guard"], {"arm2": LimbStatus.FREE}, {"arm2": LimbStatus.FREE}, {}, {"arm2": LimbStatus.UNAVAILABLE}) for i in range(length)]

        def generateLeftLegPins(length):
            return [MovementCard("Left Leg Pin", ["Closed Guard", "Open Guard", "Half Guard"], {"arm1": LimbStatus.FREE}, {"leg1": LimbStatus.FREE}, {}, {"leg1": LimbStatus.UNAVAILABLE}) for i in range(length)]
        
        def generateRightLegPins(length):
            return [MovementCard("Right Leg Pin", ["Closed Guard", "Open Guard", "Half Guard"], {"arm2": LimbStatus.FREE}, {"leg2": LimbStatus.FREE}, {}, {"leg2": LimbStatus.UNAVAILABLE}) for i in range(length)]
       
        def generateLeftLegSweep(length):
            return [MovementCard("Left Leg Sweep", ["Closed Guard", "Open Guard", "Half Guard"], {"leg1": LimbStatus.UNAVAILABLE}, {"leg1": LimbStatus.FREE}, {"leg1": LimbStatus.FREE}, {"leg1": LimbStatus.UNAVAILABLE}) for i in range(length)]
        
        def generateRightLegSweep(length):
            return [MovementCard("Right Leg Sweep", ["Closed Guard", "Open Guard", "Half Guard"], {"leg2": LimbStatus.UNAVAILABLE}, {"leg2": LimbStatus.FREE}, {"leg2": LimbStatus.FREE}, {"leg2": LimbStatus.UNAVAILABLE}) for i in range(length)]
        
        def generateTorsoPin(length):
            return [MovementCard("Torso Pin", ["Closed Guard", "Open Guard", "Half Guard", "Full Mount"], {"torso": LimbStatus.FREE}, {"torso": LimbStatus.FREE}, {}, {"torso": LimbStatus.UNAVAILABLE}) for i in range(length)]

        def generateClosedToMountSwap(length):
            return [TransitionCard(
            "Breaking Guard", 
            ["Closed Guard", "Open Guard", "Half Guard"], 
            {"arm1": LimbStatus.FREE, "arm2": LimbStatus.FREE, "torso": LimbStatus.FREE}, 
            {"arm1": LimbStatus.UNAVAILABLE, "torso": LimbStatus.UNAVAILABLE}, 
            {"arm1": LimbStatus.FREE,
            "arm2": LimbStatus.FREE,
            "leg1": LimbStatus.FREE, 
            "leg2": LimbStatus.FREE, 
            "head": LimbStatus.FREE,
            "torso": LimbStatus.FREE}, 
            {"arm1": LimbStatus.UNAVAILABLE,
            "arm2": LimbStatus.UNAVAILABLE,
            "leg1": LimbStatus.FREE, 
            "leg2": LimbStatus.FREE, 
            "head": LimbStatus.FREE,
            "torso": LimbStatus.UNAVAILABLE
        },
        "Full Mount"
        ) for i in range(length)]


        self.deck = Deck(generateLeftArmPins(5) + generateRightArmPins(5) + generateLeftLegPins(5) + generateRightArmPins(5) + generateLeftLegSweep(5) + generateRightLegSweep(5) + generateTorsoPin(5) + generateClosedToMountSwap(5))
        self.deck.shuffleDeck()
        self.player1 = Player("player1", self.deck, self)
        self.player2 = Player("player2", self.deck, self)
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1

        self.initiative = self.player1
        self.position = "Closed Guard"
        self.deck = Deck
        self.currentPlayer = self.player1


    def runGame(self):
        while self.running:
            self.player1.refreshHand()
            self.player2.refreshHand()
            self.currentPlayer.showHand()
            
            pygame.display.set_caption('size:(640, 640)')

            print("Player 1:")
            self.player1.display()
            print("Player 2:")
            self.player2.display()
            pygame.display.update()
            self.running = (not self.turn())

        pygame.quit()

    def turn(self):
        print(self.currentPlayer.name, "turn!")
        print("Options:")
        self.currentPlayer.hand.display()
        inp = None
        while inp == None:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_0:
                        inp = 0
                        break
                    if event.key == pygame.K_1:
                        inp = 1
                        break
                    if event.key == pygame.K_2:
                        inp = 2
                        break
                    if event.key == pygame.K_3:
                        inp = 3
                        break
                    if event.key == pygame.K_4:
                        inp = 4
                        break
        
        if self.currentPlayer.playCard(inp):
            print("Game ended!")
            return True
        else:
            print("Changing turns")
            self.currentPlayer = self.currentPlayer.opponent
            return False




game = Game()
game.runGame()