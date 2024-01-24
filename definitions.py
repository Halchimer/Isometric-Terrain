import pygame, os, sys
import random
import terraingen
import json
import builds
import threading
#variables definition -------------------------------------------------------------

size = width, height = 720, 720
bg = 0, 0, 0

CHUNK_SIZE = 8

spritesdef = [
	pygame.image.load(os.path.join('sprites/tiles', '0.png')),
	pygame.image.load(os.path.join('sprites/tiles', '1.png')),
	pygame.image.load(os.path.join('sprites/tiles', '2.png')),
	pygame.image.load(os.path.join('sprites/tiles', '3.png')),
	pygame.image.load(os.path.join('sprites/tiles', '4.png'))
]
shadowmap = pygame.image.load(os.path.join('sprites', 'shadowmap.png'))
shadowmap = pygame.transform.scale(shadowmap, (64, 64))

for i in range(len(spritesdef)):
	spritesdef[i] = pygame.transform.scale(spritesdef[i], (spritesdef[i].get_width()*4, spritesdef[i].get_height()*4))

clock = pygame.time.Clock()

#biomes vars
NOISEMAPVARIATION = 'noise'
RANDOMVARIATION = 'random'

#functions definition ---------------------------------------------------------------

def screen_to_grid(x: int, y: int) :
	return round((1/(2*32*16))*(x*16 + y*32 - player.posx*16 - player.posy*32)) , round((1/(2*32*16))*(x*-16 + y*32 + player.posx*16 - player.posy*32))

def screen_to_chunk(x : int, y : int):
	screentogrid = screen_to_grid(x,y)
	return screentogrid[0]//CHUNK_SIZE + screentogrid[0]%CHUNK_SIZE, screentogrid[1]//CHUNK_SIZE + screentogrid[1]%CHUNK_SIZE

def grid_to_screen(x : int, y : int, z:int) :
	return (x*(64/2)+y*(64/-2))+(64*16)/2, (x*(64/4)+y*(64/4) - (z*4))

def split_tile_data(datastring) : 
	return datastring.split(',')

def clamp_value(minval : int | float, maxval : int | float, value : int | float):
	return max(minval, min(maxval, value))
#class definition -----------------------------------------------------------------------

#game events permet de récupérer des infos provenant du monde et d'y accéder depuis d'autres classes et structures
class game_events :
	events_list = []
	def events_reset():
		game_events.events_list = []

class player :
	posx, posy = 0, 0

	def inputs():
		#gère les entrées du joueur et ajoute au gamme-events l'évenement "moving"
		move_ticker = 0
		keys=pygame.key.get_pressed()
		if keys[pygame.K_q]:
			if move_ticker == 0:
				move_ticker = 10
				player.posx+=0.2*clock.get_time()
				if not 'moving' in game_events.events_list : game_events.events_list.append('moving')
		if keys[pygame.K_d]:
			if move_ticker == 0:   
				move_ticker = 10     
				player.posx-=0.2*clock.get_time()
				if not 'moving' in game_events.events_list : game_events.events_list.append('moving')
		if keys[pygame.K_z]:
			if move_ticker == 0:   
				move_ticker = 10     
				player.posy+=0.2*clock.get_time()
				if not 'moving' in game_events.events_list : game_events.events_list.append('moving')
		if keys[pygame.K_s]:
			if move_ticker == 0:   
				move_ticker = 10     
				player.posy-=0.2*clock.get_time()
				if not 'moving' in game_events.events_list : game_events.events_list.append('moving')
		if keys[pygame.K_ESCAPE]:
			if move_ticker == 0:   
				move_ticker = 10     
				sys.exit()



