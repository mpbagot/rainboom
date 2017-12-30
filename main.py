import pygame
import math
from time import sleep, time

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

    def renderPoints(self, points):
        start = time()
        # points2 = [getLocalPos(point, self) for point in points]
        # print(points2)
        for point in points:
            localPos = getLocalPos(point, self)
            if localPos[2] < 0:
                continue
            dist = getDistance(point, self)
            scale = int((1-(dist/RENDER_DISTANCE))*10) if dist < RENDER_DISTANCE else 0

            screenPos = projectPoint(localPos)
            try:
                if 0 < screenPos[0] < SCREEN_SIZE[0] and 0 < screenPos[1] < SCREEN_SIZE[1]:
                    pygame.draw.circle(screen, (0, 0, 0), screenPos, scale)
            except OverflowError:
                print('Scale:', scale)
                print('Screen Position:', [round(a, 2) for a in screenPos])
        self.fps = 1/(time()-start)

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

    if point[2] > 0:
        x = (SCREEN_SIZE[0]/2)+point[0]*CAMERA_DEPTH/point[2]
        y = (SCREEN_SIZE[1]/2)-point[1]*CAMERA_DEPTH/point[2]
    else:
        x = y = -999

    # print(x, y)
    return (int(x), int(y))

def getDistance(point, cam):
    point = [point[a]-cam.pos[a] for a in range(3)]
    dist = math.sqrt((point[0])**2+(point[1])**2+(point[2])**2)
    return dist

def fixTan(opp, adj):
    if adj == 0:
        if opp > 0:
            return math.pi/2
        elif opp < 0:
            return -math.pi/2
        else:
            return 0
    result = math.atan(opp/adj)
    if opp < 0:
        if adj < 0:
            # Third quadrant, result is positive
            return result - math.pi
        elif adj > 0:
            # Second quadrant, result is negative
            return result
    elif opp > 0:
        if adj > 0:
            # First quadrant, result is positive
            return result
        elif adj < 0:
            # Fourth Quadrant, result is negative
            return math.pi+result
    elif adj < 0:
        # 180 degrees
        return math.pi
    return 0

def getLocalPos(point, camera):
    vecMag = getDistance(point, camera)
    point = [point[a]-camera.pos[a] for a in range(3)]

    # Calculate the angles
    # x/z
    xtheta = fixTan(point[0], point[2])-camera.rot[0]
    # y/xzMag
    xzMag = math.sqrt(point[2]**2+point[0]**2)
    ytheta = fixTan(point[1], xzMag)-camera.rot[1]

    y = vecMag*math.sin(ytheta)

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
                # if abs(x*y*z)%16 == 0:
                # if x*z in [16, -16] or x*y in [16, -16] or z*y in [16, -16]:
                if abs(x) == 4 or abs(y) == 4 or abs(z) == 4:
                    points.append((x, y, z))

    # points = [(a, 0, 5) for a in range(-20, 20)]

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

        if pygame.time.get_ticks()%5000 < 10:
            print('Average FPS:', cam.fps)

        pygame.display.flip()
    clock.tick(60)
