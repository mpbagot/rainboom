import pygame

import math
from time import time

from math_helper import *

#Initialise the constants
SCREEN_SIZE = (1200, 675)
# SCREEN_SIZE = (800, 450)
# the smaller this is, the bigger the fov (???)
CAMERA_DEPTH = 750
NEAR_CLIP = 0.001
FAR_CLIP = 20
FOV = math.radians(75)

FLAT = 0
SMOOTH_GOURAUD = 1
SMOOTH_PHONG = 2

SHADING_MODE = FLAT

HARD_OUTLINE = 3
NO_OUTLINE = 4

POLY_OUTLINE = HARD_OUTLINE

WIREFRAME = 5
WIREFRAME_DOTS = 6
SHADED = 7

RENDER_MODE = WIREFRAME

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

    def preRender(self):
        for g in range(len(self.scene.groups)):
            self.scene.groups[g].preRender(self)

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

    def preRender(self, cam):
        for p in range(len(self.polygons)):
            self.polygons[p].preRender(cam)

    def render(self, cam):
        for poly in self.polygons:
            poly.render(cam)

class Group:
    def __init__(self):
        self.objects = []

    def addObject(self, obj):
        self.objects.append(obj)

    def preRender(self, cam):
        for o in range(len(self.objects)):
            self.objects[o].preRender(cam)

    def render(self, cam):
        for obj in self.objects:
            obj.render(cam)

