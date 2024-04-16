import pygame
import math

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''
        self.anim_offset = (0, 0)
        self.flip = False
        self.set_action('idle')

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        self.pos[1] = math.ceil(self.pos[1])
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        if self.collisions['left'] or self.collisions['right']:
            self.velocity[0] = 0

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        Player.lightlevel_value = 100
        self.inputs = [
            [105, 105],
            [106, 106],
            [107, 107],
            [108, 108],
            [109, 109],
            [110, 110],
            [111, 111],
            [44, 44],
            [117, 117],
            [pygame.K_l, pygame.K_k, pygame.K_j, pygame.K_i],
        ]
        self.HUD = pygame.display.get_surface()
        self.HUD_height = 1900
        self.HUD_width = 900
        self.input = input


    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        Player.lightlevel_value -= 0.01
        Player.lightlevel_value = max(4, min(Player.lightlevel_value, 15))
        self.air_time += 1

        if self.collisions['down'] == True:
            self.air_time = 0     
        

        if self.air_time > 4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')


        font = pygame.font.Font(None, 36)
        text = font.render(' '.join(str(self.input)), True, (0, 0, 0))
        if text != ():
            self.HUD.blit(text, ((1900 - text.get_width()) // 2, (900 - text.get_height()) // 2))
        pygame.display.flip()

    def jump(self):
        if self.jumps >=1:
            self.velocity[1] += (-self.size[1] / self.size[1] * 2.3)
            self.jumps -= 1
            self.air_time = 5
            print("yes")

    def spell(self, input_key, input):
        self.input = input

        if input_key == 32:
            print(self.input)
            for sequence in self.inputs:
                if self.input == sequence:
                    if sequence == self.inputs[0]:
                        self.jumps = 2
                    if sequence == self.inputs[1]:
                        Player.lightlevel_value += 5
                        Player.lightlevel_value = max(4, min(Player.lightlevel_value, 15))
                        print(Player.lightlevel_value)

            self.input = []

    def lightlevel(self):
        
        return Player.lightlevel_value




