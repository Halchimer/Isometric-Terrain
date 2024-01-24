import pygame, os, sys
from definitions import *
import random
import math
import builds
import time
import pickle

pygame.init()

screen = pygame.display.set_mode(size)

class mainapp :
	def __init__(self) :
		self.chunks = []

		self.threads = []

		self.debug_font = pygame.font.SysFont(None, 24)

		self.serializedChunksBuffer = {}
		self.renderBuffer = []

	def renderscreen(self) :
		screen.fill(bg)

		self.renderBuffer = [chunk.render(screen) for chunk in sorted(self.chunks, key=lambda x: x.pos, reverse=False)]
			
		screen.blits(self.renderBuffer)

		devinfo = self.debug_font.render(f'DEBUG MENU',  True, (255, 255, 255))
		screen.blit(devinfo, (0, 0))
		devinfo = self.debug_font.render(f'Deltatime : {clock.get_time()}ms | FPS : {clock.get_fps()}',  True, (255, 255, 255))
		screen.blit(devinfo, (0, 24))
		devinfo = self.debug_font.render(f'Chunks : {len(self.chunks)} | Tiles : {len(self.chunks)* 8**2}',  True, (255, 255, 255))
		screen.blit(devinfo, (0, 48))
		return 1
	
	def deleteChunks(self):
		for chunk in self.chunks :
				chunkpos = chunk.pos
				chunkscreenpos = chunk.screenpos

				if chunkscreenpos[0] > -64*12 and chunkscreenpos[0] < width-64*4 and chunkscreenpos[1] < height and chunkscreenpos[1] > -64*4:
					pass
				else :
					self.chunks.remove(chunk)

	def generatePeripheralChunks(self):
		origineToChunk = screen_to_chunk(0, 0)
		self.chunks += [chunk((origineToChunk[0]-x, origineToChunk[1]+y)) for x in range(2) for y in range(2) if not any(element.pos == (origineToChunk[0]+x, origineToChunk[1]+y) for element in self.chunks)]

	def gameloop(self):
		self.deleteChunks()
		self.generatePeripheralChunks()
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT: sys.exit()
			player.inputs()
		
			self.threads.append(threading.Thread(target=self.renderscreen))
			if 'moving' in game_events.events_list :
				self.threads.append(threading.Thread(target=self.generatePeripheralChunks))
				self.threads.append(threading.Thread(target=self.deleteChunks))

			for thread in self.threads : 
				thread.start()
				thread.join()
			self.threads = []
			game_events.events_reset()

			clock.tick()
			pygame.display.flip()

	

if __name__ == '__main__' :
	instance = mainapp()
	instance.gameloop()