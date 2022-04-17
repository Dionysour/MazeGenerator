import pygame
import random
import enum
import sys
import os
import json
from Maze import *

from typing import Dict, Tuple, List

class Generator:
    clock = pygame.time.Clock()
    maze: Maze
    cell_size: int
    wall_width: int
    maze_generator: int
    screen: pygame.display
    fps = 100
    with_visuals = False
    is_loaded = False
    running = True
    with_path = False

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        sys.setrecursionlimit(100000)

        self.maze: Maze
        self.cell_size: int
        self.wall_width: int
        self.maze_generator: int
        self.screen: pygame.display
        self.fps = 100
        self.with_visuals = False
        self.is_loaded = False
        self.running = True
        self.with_path = False
        init_maze(self)
        self.screen.fill('grey')

    def run(self):
        while self.running:
            draw_maze(self)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.with_path = True
                    if event.key == pygame.K_l:
                        self.with_path = False
                    if event.key == pygame.K_r and not self.is_loaded:
                        self.screen.fill('grey')
                        reconstruct_maze(self)
                    if event.key == pygame.K_s:
                        file_name = input('File name: ')
                        self.maze.save_maze(file_name, self)
                    if event.key == pygame.K_e:
                        set_entrance_with_mouse(self)
                    if event.key == pygame.K_x:
                        set_exit_with_mouse(self)
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                if event.type == pygame.QUIT:
                    self.running = False

            pygame.display.flip()
            self.clock.tick(20)

def init_circular_maze(maze_generator: int, gen):
    radius = input('Radius: ')
    if radius == '':
        radius = 15
    radius = int(radius)
    cell_size = input('Cell_size: ')
    if cell_size == '':
        cell_size = 20
    gen.cell_size = int(cell_size)
    wall_width = input('Wall_width: ')
    if wall_width == '':
        wall_width = 3
    gen.wall_width = int(wall_width)
    gen.screen = pygame.display.set_mode(
        ((radius * 2 - 1) * gen.cell_size, (radius * 2 - 1) * gen.cell_size))
    gen.maze = CircularMaze(radius)
    if gen.maze_generator == 1:
        gen.maze.generate_maze_dfs(gen)
    elif gen.maze_generator == 0:
        gen.maze.generate_maze_prims(gen)
    gen.maze.set_exit(random.choice(list(gen.maze.cells.keys())))
    gen.maze.calculate_path()


def init_rectangular_maze(maze_generator: int, gen):
    length = input('Length: ')
    if length == '':
        length = 30
    length = int(length)
    width = input('Width: ')
    if width == '':
        width = 30
    width = int(width)
    cell_size = input('Cell_size: ')
    if cell_size == '':
        cell_size = 20
    gen.cell_size = int(cell_size)
    wall_width = input('Wall_width: ')
    if wall_width == '':
        wall_width = 3
    gen.wall_width = int(wall_width)
    gen.maze = RectMaze(length, width)
    gen.screen = pygame.display.set_mode((length * gen.cell_size, width * gen.cell_size))
    if gen.maze_generator == 1:
        gen.maze.generate_maze_dfs(gen)
    elif gen.maze_generator == 0:
        gen.maze.generate_maze_prims(gen)
    gen.maze.set_exit(random.choice(list(gen.maze.cells.keys())))
    gen.maze.calculate_path()


def init_maze(gen):
    os.makedirs('saves', exist_ok=True)
    ans = input('Load maze(y/n): ')
    if ans == 'y':
        gen.maze = Maze.load_maze(input('File name: '), gen)
        gen.is_loaded = True
        return
    gen.maze_generator = int(input("Maze generator(0: Prim, 1: DFS): "))
    maze_type = int(input('Maze type(0: rectangular, 1: circular): '))
    with_visuals = input('With visuals?(y/n): ')
    if with_visuals == 'y':
        gen.with_visuals = True
        gen.fps = int(input('Construction speed: '))
    if with_visuals == 'n':
        gen.with_visuals = False
    if maze_type == 0:
        init_rectangular_maze(gen.maze_generator, gen)
    if maze_type == 1:
        init_circular_maze(gen.maze_generator, gen)