#chunk est une classe qui gère les morceaux de terrain, composés de 8 par 8 tuiles
class chunk :
	__slots__ = ('pos','tiles','screenpos','tilesframe','chunkrendered', 'tilesTexturesBuffer')
	def __init__(self, pos : tuple[int, int, int]):
		self.pos = pos
		self.tiles = [f'{x},{y},{terraingen.getheight(self.pos[0]*CHUNK_SIZE + x,self.pos[1]*CHUNK_SIZE + y)},{1 if terraingen.getheight(self.pos[0]*CHUNK_SIZE + x,self.pos[1]*CHUNK_SIZE + y) < -3 else builds.biomes[clamp_value(0,len(builds.biomes)-1,terraingen.getbiome(self.pos[0]*CHUNK_SIZE + x,self.pos[1]*CHUNK_SIZE + y))].gensurfacemap()},0' for y in range(8) for x in range(8)]
		self.screenpos = (0,0)
		
		'''for i in range(len(self.tiles)) :
			self.tiles[i] += str(random.randint(0, spritesdef[int(self.tiles[i].split(',')[3])].get_height()/64-1)) '''

		#ici, on fait un prérendu des chunks, puisque ceux ci ne sont pas rendus à chaque frame (ils doivent donc être updatés pour modif)
		self.prerender()

	def getTileTexture(self):
		self.tilesframe.fill((0, 0, 0, 0))
		self.tilesframe.blit(spritesdef[int(tile.split(',')[3])], (0, -int(tile.split(',')[4])*64))
		self.tilesframe.blit(shadowmap, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
		self.tilesTexturesBuffer.append((self.tilesframe, grid_to_screen((int(tile.split(',')[0])),(int(tile.split(',')[1])),(int(tile.split(',')[2])))))
	def prerender (self):
		#cette fonction permet de combiner les textures de tous les objets du chunk en une seule surface
		#cela permet de ne faire qu'un appel au GPU par chunk au lieu d'en faire 64 par chunk (1 par tuile)

		self.tilesframe = pygame.Surface((64, 64), pygame.SRCALPHA).convert_alpha()
		self.chunkrendered = pygame.Surface((64*CHUNK_SIZE*2, 80*CHUNK_SIZE*4), pygame.SRCALPHA).convert_alpha() 
		self.chunkrendered.fill((0, 0, 0, 0))
		self.tilesTexturesBuffer = []

		for tile in self.tiles :
			self.tilesframe.fill((0, 0, 0, 0))
			self.tilesframe.blit(spritesdef[int(tile.split(',')[3])], (0, -int(tile.split(',')[4])*64))
			self.tilesframe.blit(shadowmap, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
			self.tilesTexturesBuffer.append((self.tilesframe, grid_to_screen((int(tile.split(',')[0])),(int(tile.split(',')[1])),(int(tile.split(',')[2])))))

		
		self.chunkrendered.blits(self.tilesTexturesBuffer)
	
	def render(self, screen):
		#cette fonction affiche le chunk (sachant que le rendu de chaque tuile est déjà stocké en mémoir, il n'y à plus qu'à afficher le tout)
		
		self.screenpos = (((self.pos[0]*CHUNK_SIZE)*(64/2)+(self.pos[1]*CHUNK_SIZE)*(64/-2))+player.posx, ((self.pos[0]*CHUNK_SIZE)*(64/4)+(self.pos[1]*CHUNK_SIZE)*(64/4)+player.posy))
		return (self.chunkrendered, self.screenpos)

	def get_tile_info(self, xoffset, yoffset):
		tile = split_tile_data(self.tiles[yoffset*CHUNK_SIZE + xoffset])
		return {'x' : tile[0], 'y' : tile[1], 'h' : tile[2], 'tile' : tile[3]}
	
	def modify_tile_data(self,tileoffset, newtiledata) :
		self.tiles[tileoffset[1]*CHUNK_SIZE + tileoffset[0]] = ','.join(map(str,newtiledata))
		self.prerender()
		

#les éléments d'interface utilisateur en jeu
class ui_element :
	def __init__(self, spriteatlas, static : bool = False, snap_to_grid : bool = False) :
		pass



