import pygame

import math
from time import time

from math_helper import *

class PointLight:
    def __init__(self, pos, power):
        self.power = power
        self.pos = pos
        self.colour = [255, 255, 255]

    def setBrightness(self, power):
        self.power = power

    def setColour(self, colour):
        self.colour = colour

    def getPos(self, otherPos):
        return self.pos

    def calculateFalloff(self, otherPos):
        '''
        Calculate the light level at a given position based on falloff
        '''
        dist = math.sqrt(sum([(otherPos[a]-self.pos[a])**2 for a in range(len(otherPos))]))
        if dist == 0:
            return 999999
        return self.power/(dist**2)

class DirectionalLight(PointLight):
    def __init__(self, rot, power):
        super().__init__([0, 0, 0], power)
        self.rot = rot

    def getPos(self, otherPos):
        calcPos = [0, 0, 0]

        calcPos[0] = 10*math.cos(self.rot[0])
        calcPos[2] = 10*math.sin(self.rot[0])
        calcPos[1] = 10*math.tan(self.rot[1])

        return [otherPos[a]-calcPos[a] for a in range(3)]

    def calculateFalloff(self, otherPos):
        '''
        Return the light brightness because it's the same regardless of position
        '''
        return self.power
