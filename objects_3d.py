import pygame

import math
from time import time
from copy import deepcopy

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

POLY_OUTLINE = NO_OUTLINE

WIREFRAME = 5
WIREFRAME_DOTS = 6
SHADED = 7

RENDER_MODE = SHADED

AMBIENT_LIGHT_MULT = [31, 31, 31]

class Primitive:
    def __lt__(self, other):
        if isinstance(other, Primitive):
            return self.getCentrePos()[2] < other.getCentrePos()[2]
        else:
            return True

    def getCentrePos(self):
        '''
        Get the 3D position of the centre of the N-Gon in local space
        '''
        poss = [vert.localPos for vert in self.vertices]

        # Average the three positions
        avgPos = [0, 0, 0]
        for i in range(3):
            value = sum([pos[i] for pos in poss])/len(poss)
            avgPos[i] = value

        return avgPos

    def getGlobalCentrePos(self):
        '''
        Get the 3D position of the centre of the N-Gon in local space
        '''
        poss = [vert.pos for vert in self.vertices]

        # Average the three positions
        avgPos = [0, 0, 0]
        for i in range(3):
            value = sum([pos[i] for pos in poss])/len(poss)
            avgPos[i] = value

        return avgPos

class NGon(Primitive):
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

class Line(Primitive):
    def __init__(self, vertices):
        self.vertices = vertices

    def preRender(self, cam):
        for v in range(len(self.vertices)):
            self.vertices[v].preRender(cam)

    def render(self, cam):
        for vertex in self.vertices:
            vertex.render(cam)

        pygame.draw.lines(cam.screen, (0, 0, 0), True, [v.screenPos for v in self.vertices], 3)

class Triangle(Primitive):
    def __init__(self, vertices, flipped=False, backCull=True):
        self.vertices = deepcopy(vertices)
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

        # Check if any point is behind z=0
        lessZ = [a.localPos[2] < 0 for a in self.vertices]
        if any(lessZ) and not all(lessZ):
            # Scale it to z=NEAR_CLIP
            less = [v for v, vert in enumerate(self.vertices) if vert.localPos[2] < 0]
            great = [v for v in range(3) if v not in less]
            for lIn in less:
                lPos = self.vertices[lIn].localPos
                lPosses = []
                for gIn in great:
                    gPos = self.vertices[gIn].localPos
                    # Calculate the vector between the two points
                    vector = [gPos[a] - lPos[a] for a in range(3)]
                    # Calculate the scale ratio
                    zRatio = abs((gPos[2]-NEAR_CLIP*1.5)/vector[2])
                    # Scale the vector
                    vector = [a*zRatio for a in vector]
                    # Calculate and set the position
                    pos = [gPos[a]-vector[a] for a in range(3)]

                    # Get the offscreen point's position and the onscreen point's position for scaling
                    screenPos = list(Vertex.projectPoint(pos))
                    onscreenPos = Vertex.projectPoint(self.vertices[gIn].localPos)

                    # Determine the correct ratio to use
                    ratio = 1
                    testX = screenPos[0] != onscreenPos[0]
                    testY = screenPos[1] != onscreenPos[1]

                    if testX and screenPos[0] > SCREEN_SIZE[0]:
                        ratio = (SCREEN_SIZE[0]-onscreenPos[0])/(screenPos[0]-onscreenPos[0])
                    elif testX and screenPos[0] < 0:
                        ratio = onscreenPos[0]/(screenPos[0]-onscreenPos[0])
                    elif testY and screenPos[1] > SCREEN_SIZE[1]:
                        ratio = (SCREEN_SIZE[1]-onscreenPos[1])/(screenPos[1]-onscreenPos[1])
                    elif testY and screenPos[1] < 0:
                        ratio = onscreenPos[1]/(screenPos[1]-onscreenPos[1])

                    ratio = abs(ratio)

                    # Scale the screen position if the position is actually offscreen, otherwise, just leave it
                    # if not (0 < screenPos[a] < SCREEN_SIZE[a]) else screenPos[a]
                    screenPos = [int((screenPos[a]-onscreenPos[a])*ratio+onscreenPos[a]) for a in (0, 1)]
                    lPosses.append(tuple(screenPos))

                if len(lPosses) == 2:
                    # Construct the quad as required using lPosses
                    vPos = [tuple(lPosses[0]), tuple(lPosses[1]), tuple(self.vertices[great[1]].screenPos)]
                    vertices = [Vertex([0, 0, 0]) for a in vPos]

                    # Set the screen positions for the vertices
                    for v in range(len(vertices)):
                        vertices[v].screenScale = 1
                        # Project the 3D point to the 2D screen
                        vertices[v].screenPos = vPos[v]

                    # Duplicate this triangle, but replace the vertices
                    t = Triangle.fromExisting(self, vertices)
                    cam.addFrameFace(t)

                # Set the screenPos
                self.vertices[lIn].screenPos = tuple(lPosses[0])

        self.shouldRender = self.backFaceCull()
        if not self.shouldRender:
            return

        self.frameColour = self.getShadeColour(cam.scene.getLights())

    def render(self, cam):
        '''
        Render this triangle to the given camera's screen
        '''
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
        if POLY_OUTLINE == HARD_OUTLINE or RENDER_MODE in [WIREFRAME, WIREFRAME_DOTS]:
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

        if diff > 0.51*math.pi:
            return False

        return True

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
            centrePos = self.getGlobalCentrePos()
            power = light.calculateFalloff(centrePos)

            normal = self.getGlobalNormal()
            theta = getAngleNormalToLight(normal, centrePos, light)

            diffuse = power*math.sin(theta)
            lightMult = [lightMult[a]+diffuse*light.colour[a] for a in range(3)]

        lightMult = [a/255 for a in lightMult]

        shadeColour = [self.colour[channel]*(lightMult[channel]) for channel in range(len(self.colour))]

        return [min(channel, 255) for channel in shadeColour]

    @staticmethod
    def fromExisting(triangle, vertices):
        t = Triangle(vertices)
        t.frameColour = triangle.frameColour
        t.shouldCull = triangle.shouldCull
        return t

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
        self.screenPos = Vertex.projectPoint(self.localPos)

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

    @staticmethod
    def projectPoint(localPos):
        '''
        Project a 3D point to the 2D screen space
        '''
        global CAMERA_DEPTH
        global SCREEN_SIZE

        if localPos[2] == 0:
            return (-50, -50)

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
        # Translate the position
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
