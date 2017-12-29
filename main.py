import pygame
import math
from time import sleep

#Initialise the constants
SCREEN_SIZE = (1200, 675)
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

    def renderPoints(self, points):
        for point in points:
            localPos = getLocalPos(point, self)
            dist = getDistance(point, self)
            scale = int((1-(dist/RENDER_DISTANCE))*10) if dist < RENDER_DISTANCE else 0

            screenPos = projectPoint(localPos)
            try:
                pygame.draw.circle(screen, (0, 0, 0), screenPos, scale)
            except OverflowError:
                print('Scale:', scale)
                print('Screen Position:', [round(a, 2) for a in screenPos])

    def renderDebug(self):
        rot = [round(math.degrees(a), 2) for a in self.rot]
        pos = [round(math.degrees(a), 2) for a in self.pos]
        font = pygame.font.SysFont(None, 20)
        text = font.render("Rotation:"+str(rot), True, (0, 0, 255))
        screen.blit(text, [10, 10])
        text = font.render("Position:"+str(pos), True, (0, 0, 255))
        screen.blit(text, [10, 30])

def projectPoint(point):
    global CAMERA_DEPTH
    global SCREEN_SIZE

    # print(point)

    if point[2] > 0:
        x = (SCREEN_SIZE[0]/2)+point[0]*CAMERA_DEPTH/point[2]
        y = (SCREEN_SIZE[1]/2)+point[1]*CAMERA_DEPTH/point[2]
    else:
        x = y = -999

    # print(x, y)
    return (int(x), int(y))

def getDistance(point, cam):
    point = [point[a]-cam.pos[a] for a in range(3)]
    dist = math.sqrt((point[0])**2+(point[1])**2+(point[2])**2)
    return dist

def fixTan(result, opp, adj):
    if opp < 0:
        if adj < 0:
            # Third quadrant, result is positive
            return math.pi - result
        elif adj > 0:
            # Second quadrant, result is negative
            return result
        else:
            # 180 degrees
            return math.pi
    elif opp > 0:
        if adj > 0:
            # First quadrant, result is positive
            return result
        elif adj < 0:
            # Fourth Quadrant, result is negative
            return math.pi+result
    else:
        if adj > 0:
            # 0 degrees
            return 0
        elif adj < 0:
            # 180 degrees
            return math.pi
        else:
            return 0

def getLocalPos(point, camera):
    vecMag = getDistance(point, camera)
    point = [point[a]-camera.pos[a] for a in range(3)]

    camThetas = list(camera.rot[:-1])

    # Break out if the point has z of 0
    if point[2] == 0:
        return (-5, -5, -5)

    # Calculate the angles
    # TODO Adjust the angles for the different quadrants
    # x/z
    xtheta = fixTan(math.atan(point[0]/point[2]), point[0], point[2])
    # y/xzMag
    ytheta = fixTan(math.atan(point[1]/math.sqrt(point[2]**2+point[0]**2)), point[1], math.sqrt(point[2]**2+point[0]**2))

    xtheta, ytheta = [xtheta-camThetas[0], ytheta-camThetas[1]]

    y = -vecMag*math.sin(ytheta)

    m = math.sqrt(vecMag**2-y**2)
    x = m*math.sin(xtheta)
    z = m*math.cos(xtheta)
    return (x, y, z)

if __name__ == "__main__":
    cam = Camera([0, 0, 0], [0, 0, 0])
    points = [(30, 30, 30), (10, 10, 10), (5, 5, 5), (0, 0, 20)]
    points = [(0, 0, 5), (5, 0, 5), (-5, 0, 5), (3, 0, 3), (-3, 0, 3), (0, 5, 5)]
    # Generate a cube of points
    points = []
    for z in range(-4, 5):
        for y in range(-4, 5):
            for x in range(-4, 5):
                if x*z in [16, -16] or x*y in [16, -16] or z*y in [16, -16]:
                    points.append((x, y, z))

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pass

        screen.fill((255, 255, 255))
        cam.renderPoints(points)
        cam.renderDebug()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            cam.rot[0] += 0.005
        elif keys[pygame.K_a]:
            cam.rot[0] -= 0.005
        if keys[pygame.K_w]:
            cam.rot[1] += 0.005
        elif keys[pygame.K_s]:
            cam.rot[1] -= 0.005


        pygame.display.flip()
    clock.tick(60)
