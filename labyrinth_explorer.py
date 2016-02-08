#!/usr/bin/env python
# coding=utf-8
#   Python Script
#
#   Copyright © Manoel Vilela
#
#


from __future__ import print_function
import os
import pygame
from labyrinth_generator import generate
from random import randint
from time import time

BLOCKSIZE = 16
WIDTH = 590
HEIGHT = 480

WHITE = (255, 255, 255)
YELLOW = (255, 200, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)


#
# DEPRECATED
#
def safe_position(level):  # ??
    a, b = len(level) - 2, len(level[0]) - 2
    x, y = (randint(1, a), randint(1, b))
    if level[x][y] != ' ':
        print('Not safe', x, y, '->', level[x][y])
        x, y = safe_position(level)
    return (min(1, x + 1), y)


# Class for the orange dude
class Player(object):

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BLOCKSIZE, BLOCKSIZE)

    def move(self, dx, dy):

        # Move each axis separately.
        # Note that this checks for collisions both times.
        if dx != 0:
            self.move_single_axis(dx, 0)
        if dy != 0:
            self.move_single_axis(0, dy)

    def move_single_axis(self, dx, dy):

        # Move the rect
        self.rect.x += dx
        self.rect.y += dy

        # If you collide with a wall, move out based on velocity
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if dx > 0:  # Moving right; Hit the left side of the wall
                    self.rect.right = wall.rect.left
                if dx < 0:  # Moving left; Hit the right side of the wall
                    self.rect.left = wall.rect.right
                if dy > 0:  # Moving down; Hit the top side of the wall
                    self.rect.bottom = wall.rect.top
                if dy < 0:  # Moving up; Hit the bottom side of the wall
                    self.rect.top = wall.rect.bottom

    @property
    def position(self):
        return self.rect.x, self.rect.y


class AI(Player):
    memo = {}
    path = {}

    dx = 2
    dy = 2

    def run(self):
        self.remember()
        self.walk()
        self.forget_it()

    def remember(self):
        self.path[time()] = self.position
        self.memo.setdefault(self.position, 0).__add__(1)

    def walk(self):
        motion = self.decide()
        self.move(*motion)

    def decide(self):
        if self.memo[self.position] > 10:
            self.change()

        if len(self.path) > 2:
            t1, t2 = sorted(self.path, reverse=True)[:2]
            (x1, y1), (x2, y2) = self.path[t1], self.path[t2]
            diff = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
            if not diff:
                self.change()

        return self.dx, self.dy

    def forget_it(self):
        if len(self.path) > 3:
            del self.path[min(self.path)]

    def change(self):
        from random import choice
        dice = choice([0, 1])

        if dice:
            self.dx *= -1
        else:
            self.dy *= -1


# Nice class to hold a wall rect
class Wall(object):
    def __init__(self, pos):
        walls.append(self)
        self.rect = pygame.Rect(pos[0], pos[1], BLOCKSIZE, BLOCKSIZE)


def draw_counter(time):
    text = pygame.font.Font('freesansbold.ttf', BLOCKSIZE)
    text_surf = text.render('Time: {:04.1f}'.format(time), True, WHITE)
    text_rect = text_surf.get_rect()
    text_rect.midright = (WIDTH - 40, HEIGHT - BLOCKSIZE // 2)
    screen.blit(text_surf, text_rect)


def setup():
    global walls, player, clock, end_rect, screen, computer
    # Initialise pygame
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.init()

    # Set up the display
    pygame.display.set_caption("Get to the red square!")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    walls = []  # List to hold the walls
    level = generate()

    # Holds the level layout in a list of strings.

    # Parse the level string above. W = wall, E = exit
    x = y = 0
    for row in level:
        for col in row:
            if col == "W":
                Wall((x, y))
            elif col == "E":
                end_rect = pygame.Rect(x, y, BLOCKSIZE, BLOCKSIZE)
            elif col == "P":
                player = Player(x, y)
            elif col == "C":
                computer = AI(x, y)
            x += BLOCKSIZE
        y += BLOCKSIZE
        x = 0

    return screen, clock, walls, player, end_rect


def game():
    setup()
    running = True
    start = time()
    while running:

        clock.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False

        # Move the player if an arrow key is pressed
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            player.move(-2, 0)
        if key[pygame.K_RIGHT]:
            player.move(2, 0)
        if key[pygame.K_UP]:
            player.move(0, -2)
        if key[pygame.K_DOWN]:
            player.move(0, 2)

        # Just added this to make it slightly fun ;)
        if player.rect.colliderect(end_rect):
            raise SystemExit("You win! @{:2f}s".format(time() - start))
        if computer.rect.colliderect(end_rect):
            raise SystemExit("You lost! The computer wins")
        # Draw the scene
        screen.fill(BLACK)
        computer.run()
        for wall in walls:
            pygame.draw.rect(screen, WHITE, wall.rect)
        pygame.draw.rect(screen, RED, end_rect)
        pygame.draw.rect(screen, GREEN, player.rect)
        pygame.draw.rect(screen, YELLOW, computer.rect)
        draw_counter(time() - start)
        pygame.display.flip()

if __name__ == '__main__':
    game()
