import pygame

import math
from time import time

from objects_3d import Triangle

class Camera:
    def __init__(self, pos, rot, screen):
        self.rot = rot
        self.pos = pos
        self.fps = 0
        self.screen = screen
        self.scene = None
        self.sortedFaces = []
        self.tempFaces = []

    def setScene(self, scene):
        '''
        Set the scene to be rendered by this camera
        '''
        self.scene = scene

    def addFrameFace(self, face):
        '''
        Add a face to be rendered on this frame only
        Must be preRendered
        '''
        self.tempFaces.append(face)

    def preRender(self):
        for g in range(len(self.scene.groups)):
            self.scene.groups[g].preRender(self)

        self.sortedFaces = []
        for group in self.scene.groups:
            for obj in group.objects:
                self.sortedFaces += obj.polygons

        self.sortedFaces = sorted(self.sortedFaces+self.tempFaces, reverse=True)

        self.tempFaces = []

    def renderScene(self):
        '''
        Render the scene that this camera is set to render
        '''
        start = time()

        if self.scene is None:
            raise ValueError('The scene has not been set for this camera!')

        for face in self.sortedFaces:
            face.render(self)

        if time()-start:
            self.fps = 1/(time()-start)

    def renderDebug(self):
        rot = [round(math.degrees(a), 2) for a in self.rot]
        pos = [round(a, 2) for a in self.pos]
        font = pygame.font.SysFont(None, 20)
        text = font.render("Rotation:"+str(rot), True, (0, 0, 255))
        self.screen.blit(text, [10, 10])
        text = font.render("Position:"+str(pos), True, (0, 0, 255))
        self.screen.blit(text, [10, 30])

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

    def preRender(self, cam):
        for p in range(len(self.polygons)):
            self.polygons[p].preRender(cam)

class Group:
    def __init__(self):
        self.objects = []

    def addObject(self, obj):
        self.objects.append(obj)

    def preRender(self, cam):
        for o in range(len(self.objects)):
            self.objects[o].preRender(cam)
