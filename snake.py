import pygame
from pygame.locals import *
from dataclasses import dataclass
from typing import List
import time
import sys
from copy import copy
import random


@dataclass(init=False, repr=False, eq=False)
class Colors:
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    dark_green = (20, 145, 20)


@dataclass
class Pos:
    x: int
    y: int

    def __add__(self, other):
        return Pos(self.x + other.x, self.y + other.y)


class Snake:
    segments: List[Pos]
    _direction: str
    _dirs = {
        'UP': Pos(x=0, y=-1),
        'RIGHT': Pos(x=1, y=0),
        'DOWN': Pos(x=0, y=1),
        'LEFT': Pos(x=-1, y=0),
    }
    _opposite_dirs = {'Y': ['UP', 'DOWN'], 'X': ['LEFT', 'RIGHT']}
    dead: bool
    ate: bool

    def __init__(self, field_width, field_length):
        self._field_legth = field_length
        self._field_width = field_width
        self.segments = [Pos(x=field_width // 2, y=field_length // 2),
                         Pos(x=field_width // 2, y=field_length // 2 + 1),
                         Pos(x=field_width // 2, y=field_length // 2 + 2)]
        self._direction = 'UP'
        self.dead = False
        self.ate = False

    def change_dir(self, new_direction):
        if self._direction in ['UP', 'DOWN'] and new_direction in ['UP', 'DOWN']:
            return
        elif self._direction in ['LEFT', 'RIGHT'] and new_direction in ['LEFT', 'RIGHT']:
            return
        self._direction = new_direction

    def move(self):
        if self.ate:
            self.grow()
            for index in range(len(self.segments) - 2, 0, -1):
                self.segments[index] = copy(self.segments[index - 1])
        else:
            for index in range(len(self.segments) - 1, 0, -1):
                self.segments[index] = copy(self.segments[index - 1])

        self.segments[0] += self._dirs[self._direction]

        if self.segments[0].x >= self._field_width:
            self.segments[0].x = 0
        elif self.segments[0].y >= self._field_legth:
            self.segments[0].y = 0
        elif self.segments[0].x < 0:
            self.segments[0].x = self._field_width - 1
        elif self.segments[0].y < 0:
            self.segments[0].y = self._field_legth - 1

        if self.segments[0] in self.segments[1:]:
            self.dead = True

    def grow(self):
        self.segments.append(copy(self.segments[len(self.segments) - 1]))
        self.ate = False


class Stopwatch:
    def __init__(self):
        self._start_time = time.time()

    def seconds(self):
        return time.time() - self._start_time

    def reset(self):
        self._start_time = time.time()


class Field:
    def __init__(self, width, length, snake):
        self.width = width
        self.length = length
        self.snake = snake
        self.fruits = []

    def spawn_fruit(self):
        while True:
            fruit_pos = Pos(x=random.randint(0, self.width - 1), y=random.randint(0, self.length - 1))

            if fruit_pos not in self.snake.segments:
                self.fruits.append(fruit_pos)
                break


def main():
    field_size = Pos(10, 10)
    snake = Snake(field_size.x, field_size.y)
    field = Field(field_size.x, field_size.y, snake)

    stopwatch = Stopwatch()
    move_time = 0.25

    pygame.init()
    pygame.display.set_caption('Snake')

    screen = pygame.display.set_mode((550, 600), 0, 32)
    screen.fill(Colors.black)

    field_offset = Pos(x=20, y=20)
    cell_size = 50

    new_dir = 'UP'
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_UP or event.key == K_w:
                    new_dir = 'UP'
                elif event.key == K_RIGHT or event.key == K_d:
                    new_dir = 'RIGHT'
                elif event.key == K_DOWN or event.key == K_s:
                    new_dir = 'DOWN'
                elif event.key == K_LEFT or event.key == K_a:
                    new_dir = 'LEFT'

        if stopwatch.seconds() > move_time:
            if new_dir:
                snake.change_dir(new_dir)
            snake.move()

            if snake.segments[0] in field.fruits:
                snake.ate = True
                field.fruits.remove(snake.segments[0])

            if len(field.fruits) < 3:
                field.spawn_fruit()

            for y in range(field.length):
                for x in range(field.width):
                    if Pos(x, y) in field.fruits:
                        pygame.draw.rect(screen,
                                         Colors.red,
                                         (field_offset.x + x * cell_size, field_offset.y + y * cell_size,
                                          cell_size, cell_size),
                                         0)
                    else:
                        pygame.draw.rect(screen,
                                         Colors.black,
                                         (field_offset.x + x * cell_size, field_offset.y + y * cell_size,
                                          cell_size, cell_size),
                                         0)
                    pygame.draw.rect(screen,
                                     Colors.white,
                                     (field_offset.x + x * cell_size, field_offset.y + y * cell_size,
                                      cell_size, cell_size),
                                     2)

            pygame.draw.rect(screen,
                             Colors.green,
                             (field_offset.x + snake.segments[0].x * cell_size, field_offset.y + snake.segments[0].y * cell_size, cell_size,
                              cell_size),
                             0)
            pygame.draw.rect(screen,
                             Colors.white,
                             (field_offset.x + snake.segments[0].x * cell_size, field_offset.y + snake.segments[0].y * cell_size, cell_size,
                              cell_size),
                             2)
            for segment in snake.segments[1:]:
                pygame.draw.rect(screen,
                                 Colors.dark_green,
                                 (field_offset.x + segment.x * cell_size, field_offset.y + segment.y * cell_size, cell_size, cell_size),
                                 0)
                pygame.draw.rect(screen,
                                 Colors.white,
                                 (field_offset.x + segment.x * cell_size, field_offset.y + segment.y * cell_size, cell_size, cell_size),
                                 2)
            if snake.dead:
                pygame.quit()
                sys.exit()
            stopwatch.reset()

        pygame.display.update()
        time.sleep(0.1)


if __name__ == '__main__':
    main()
