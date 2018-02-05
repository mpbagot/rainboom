from objects_3d import AMBIENT_LIGHT_MULT
from math_helper import *

class Material:
    def __init__(self):
        self._diffuse = NullShader()
        self._specular = NullShader()
        self._emission = NullShader()

        self.isEmissive = False

        self.shaders = {'diffuse' : self._diffuse,
                        'specular' : self._specular,
                        'emission' : self._emission
                        }

    def setShader(self, shaderType, shader):
        if shaderType not in self.shaders:
            print('[Warning] Shader type is invalid. This shader will not be used.')
            return
        self.shaders[shaderType] = shader

    def isColour(self):
        return not self._diffuse.useImage()

    def getColour(self, poly, lights):
        polyColour = self.shaders.get('diffuse').colour
        # Start with ambient light
        lightMult = list(AMBIENT_LIGHT_MULT)

        # Diffuse is colour, return normal colour
        factor = self.shaders.get('diffuse').getLightMult(poly, lights)

        polyColour = [polyColour[a]*min(lightMult[a]+factor[a], 255)/255 for a in range(3)]
        # Specular is additive, adds to colour.
        factor = self.shaders.get('specular').getLightMult(poly, lights)
        polyColour = [polyColour[a]+factor[a] for a in range(3)]
        # Emission doesn't modify poly colour, only produces colour/light

        return polyColour

class NullShader:
    def getLightMult(self, poly, lights):
        return [0, 0, 0]

class DiffuseShader:
    def __init__(self, colour=[0, 0, 0]):
        self.colour = colour
        self.image = None

    def useImage(self):
        return bool(self.image)

    def getLightMult(self, poly, lights):
        lightMult = [0, 0, 0]

        for light in lights:
            centrePos = poly.getGlobalCentrePos()
            power = light.calculateFalloff(centrePos)

            normal = poly.getGlobalNormal()
            theta = getAngleNormalToLight(normal, centrePos, light)

            diffuse = power*math.sin(theta)
            lightMult = [lightMult[a]+diffuse*light.colour[a] for a in range(3)]

        return lightMult

class SpecularShader:
    def getLightMult(self, poly, lights):
        return [0, 0, 0]
