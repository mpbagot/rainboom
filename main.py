import pygame
import math
from time import sleep, time

from math_helper import fixTan

#Initialise the constants
SCREEN_SIZE = (1200, 675)
# SCREEN_SIZE = (800, 450)
# the smaller this is, the bigger the fov (???)
CAMERA_DEPTH = 750
RENDER_DISTANCE = 20
FOV = math.radians(75)

pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE)

class Camera:
    def __init__(self, pos, rot):
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
            # localPos = point.getLocalPos(self)
            # if localPos[2] <= 0:
            #     continue
            # dist = point.getDistance(self)
            # if dist > RENDER_DISTANCE:
            #     continue
            # scale = int((1-(dist/RENDER_DISTANCE))*10) if dist < RENDER_DISTANCE else 0
            #
            # screenPos = point.projectPoint(localPos)
            # try:
            #     if 0 < screenPos[0] < SCREEN_SIZE[0] and 0 < screenPos[1] < SCREEN_SIZE[1]:
            #         pygame.draw.circle(screen, (0, 0, 0), screenPos, scale)
            # except OverflowError:
            #     print('Scale:', scale)
            #     print('Screen Position:', [round(a, 2) for a in screenPos])
        self.fps = 1/(time()-start)

    def renderDebug(self):
        rot = [round(math.degrees(a), 2) for a in self.rot]
        pos = [round(math.degrees(a), 2) for a in self.pos]
        font = pygame.font.SysFont(None, 20)
        text = font.render("Rotation:"+str(rot), True, (0, 0, 255))
        screen.blit(text, [10, 10])
        text = font.render("Position:"+str(pos), True, (0, 0, 255))
        screen.blit(text, [10, 30])

class Scene:
    def __init__(self):
        self.groups = []

    def addGroup(self, group):
        if isinstance(group, Object):
            self.addObject(group)
            return
        self.groups.append(group)

    def addObject(self, obj):
        group = Group()
        group.addObject(obj)
        self.groups.append(group)

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

    def render(self, cam):
        '''
        Render this point to the given camera's screen
        '''
        screenPoints = [vertex.render(cam) for vertex in self.vertices]

        for a in range(len(screenPoints)):
            pygame.draw.line(cam.screen, (0, 0, 0), screenPoints[a], screenPoints[(a+1)%len(screenPoints)], 3)

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

if __name__ == "__main__":
    scene = Scene()
    obj = Object()

    cams = [Camera([0, 0, 0], [0, 0, 0]), Camera([0, 5, 5], [-math.pi/2, -math.pi/2, 0])]

    camIndex = False

    # Generate a cube of points
    points = []
    for z in range(-4, 5):
        for y in range(-4, 5):
            for x in range(-4, 5):
                if abs(x) == 4 or abs(y) == 4 or abs(z) == 4:
                    points.append(Vertex(x, y, z))

    points = [Vertex(a, 0, 5) for a in range(-20, 20)]

    points = [Vertex(0, 5, 5), Vertex(5, -5, 5), Vertex(-5, -5, 5)]
    faces = [Triangle(points)]

    for face in faces:
        obj.addPolygon(face)

    scene.addObject(obj)

    cams[0].setScene(scene)
    cams[1].setScene(scene)

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    camIndex = not camIndex

        screen.fill((255, 255, 255))
        cams[int(camIndex)].renderScene()
        cams[int(camIndex)].renderDebug()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            cams[int(camIndex)].rot[0] += 0.01
        elif keys[pygame.K_a]:
            cams[int(camIndex)].rot[0] -= 0.01
        if keys[pygame.K_w]:
            cams[int(camIndex)].rot[1] += 0.01
        elif keys[pygame.K_s]:
            cams[int(camIndex)].rot[1] -= 0.01

        if pygame.time.get_ticks()%5000 < 50:
            print('Average FPS:', cams[int(camIndex)].fps)

        pygame.display.flip()

        clock.tick(60)
