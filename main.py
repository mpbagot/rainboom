import pygame
import math
from time import sleep

#Initialise the constants
SCREEN_SIZE = (1200, 675)
# the smaller this is, the bigger the fov (???)
CAMERA_DEPTH = 512
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
            pygame.draw.circle(screen, (0, 0, 0), screenPos, scale)

    def renderInfo(self):
        font = pygame.font.SysFont(None, 20)
        text = font.render("Rotation:"+str(self.rot), True, (0, 0, 255))
        screen.blit(text, [10, 10])
        text = font.render("Position:"+str(self.pos), True, (0, 0, 255))
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

def getLocalPos(point, camera):
    vecMag = getDistance(point, camera)
    point = [point[a]-camera.pos[a] for a in range(3)]

    camThetas = list(camera.rot[:-1])

    # Break out if the point has z of 0
    if point[2] == 0:
        return (-5, -5, -5)

    # Calculate the angles
    # x/z
    xtheta = math.atan(point[0]/point[2])
    # y/xzMag
    ytheta = math.atan(point[1]/math.sqrt(point[2]**2+point[0]**2))

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
                if z in [-4, 4] or y in [-4, 4] or x in [-4, 4]:
                    points.append((x, y, z))
                    # if z%2 == 0 and y%2 == 0 and x%2 == 0:

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pass
                # if event.key == pygame.K_w:
                #     cam.pos[2] += 1

        screen.fill((255, 255, 255))
        cam.renderPoints(points)
        cam.renderInfo()

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
