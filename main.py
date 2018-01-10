import pygame
import math

from objects_3d import *

pygame.init()

if __name__ == "__main__":
    screen = pygame.display.set_mode(SCREEN_SIZE)

    scene = Scene()
    obj = Object()

    cams = [Camera([0, 0, 0], [0, 0, 0], screen), Camera([0, 5, 5], [-math.pi/2, -math.pi/2, 0], screen)]

    camIndex = False

    # Generate a cube of points
    points = []
    for z in range(-4, 5):
        for y in range(-4, 5):
            for x in range(-4, 5):
                if abs(x) == 4 or abs(y) == 4 or abs(z) == 4:
                    points.append(Vertex(x, y, z))

    points = [Vertex(a, 0, 5) for a in range(-20, 20)]

    # points = [Vertex(0, 5, 5), Vertex(5, -5, 5), Vertex(-5, -5, 5)]
    points = [Vertex(0, 0, 5), Vertex(0, 5, 5), Vertex(2.5, 7.5, 5), Vertex(5, 5, 5), Vertex(5, 0, 5)]
    # faces = [Triangle(points)]
    faces = [NGon(points)]

    for face in faces:
        obj.addPolygon(face)

    scene.addObject(obj)
    pLight = DirectionalLight([0, 0, 0], 1)
    lightPointer = scene.addLight(pLight)

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
        # Handle cam rotation
        if keys[pygame.K_d]:
            cams[int(camIndex)].rot[0] += 0.01
        elif keys[pygame.K_a]:
            cams[int(camIndex)].rot[0] -= 0.01
        if keys[pygame.K_w]:
            cams[int(camIndex)].rot[1] += 0.01
        elif keys[pygame.K_s]:
            cams[int(camIndex)].rot[1] -= 0.01

        # Handle basic cam motion
        if keys[pygame.K_UP]:
            cams[int(camIndex)].pos[2] += 0.01
        elif keys[pygame.K_DOWN]:
            cams[int(camIndex)].pos[2] -= 0.01
        if keys[pygame.K_RIGHT]:
            cams[int(camIndex)].pos[0] += 0.01
        if keys[pygame.K_LEFT]:
            cams[int(camIndex)].pos[0] -= 0.01

        if keys[pygame.K_l]:
            scene.lights[lightPointer].rot[0] += 0.01
        elif keys[pygame.K_o]:
            scene.lights[lightPointer].rot[0] -= 0.01

        if pygame.time.get_ticks()%5000 < 50:
            print('Current FPS:', cams[int(camIndex)].fps)

        pygame.display.flip()

        clock.tick(60)
