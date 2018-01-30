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

def normalise(vector):
    '''
    Normalise a vector
    '''
    mag = math.sqrt(sum([a**2 for a in vector]))
    return [a/mag for a in vector]

def getAngleNormalToLight(normal, normalPos, light):
    '''
    Get the angle between a given normal vector and a given light's position
    '''
    # Get the position of the light
    lightPos = light.getPos(normalPos)
    lightVec = normalise([normalPos[a]-lightPos[a] for a in range(3)])
    normalVec = normalise(normal)

    return max(math.pi/2-math.acos(sum([lightVec[a]*normalVec[a] for a in range(3)])), 0)

def getAngleBetween(vector1, vector2):
    vec1 = normalise(vector1)
    vec2 = normalise(vector2)
    return math.acos(sum([vec1[a]*vec2[a] for a in range(3)]))
