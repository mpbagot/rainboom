import math

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

def getAngleNormalToLight(normal, light):
    result = 0
    if abs(result) < 0:
        return 0
    elif abs(result) > math.pi:
        return math.pi
    return result