class NGon:
    def __init__(self, vertices, flipped=False, backCull=True):
        # Check the number of vertices
        if len(vertices) < 3:
            raise ValueError("Insufficient number of vertices.")
        elif len(vertices) == 3:
            print('Warning: 3 vertices used in N-gon. It is better to use a Triangle object instead.')

        self.vertices = vertices
        # Triangulate the quad
        self.tris = []
        n = len(vertices)
        for a in range((n-2)//2):
            self.tris += [
                            Triangle([vertices[b] for b in [a, -a-1, -a-2]], flipped, backCull),
                            Triangle([vertices[b] for b in [a, -a-2, abs(-a-2)-1]], flipped, backCull)
                         ]
        if (n-2)%2 == 1:
            a = (n-2)//2
            self.tris.append(Triangle([vertices[b] for b in [a, -a-1, -a-2]], flipped, backCull))

    def preRender(self, cam):
        '''
        Calculate all of the pre-render information
        '''
        for t in range(len(self.tris)):
            self.tris[t].preRender(cam)

    def render(self, cam):
        '''
        Render this shape to the screen
        '''
        for tri in self.tris:
            tri.render(cam)

class Quad(NGon):
    def __init__(self, vertices, flipped=False, backCull=True):
        if len(vertices) > 4:
            raise OverflowError('Too many vertices for a quad.')
        elif len(vertices) < 4:
            raise ValueError('Insufficient number of vertices.')
        super().__init__(vertices, flipped, backCull)

class Triangle:
    def __init__(self, vertices, flipped=False, backCull=True):
        self.vertices = vertices
        self.colour = [0, 255, 0]

        self.frameColour = list(self.colour)
        self.shouldRender = True

        self.flipNormal = flipped
        self.shouldCull = backCull

    def preRender(self, cam):
        '''
        Calculate all of the pre-render information
        '''
        for v in range(len(self.vertices)):
            self.vertices[v].preRender(cam)

        self.shouldRender = self.backFaceCull()
        if not self.shouldRender:
            return

        self.frameColour = self.getShadeColour(cam.scene.getLights())

    def render(self, cam):
        '''
        Render this triangle to the given camera's screen
        '''
        # TODO Somehow figure out how to render even if some points cannot be rendered, or are offscreen
        if not self.shouldRender:
            return

        # Get the colour to render the triangle with
        screenPoints = [vertex.screenPos for vertex in self.vertices]

        if RENDER_MODE == SHADED:
            # Render according to SHADING_MODE value
            try:
                if SHADING_MODE == FLAT:
                    pygame.draw.polygon(cam.screen, self.frameColour, screenPoints)
                elif SHADING_MODE == SMOOTH_GOURAUD:
                    pass
                elif SHADING_MODE == SMOOTH_PHONG:
                    pass
            except TypeError:
                pass

        # render hard edges on the polygon if option set
        if POLY_OUTLINE == HARD_OUTLINE or RENDER_MODE == WIREFRAME:
            if RENDER_MODE == WIREFRAME_DOTS:
                [vertex.render(cam) for vertex in self.vertices]

            try:
                pygame.draw.lines(cam.screen, (0, 0, 0), True, screenPoints, 3)
            except TypeError:
                pass

    def backFaceCull(self):
        '''
        Return whether or not this triangle has successfully escaped backface culling
        '''
        if not self.shouldCull:
            return True

        normal = self.getNormal()
        xthetaNormal = fixTan(normal[0], normal[2])

        poss = [vert.localPos for vert in self.vertices]

        # Average the three positions
        avgPos = [0, 0, 0]
        for i in range(3):
            value = sum([pos[i] for pos in poss])/len(poss)
            avgPos[i] = value

        xthetaCam = fixTan(avgPos[0], avgPos[2])

        diff = abs(xthetaCam-xthetaNormal)
        if diff > math.pi:
            diff = 2*math.pi-diff

        if diff > 5*math.pi/9:
            return False

        return True

    def getCentrePos(self):
        '''
        Get the 3D position of the centre of the triangle
        '''
        poss = [vert.pos for vert in self.vertices]

        # Average the three positions
        avgPos = [0, 0, 0]
        for i in range(3):
            value = sum([pos[i] for pos in poss])/len(poss)
            avgPos[i] = value

        return avgPos

    def getGlobalNormal(self):
        '''
        Get the normal vector of the triangle in global 3D space
        '''
        # Create the two vectors
        U = [self.vertices[1].pos[a]-self.vertices[0].pos[a] for a in range(3)]
        V = [self.vertices[2].pos[a]-self.vertices[0].pos[a] for a in range(3)]

        # Take the cross product
        normal = [U[(a+1)%3]*V[(a+2)%3] - U[(a+2)%3]*V[(a+1)%3] for a in range(3)]
        if self.flipNormal:
            normal = [-a for a in normal]
        return normal

    def getNormal(self):
        '''
        Get the normal vector of the triangle in cam/local 3D space
        '''
        # Create the two vectors
        U = [self.vertices[1].localPos[a]-self.vertices[0].localPos[a] for a in range(3)]
        V = [self.vertices[2].localPos[a]-self.vertices[0].localPos[a] for a in range(3)]

        # Take the cross product
        normal = [U[(a+1)%3]*V[(a+2)%3] - U[(a+2)%3]*V[(a+1)%3] for a in range(3)]
        if self.flipNormal:
            normal = [-a for a in normal]
        return normal

    def getShadeColour(self, lights):
        '''
        Get the flat shading colour of this triangle
        '''
        # Start with ambient light
        lightMult = list(AMBIENT_LIGHT_MULT)
        # TODO Get other lighting factors here
        # diffuse, specular, etc...
        for light in lights:
            centrePos = self.getCentrePos()
            power = light.calculateFalloff(centrePos)

            normal = self.getGlobalNormal()
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

        self.localPos = list(self.pos)
        self.screenPos = [0, 0]
        self.screenScale = 0
        self.shouldRender = True

    def preRender(self, cam):
        '''
        Run the pre-render calculations for the vertex
        '''
        # Get the local pos and perform a check
        self.localPos = self.getLocalPos(cam)
        if self.localPos[2] <= 0:
            self.shouldRender = False
            return

        dist = self.getDistance(cam)

        # Calculate the scale of the point
        self.screenScale = int((1-(dist/FAR_CLIP))*10) if dist < FAR_CLIP else 0

        # Project the 3D point to the 2D screen
        self.screenPos = self.projectPoint(self.localPos)

        # Get the distance and perform a check
        if NEAR_CLIP > dist or dist > FAR_CLIP:
            self.shouldRender = False
            return

        self.shouldRender = (0 < self.screenPos[0] < SCREEN_SIZE[0] and 0 < self.screenPos[1] < SCREEN_SIZE[1])

    def render(self, cam):
        '''
        Render this point to the given camera's screen
        '''
        if not self.shouldRender:
            return
        try:
            pygame.draw.circle(cam.screen, (0, 0, 0), self.screenPos, self.screenScale)
        except OverflowError:
            print('Scale:', self.screenScale)
            print('Screen Position:', [round(a, 2) for a in self.screenPos])

        return self.screenPos

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
        # z/x
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

        self.localPos = [x, y, z]

        return [x, y, z]
