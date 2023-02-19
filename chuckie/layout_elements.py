import pygame
import config
import os


class Egg(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('.', 'images', 'egg.png')).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x * config.tile_width
        self.rect.y = y * config.tile_height
        self.name = "egg"
        return


class Grain(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('.', 'images', 'grain.png')).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x * config.tile_width
        self.rect.y = y * config.tile_height
        self.name = "grain"
        return


class Floor(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('.', 'images', 'floor.png')).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x * config.tile_width
        self.rect.y = y * config.tile_height
        self.name = "floor"
        return


class Ladder(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('.', 'images', 'ladder.png')).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x * config.tile_width
        self.rect.y = y * config.tile_height
        self.name = "ladder"
        return
