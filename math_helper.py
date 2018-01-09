import math
import objects_3d
# from objects_3d import Vertex, Camera

def fixTan(opp, adj):
    if adj == 0:
        if opp > 0:
            return math.pi/2
        elif opp < 0:
            return -math.pi/2
        else:
            return 0
    result = math.atan(opp/adj)
    if adj > 0:
        # First quadrant, result is positive
        # Second quadrant, result is negative
        return result
    else:
        if opp < 0:
            # Third quadrant, result is positive
            return result - math.pi
        elif opp == 0:
            # 180 degrees
            return math.pi
        elif opp > 0:
            # Fourth Quadrant, result is negative
            return math.pi +result
    return 0

def getAngleNormalToLight(normal, normalPos, light):
    '''
    Get the angle between a given normal vector and a given light's position
    '''
    rotation = [0, 0, 0]

    # Find the rotation angles of the normal with respect to [0, 0, 0]
    rotation[0] = fixTan(normal[2], normal[0])-math.pi/2
    xzMag = math.sqrt(normal[2]**2+normal[0]**2)
    rotation[1] = math.atan(normal[1]/xzMag)

    tempVert = objects_3d.Vertex(light.pos)
    tempCam = objects_3d.Camera(normalPos, rotation, None)

    pos = tempVert.getLocalPos(tempCam)

    xyMag = math.sqrt(pos[1]**2+pos[0]**2)
    if xyMag < 0.0001:
        result = math.pi/2
    else:
        result = abs(fixTan(xyMag, pos[2]))

    print(result)

    if result > math.pi/2 or result < 0:
        return 0
    return math.pi/2-result
