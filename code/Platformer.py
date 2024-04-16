import pygame
import sys
import random
import math

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particles import Particle

class Game:
    def __init__(self):
        pygame.init()        

        pygame.display.set_caption("ta")
        self.screen = pygame.display.set_mode((1900, 1000))
        self.display = pygame.Surface((950, 500))
        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            'player': load_image('entities/player/player.png'),
            '0': load_images('tiles/dirt'),
            '1': load_images('tiles/grass'),
            '2': load_images('tiles/stone'),
            'clouds': load_images('clouds/overworld'),
            'player/idle' : Animation(load_images('entities/player/idle/'), img_dur=6),
            'player/run' : Animation(load_images('entities/player/idle/'), img_dur=6),
            'player/jump' : Animation(load_images('entities/player/idle/'), img_dur=6),
            'particle/0' : Animation(load_images('particles/grass/'), img_dur=6, loop=False),
        }

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (475, 250), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map.json')

        self.grass_spawners = []
        for grass in self.tilemap.extract([('grass, 0')], keep = True):
             self.grass_spawners.append(pygame.Rect(4 + grass['pos'][0], 4 + grass['pos'][1], 2, 2))

        self.particles = []
        
        self.scroll = [0, 0]

        self.input_key = None
        self.input = []



    def run(self):
        APressed = False
        DPressed = False

        while True:
            self.display.fill((14, 219, 248))

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 15
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 15
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for rect in self.grass_spawners:
                 if random.random() * 49999 < rect.width * rect.height:
                      pos = (rect.x + random.ranom() * rect.width, rect.y + random.random() * rect.height)
                      self.particles.append(Particle(self, 'particle/0', pos, velocity=[random.random() *2 -1, -1], frame=0))

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)

            self.tilemap.render(self.display, offset=render_scroll) #render for player add one for light later.

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

            for particle in self.particles.copy():
                 kill = particle.update()
                 particle.render(self.display, offset=render_scroll)
                 if kill:
                      self.particles.remove(particle)
                      
            

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        #if self.player.collisions['down'] == True:
                            self.movement[0] = True
                        #APressed = True
                    if event.key == pygame.K_d:
                        #if self.player.collisions['down'] == True:
                            self.movement[1] = True
                        #DPressed = True
                    if event.key in (pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_u, pygame.K_o, pygame.K_n, pygame.K_m, pygame.K_COMMA):
                        self.input.append(event.key)
                    if event.key == pygame.K_SPACE:
                        self.player.spell(input_key=event.key, input=self.input)
                        self.input = []
                    if event.key == pygame.K_w:
                        self.player.jump()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                        APressed = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                        DPressed = False

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

Game().run()


#Magic will in general arc, but adding gravity magic to it will make it not arc.
#spells can be combined but some times I want air to only push the spell. so air will in general push spells that it hits.

#make light maybe a fitler on another layer on the screen, color the area around the player and then make everything else darker.
#make partcle phyics
