import pygame
import config
import os

# @todo - make this a factory?


class Egg(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('.', 'images', 'egg.png')).convert()
        #img.convert_alpha()
        #img.set_colorkey(ALPHA)
        #print(f"putting an egg at [{x}, {y}]")
        self.rect = self.image.get_rect()
        self.rect.x = x * config.tile_width
        self.rect.y = y * config.tile_height
        return


class Grain(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('.', 'images', 'grain.png')).convert()
        #img.convert_alpha()
        #img.set_colorkey(ALPHA)
        #print(f"putting grain at [{x}, {y}]")
        self.rect = self.image.get_rect()
        self.rect.x = x *config.tile_width
        self.rect.y = y *config.tile_height
        return


class Floor(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('.', 'images', 'floor.png')).convert()
        #img.convert_alpha()
        #img.set_colorkey(ALPHA)
        #print(f"putting floor at [{x}, {y}]")
        self.rect = self.image.get_rect()
        self.rect.x = x *config.tile_width
        self.rect.y = y *config.tile_height
        return


class Ladder(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('.', 'images', 'ladder.png')).convert()
        #img.convert_alpha()
        #img.set_colorkey(ALPHA)
        #print(f"putting ladder at [{x}, {y}]")
        self.rect = self.image.get_rect()
        self.rect.x = x *config.tile_width
        self.rect.y = y *config.tile_height
        return
