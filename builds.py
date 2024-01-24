import json
import random
import terraingen

class biomebuild :
    def __init__(self, biomedatapath : str):
        with open(biomedatapath, 'r') as file:
            self.data = json.loads(file.read())
            self.surfacevariationmode = self.data['surface']['variation_mode']
            self.surfacematerials = self.data['surface']['surface_tiles']

    def gensurfacemap(self, posx:int=0, posy:int=0) :
        if self.surfacevariationmode == 'random' :
            return random.choice(self.surfacematerials)
        elif self.surfacevariationmode == 'noise' :
            return self.surfacematerials[max(0, min(len(self.surfacematerials)-1,terraingen.getdeconoise(posx, posy)))]
        elif self.surfacevariationmode == 'none' :
            return self.surfacematerials[0]
        else :
            return 0
    
            
	
biomes = (
	biomebuild('biomes/plain.biome.json'),
    biomebuild('biomes/deso.biome.json')
)