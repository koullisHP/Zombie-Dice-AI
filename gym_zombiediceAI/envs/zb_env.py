import random
import math
import gym

from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np


class ZombieDiceENV(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):

        self.brains = 0
        self.shotguns = 0
        self.footprints = 0
        self.dice = [GreenDice(), GreenDice(), GreenDice(), GreenDice(), GreenDice(), GreenDice(),
                     YellowDice(), YellowDice(), YellowDice(), YellowDice(),
                     RedDice(), RedDice(), RedDice()]  # list all dice
        self.minBrains = 0
        self.maxBrains = 29
        self.minShotguns = 0
        self.maxShotguns = 23
        self.minFootprints = 0
        self.maxFootprints = 26
        self.action_space = spaces.Discrete(2)
        self.low = np.array([self.minBrains, self.minShotguns, self.minFootprints])
        self.high = np.array([self.maxBrains, self.maxShotguns, self.maxFootprints])
        self.observation_space = spaces.Box(self.low, self.high, dtype=np.int)
        self.seed()
        self.viewer = None
        self.state = None
        self.reward = 0
        self.win = 0
        self.loss = 0

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def reset(self):
        brains = 0  # self.brains
        shotguns = 0  # self.shotguns
        footprints = 0  # self.footprints

        self.state = brains, shotguns, footprints
        return np.array(self.state)

    # main action of the game(player turns)
    def step(self, action):

        assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
        brains, shotguns, footprints = self.state
        done = False

        print("Brains:", brains, " Shotguns:", shotguns, " Footprints:", footprints)
        print("---   ---   ---")

        numFootprints = []

        b = 0  # int to hold number of brains rolled
        s = 0  # int to hold number of shotguns rolled

        pickedDice = self.dicePicker(numFootprints)  # list of dice to roll, the 3 dices to roll
        numFootprints = []  # list of rolled footprints dices

        for d in pickedDice:
            g = d.roll()  # string
            if g == "brain":
                b += 1
                print(d.color, "Brain!")
                # if d.color == "Green":
                #     self.reward += 1
                # elif d.color == "Yellow":
                #     self.reward += 2
                # elif d.color == "Red":
                #     self.reward += 3
                self.reward += 0.38

            if g == "shotgun":
                s += 1
                print(d.color, "Shotgun!")
                # if d.color == "Green":
                #     self.reward -= 2
                # elif d.color == "Yellow":
                #     self.reward -= 1.8
                # elif d.color == "Red":
                #     self.reward -= 1  # 1.6
                self.reward -= 0.29

            elif g == "footprint":
                numFootprints.append(d)
                # if d.color == "Green":
                #     self.reward += 0.38
                # elif d.color == "Red":
                #     self.reward -= 0.29
                print(d.color, "Footprint!")

        footprints = len(numFootprints)

        print("---   ---   ---")
        print("Total Brains:", b, " Total Shotguns:", s, " Total Footprints:", footprints)
        print("=== === ===")

        if (shotguns + s) >= 3:  # player lost
            self.loss += 1
            print("You have", shotguns + s, "shotguns, so you are dead!")
            print("Total number of brains is", brains, "\n")
            brains = brains
            shotguns = 0
            footprints = 0
            self.reward -= 1

        else:
            if brains + b >= 13:  # player won
                print("YOU WON", "\n")
                self.win += 1
                self.reward += 3
                done = True

            else:
                if action == 1:      # player choose to move to the next turn
                    shotguns += s
                    brains += b
                    # self.reward -= 0.1
                    print("Action  ======  1")
                    print("Same round. Draw 3 dices", "\n")
                else:           # player chose to stop its turn
                    brains += b
                    shotguns = 0
                    footprints = 0
                    # self.reward -= 0.1
                    print("Total number of brains for the next round is", brains, "\n")
                    print("Action  ======  2")
                    print("Next Round")

        print("Reward:", self.reward, "\n", "---   ---   ---")
        print("Wins:", self.win, "\n", "Losses:", self.loss)
        self.state = (brains, shotguns, footprints)

        return np.array(self.state), self.reward, done, {}

    def render(self):
        print("========== ========== ========== ========== ========== ========== ========== ========== ==========")

    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None

    # picks new dice with "footprints" if there are any
    def dicePicker(self, footprints):
        unrolled = []  # list
        rolled = []  # list
        pickedDice = []  # list of dice to be rolled

        # add footprints to list
        pickedDice = self.appendList(pickedDice, footprints)

        # populate the lists of rolled and unrolled
        for d in self.dice:
            if d.rolled:
                rolled.append(d)
                for i in footprints:
                    if i == d:
                        rolled.remove(i)
            else:
                unrolled.append(d)

        if len(unrolled) + len(footprints) >= 3:
            pickedDice = self.appendList(pickedDice, random.sample(unrolled, 3 - len(pickedDice)))
        else:
            pickedDice = self.appendList(pickedDice, unrolled)
            pickedDice = self.appendList(pickedDice, random.sample(rolled, 3 - len(pickedDice)))

            for j in self.dice:
                for k in pickedDice:
                    if j != k:
                        j.rolled = False

        return pickedDice

    # appends everything in y onto x
    def appendList(self, x, y):
        for i in y:
            x.append(i)
        return x


class Dice:
    sides = []
    color = "Green"
    rolled = False

    def __init__(self):
        pass

    def roll(self):
        pickedSide = random.choice(self.sides)
        self.rolled = True
        return pickedSide


class GreenDice(Dice):
    def __init__(self):
        self.sides = ["footprint",
                      "footprint",
                      "brain",
                      "brain",
                      "brain",
                      "shotgun"]
        self.color = "Green"


class YellowDice(Dice):
    def __init__(self):
        self.sides = ["footprint",
                      "footprint",
                      "brain",
                      "brain",
                      "shotgun",
                      "shotgun"]
        self.color = "Yellow"


class RedDice(Dice):
    def __init__(self):
        self.sides = ["footprint",
                      "footprint",
                      "brain",
                      "shotgun",
                      "shotgun",
                      "shotgun"]
        self.color = "Red"


