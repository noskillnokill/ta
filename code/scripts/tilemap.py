import pygame
import json
import sys
import math
from scripts.entities import Player

AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

NEIGHTBOR_OFFSETS = [(-1, 0), (-1, 1), (-1, -1), (1, 0), (1, -1), (1, 1), (0, 0), (0, -1), (0, 1)]

PHYSICS_TILES = {'0', '1', '2'}
AUTOTILE_TYPES = {'grass', 'stone', 'dirt'}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        self.Player = Player(game=game, pos=(0, 0), size=(0, 0))

    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['tile'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]
        return matches


    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHTBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']


        
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects
    
    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]


        
    def render(self, surf, offset=(0, 0)):
        # Render off-grid tiles
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        # Calculate the center of the screen
        center_x = (offset[0]) + surf.get_width() // 2
        center_y = (offset[1]) + surf.get_height() // 2
        # Define the radius of the circle
        circle_radius_tiles = self.Player.lightlevel_value
         # Adjust this value as needed

        # Iterate over the tile positions and check if they are within the circular region
        for tile_x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for tile_y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                # Calculate the center of the current tile
                tile_center_x = tile_x * self.tile_size + self.tile_size // 2
                tile_center_y = tile_y * self.tile_size + self.tile_size // 2




                # Check if the tile is within the circle based on its position relative to the center
                if (tile_center_x - center_x)**2 + (tile_center_y - center_y)**2 <= (circle_radius_tiles * self.tile_size)**2:
                    loc = str(tile_x) + ';' + str(tile_y)

                    # Check if the current position is in the tilemap
                    if loc in self.tilemap:
                        # Check if the position to the left of the current tile is not in the tilemap or if it's empty
                        left_loc = str(tile_x + 1) + ';' + str(tile_y)
                        left_empty = left_loc not in self.tilemap or not self.tilemap[left_loc]

                        # Check if the position to the right of the current tile is not in the tilemap or if it's empty
                        right_loc = str(tile_x - 1) + ';' + str(tile_y)
                        right_empty = right_loc not in self.tilemap or not self.tilemap[right_loc]

                        # Check if the position above the current tile is not in the tilemap or if it's empty
                        top_loc = str(tile_x) + ';' + str(tile_y - 1)
                        top_empty = top_loc not in self.tilemap or not self.tilemap[top_loc]

                        # Check if the position below the current tile is not in the tilemap or if it's empty
                        bottom_loc = str(tile_x) + ';' + str(tile_y + 1)
                        bottom_empty = bottom_loc not in self.tilemap or not self.tilemap[bottom_loc]

                        # Render the tile only if the left, right, top, or bottom positions are either empty or not in the tilemap
                        if (left_empty or right_empty or top_empty or bottom_empty): #and ((tile_center_y > center_y and top_empty) or
                                                                                    #     (tile_center_y < center_y and bottom_empty) or
                                                                                    #     (tile_center_x <= center_x and left_empty) or
                                                                                    #     (tile_center_x >= center_x and right_empty)):
                            tile = self.tilemap[loc]
                            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))












        
        


