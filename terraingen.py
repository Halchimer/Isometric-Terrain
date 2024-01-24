import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise
import random
import opensimplex

seed = random.randint(0, 99999999)
biomeseed = seed*2
print(f'seed : {seed}\nbiome seed : {biomeseed}')
opensimplex.seed(seed)

'''
noise = PerlinNoise(octaves=25, seed=seed)
xpix, ypix = 100, 100
pic = [[noise([i/xpix, j/ypix]) for j in range(xpix)] for i in range(ypix)]'''


biomenoise = PerlinNoise(octaves=2, seed = biomeseed)
biomexpix, biomeypix = 100,100
biomepic = [[biomenoise([i/biomexpix, j/biomeypix]) for j in range(biomexpix)] for i in range(biomeypix)]

deconoise = PerlinNoise(octaves=32, seed = biomeseed)
decoxpix, decoypix = 100,100
decopic = [[deconoise([i/decoxpix, j/decoypix]) for j in range(decoxpix)] for i in range(decoypix)]


def getheight(xpos : int, ypos : int) :
	return int(opensimplex.noise2(xpos/5, ypos/5)*20)

def getbiome(xpos:int, ypos : int) :
	return int(opensimplex.noise2(xpos/5, ypos/5)*20)

def getdeconoise(xpos:int, ypos : int) :
	return int(opensimplex.noise2(xpos/5, ypos/5)*20)
