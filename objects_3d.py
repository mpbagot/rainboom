import pygame

import math
from time import time

from math_helper import *

#Initialise the constants
SCREEN_SIZE = (1200, 675)
# SCREEN_SIZE = (800, 450)
# the smaller this is, the bigger the fov (???)
CAMERA_DEPTH = 750
RENDER_DISTANCE = 20
FOV = math.radians(75)

AMBIENT_LIGHT_MULT = [31, 31, 31]

class Camera:
    def __init__(self, pos, rot, screen):
        self.rot = rot
        self.pos = pos
        self.fps = 0
        self.screen = screen
        self.scene = None

    def setScene(self, scene):
        '''
        Set the scene to be rendered by this camera
        '''
        self.scene = scene

    def renderScene(self):
        '''
        Render the scene that this camera is set to render
        '''
        start = time()

        if self.scene is None:
            raise ValueError('The scene has not been set for this camera!')

        for group in self.scene.groups:
            group.render(self)

        self.fps = 1/(time()-start)

    def renderDebug(self):
        rot = [round(math.degrees(a), 2) for a in self.rot]
        pos = [round(a, 2) for a in self.pos]
        font = pygame.font.SysFont(None, 20)
        text = font.render("Rotation:"+str(rot), True, (0, 0, 255))
        self.screen.blit(text, [10, 10])
        text = font.render("Position:"+str(pos), True, (0, 0, 255))
        self.screen.blit(text, [10, 30])

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

class Scene:
    def __init__(self):
        self.groups = []
        self.lights = []

    def addGroup(self, group):
        if isinstance(group, Object):
            self.addObject(group)
            return
        self.groups.append(group)

    def addObject(self, obj):
        group = Group()
        group.addObject(obj)
        self.groups.append(group)

    def addLight(self, light):
        self.lights.append(light)
        return len(self.lights)-1

    def getLights(self):
        return self.lights

class Object:
    def __init__(self):
        self.polygons = []

    def addPolygon(self, poly):
        self.polygons.append(poly)

    def render(self, cam):
        for poly in self.polygons:
            poly.render(cam)

class Group:
    def __init__(self):
        self.objects = []

    def addObject(self, obj):
        self.objects.append(obj)

    def render(self, cam):
        for obj in self.objects:
            obj.render(cam)

class Triangle:
    def __init__(self, vertices):
        self.vertices = vertices
        self.colour = [0, 255, 0]

    def render(self, cam):
        '''
        Render this point to the given camera's screen
        '''
        # TODO Somehow figure out how to render even if some points cannot be rendered, or are offscreen

        # Get the colour to render the triangle with
        screenPoints = [vertex.render(cam) for vertex in self.vertices]

        try:
            pygame.draw.polygon(cam.screen, self.getShadeColour(cam.scene.getLights()), screenPoints)
        except TypeError:
            print(screenPoints)

        # TODO Add a flag for hard edges on polygons
        if False:
            pygame.draw.lines(cam.screen, (0, 0, 0), True, screenPoints, 3)

    def getCentrePos(self):
        '''
        Get the 3D position of the centre of the triangle
        '''
        poss = [vert.pos for vert in self.vertices]

        avgPos = [0, 0, 0]
        for i in range(3):
            value = sum([pos[i] for pos in poss])/len(poss)
            avgPos[i] = value

        return avgPos

    def getNormal(self):
        '''
        Get the normal vector of the triangle
        '''
        U = [self.vertices[1].pos[a]-self.vertices[0].pos[a] for a in range(3)]
        V = [self.vertices[2].pos[a]-self.vertices[0].pos[a] for a in range(3)]
        return [U[(a+1)%3]*V[(a+2)%3] - U[(a+2)%3]*V[(a+1)%3] for a in range(3)]

    def getShadeColour(self, lights):
        '''
        Get the flat shading colour of this triangle
        '''
        lightMult = list(AMBIENT_LIGHT_MULT)
        # TODO Get other lighting factors here
        # diffuse, specular, etc...
        for light in lights:
            centrePos = self.getCentrePos()
            power = light.calculateFalloff(centrePos)

            normal = self.getNormal()
            theta = getAngleNormalToLight(normal, centrePos, light)

            diffuse = power*math.sin(theta)
            lightMult = [lightMult[a]+diffuse*light.colour[a] for a in range(3)]

        lightMult = [a/255 for a in lightMult]

        shadeColour = [self.colour[channel]*(lightMult[channel]) for channel in range(len(self.colour))]

        return [min(channel, 255) for channel in shadeColour]

class Vertex:
    def __init__(self, x, y=0, z=0):
        if isinstance(x, list):
            self.pos = x
        else:
            self.pos = [x, y, z]

    def render(self, cam):
        '''
        Render this point to the given camera's screen
        '''
        localPos = self.getLocalPos(cam)
        if localPos[2] <= 0:
            return
        dist = self.getDistance(cam)
        if dist > RENDER_DISTANCE:
            return
        scale = int((1-(dist/RENDER_DISTANCE))*10) if dist < RENDER_DISTANCE else 0

        screenPos = self.projectPoint(localPos)
        try:
            if 0 < screenPos[0] < SCREEN_SIZE[0] and 0 < screenPos[1] < SCREEN_SIZE[1]:
                pygame.draw.circle(cam.screen, (0, 0, 0), screenPos, scale)
        except OverflowError:
            print('Scale:', scale)
            print('Screen Position:', [round(a, 2) for a in screenPos])

        return screenPos

    def projectPoint(self, localPos):
        '''
        Project a 3D point to the 2D screen space
        '''
        global CAMERA_DEPTH
        global SCREEN_SIZE

        x = (SCREEN_SIZE[0]/2)+localPos[0]*CAMERA_DEPTH/localPos[2]
        y = (SCREEN_SIZE[1]/2)-localPos[1]*CAMERA_DEPTH/localPos[2]

        return (int(x), int(y))

    def getDistance(self, cam):
        '''
        Get the distance of this point from the given camera
        '''
        point = [self.pos[a]-cam.pos[a] for a in range(3)]
        dist = math.sqrt((point[0])**2+(point[1])**2+(point[2])**2)
        return dist

    def getLocalPos(self, camera):
        '''
        Get a position for the point with respect to the camera
        '''
        point = [self.pos[a]-camera.pos[a] for a in range(3)]

        # Calculate the angle
        # x/z
        xtheta = fixTan(point[2], point[0])+camera.rot[0]
        # xzMag
        xzMag = math.sqrt(point[2]**2+point[0]**2)

        x = xzMag*math.cos(xtheta)
        point[2] = xzMag*math.sin(xtheta)

        # Calculate the other angle
        ytheta = fixTan(point[1], point[2])-camera.rot[1]

        zyMag = math.sqrt(point[2]**2+point[1]**2)

        y = zyMag*math.sin(ytheta)
        z = zyMag*math.cos(ytheta)

        return (x, y, z)
