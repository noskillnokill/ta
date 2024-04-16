import pygame
import sys

from scripts.utils import load_images
from scripts.tilemap import Tilemap

RENDER_SCALE = 2.0

class Editor:
    def __init__(self):
        pygame.init()        

        pygame.display.set_caption("editor")
        self.screen = pygame.display.set_mode((1900, 1000))
        self.display = pygame.Surface((950, 500))

        self.clock = pygame.time.Clock()



        self.assets = {
            '0': load_images('tiles/dirt'),
            '1': load_images('tiles/grass'),
            '2': load_images('tiles/stone'),

        }

        self.movement = [False, False, False, False]

        self.tilemap = Tilemap(self, tile_size=16)

        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
             pass

        
        self.scroll = [0, 0]

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

    def run(self):
        APressed = False
        DPressed = False

        while True:
            self.display.fill((0, 0, 0))

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scroll)

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)

            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))

            if self.clicking and self.ongrid == True:
                 self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (tile_pos)}
            if self.right_clicking and self.ongrid == True:
                 tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                 if tile_loc in self.tilemap.tilemap:
                      del self.tilemap.tilemap[tile_loc]


            if self.ongrid == True:
                self.display.blit(current_tile_img, (5, 5))
            else:
                 self.display.blit(current_tile_img, mpos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                         self.clicking = True
                         #if not self.ongrid:
                         #     self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                    if event.button == 3:
                         self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False
                        
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                            self.movement[0] = True
                    if event.key == pygame.K_d:
                            self.movement[1] = True                 
                    if event.key == pygame.K_w:
                         self.movement[2] = True  
                    if event.key == pygame.K_s:
                         self.movement[3] = True  
                    if event.key == pygame.K_LSHIFT:
                         self.shift = True
                    if event.key == pygame.K_g:
                         self.ongrid = not self.ongrid
                    if event.key == pygame.K_ESCAPE:
                         self.tilemap.save('map.json')
                    if event.key == pygame.K_q:
                         self.tilemap.autotile()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                         self.movement[2] = False  
                    if event.key == pygame.K_s:
                         self.movement[3] = False  
                    if event.key == pygame.K_LSHIFT:
                         self.shift = False

            #if self.player.collisions['down'] == True:
            #    if APressed == True:
            #        print("Pressed")
            #        self.movement[0] = True
            #    if DPressed == True:
            #        print("Pressed")
            #        self.movement[1] = True
                
            
                    




                #if self.movement[0] == True:
                #if self.player.collisions['down'] == True:
                #    self.movement[0] = True
                        
                
            

            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Editor().run()


#Magic will in general arc, but adding gravity magic to it will make it not arc.
#spells can be combined but some times I want air to only push the spell. so air will in general push spells that it hits.

#make light maybe a fitler on another layer on the screen, color the area around the player and then make everything else darker.
#make partcle phyics
