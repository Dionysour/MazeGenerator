import enum
import json
from typing import Dict, Tuple, List
import pygame
import random


def str_to_tuple(string):
    string = string[1:-1]
    return tuple(map(int, string.split(', ')))


class Directions(int, enum.Enum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


class CellType(int, enum.Enum):
    REGULAR = 0
    IN = 1
    OUT = 2
    PATH = 3


class Cell:
    x: int
    y: int
    walls: Dict[Directions, bool]
    visited: bool = 0
    cell_type: CellType = CellType.REGULAR

    def __init__(self, x_cord: int, y_cord: int):
        self.x = x_cord
        self.y = y_cord
        self.walls = {Directions.TOP: True,
                      Directions.RIGHT: True,
                      Directions.BOTTOM: True,
                      Directions.LEFT: True}

    def get_cords(self) -> Tuple[int, int]:
        return self.x, self.y

    def encode_cell(self):
        e_walls = dict(zip(map(int, self.walls.keys()), self.walls.values()))
        e_cell_type = int(self.cell_type)
        return self.x, self.y, e_walls, e_cell_type

    @staticmethod
    def decode_cell(encoded_cell):
        (x, y, e_walls, e_cell_type) = encoded_cell
        new_cell = Cell(x, y)
        walls = dict(zip(map(Directions, map(int, e_walls.keys())),
                         e_walls.values()))
        new_cell.walls = walls
        new_cell.cell_type = CellType(e_cell_type)
        return new_cell


class Maze:

    cells: Dict[Tuple[int, int], Cell]
    entrance: Tuple[int, int] = None
    exit: Tuple[int, int] = None

    def __init__(self):
        pass

    def set_exit(self, exit_cords: Tuple[int, int]):
        if self.exit is not None:
            self.cells[self.exit].cell_type = CellType.REGULAR
        self.exit = exit_cords
        self.cells[exit_cords].cell_type = CellType.OUT

    def set_enter(self, entrance_cords: Tuple[int, int]):
        self.cells[self.entrance].cell_type = CellType.REGULAR
        self.entrance = entrance_cords
        self.cells[entrance_cords].cell_type = CellType.IN

    def reset_cells_path(self):
        for cell in self.cells:
            if self.cells[cell].cell_type == CellType.PATH:
                self.cells[cell].cell_type = CellType.REGULAR
        Maze.calculate_times.visited = {cell: 0 for cell in self.cells.keys()}

    def save_maze(self, name, gen):
        with open(f'saves/{name}.json', 'a') as file:
            e_cells = dict(zip(map(str, self.cells.keys()),
                               map(Cell.encode_cell, self.cells.values())))
            json.dump(
                (e_cells, self.entrance, self.exit, gen.cell_size, gen.wall_width),
                file)

    @staticmethod
    def load_maze(name, gen):
        with open(f'saves/{name}.json', 'r') as file:
            maze_properties = json.loads(file.readline())
            if maze_properties[0] == 'circular':
                new_maze = CircularMaze(maze_properties[1])
            if maze_properties[0] == 'rectangular':
                new_maze = RectMaze(maze_properties[1], maze_properties[2])
            (e_cells, new_maze.entrance, new_maze.exit, gen.cell_size, gen.wall_width) \
                = json.loads(file.readline())
            new_maze.entrance = tuple(new_maze.entrance)
            new_maze.exit = tuple(new_maze.exit)
            new_maze.cells = dict(zip(map(str_to_tuple, e_cells.keys()),
                                  map(Cell.decode_cell, e_cells.values())))
            if maze_properties[0] == 'circular':
                gen.screen = pygame.display.set_mode(
                    ((new_maze.radius * 2 - 1) * gen.cell_size,
                     (new_maze.radius * 2 - 1) * gen.cell_size))
            if maze_properties[0] == 'rectangular':
                gen.screen = pygame.display.set_mode(
                    (new_maze.length * gen.cell_size,
                     new_maze.width * gen.cell_size))
        return new_maze

    def distruct_walls(self, first_cell_cords: Tuple[int, int],
                       second_cell_cords: Tuple[int, int]):
        if second_cell_cords[0] - first_cell_cords[0] == 1:
            self.cells[first_cell_cords].walls[Directions.RIGHT] = False
            self.cells[second_cell_cords].walls[Directions.LEFT] = False
        if second_cell_cords[0] - first_cell_cords[0] == -1:
            self.cells[first_cell_cords].walls[Directions.LEFT] = False
            self.cells[second_cell_cords].walls[Directions.RIGHT] = False
        if second_cell_cords[1] - first_cell_cords[1] == 1:
            self.cells[first_cell_cords].walls[Directions.BOTTOM] = False
            self.cells[second_cell_cords].walls[Directions.TOP] = False
        if second_cell_cords[1] - first_cell_cords[1] == -1:
            self.cells[first_cell_cords].walls[Directions.TOP] = False
            self.cells[second_cell_cords].walls[Directions.BOTTOM] = False

    def generate_maze_dfs(self, gen, starting_cords: Tuple[int, int] = None):
        if starting_cords is None:
            starting_cords = self.entrance
        x, y = starting_cords
        self.cells[(x, y)].visited = 1
        possible_cells: List[Tuple[int, int]] = []
        dir_coords = {Directions.TOP: (x, y - 1),
                      Directions.BOTTOM: (x, y + 1),
                      Directions.LEFT: (x - 1, y),
                      Directions.RIGHT: (x + 1, y)}
        for direction, cords in dir_coords.items():
            if cords in self.cells:
                possible_cells.append(cords)
        random.shuffle(possible_cells)

        for next_cell in possible_cells:
            if not self.cells[next_cell].visited:
                self.distruct_walls((x, y), next_cell)
                if gen.with_visuals:
                    cell_size = gen.cell_size
                    wall_width = gen.wall_width
                    draw_cell(self.cells[(x, y)], gen)
                    draw_cell(self.cells[next_cell], gen)
                    pygame.display.flip()
                    gen.clock.tick(gen.fps)
                self.generate_maze_dfs(gen, starting_cords=next_cell)

    def generate_maze_prims_helper(self, cur_cord, next_cord, walls):
        not_visited = []
        if not self.cells[next_cord].visited:
            not_visited.append(next_cord)
        if not self.cells[cur_cord].visited:
            not_visited.append(cur_cord)
        self.distruct_walls(cur_cord, next_cord)
        walls += [(next_cord, i) for i in range(4)]
        self.cells[random.choice(not_visited)].visited = 1

    def generate_maze_prims(self, gen, starting_cords: Tuple[int, int] = None):
        if starting_cords is None:
            starting_cords = self.entrance
        walls = [(starting_cords, i) for i in range(4)]
        while len(walls) != 0:
            index = random.randint(0, len(walls) - 1)
            (x, y), n_wall = walls[index]
            n_wall = Directions(n_wall)
            dir_coords = {Directions.TOP: (x, y-1),
                          Directions.BOTTOM: (x, y+1),
                          Directions.LEFT: (x-1, y),
                          Directions.RIGHT: (x+1, y)}
            cords = dir_coords[n_wall]
            if cords in self.cells and \
                    (not self.cells[cords].visited or
                    not self.cells[(x, y)].visited):
                Maze.generate_maze_prims_helper(self, (x, y), cords, walls)
                if gen.with_visuals:
                    cell_size = gen.cell_size
                    wall_width = gen.wall_width
                    draw_cell(self.cells[(x, y)], gen)
                    draw_cell(self.cells[cords], gen)
                    pygame.display.flip()
                    gen.clock.tick(gen.fps)
            walls[-1], walls[index] = walls[index], walls[-1]
            walls.pop()

    def calculate_times(self, starting_cords: Tuple[int, int] = None):
        if starting_cords is None:
            starting_cords = self.entrance
        if not hasattr(Maze.calculate_times, 'time'):
            setattr(Maze.calculate_times, 't_in', {})
            setattr(Maze.calculate_times, 't_out', {})
            setattr(Maze.calculate_times, 'visited', {})
            Maze.calculate_times.visited = \
                {cell: 0 for cell in self.cells.keys()}
            setattr(Maze.calculate_times, 'time', 0)
        x, y = starting_cords
        Maze.calculate_times.time += 1
        Maze.calculate_times.t_in[(x, y)] = Maze.calculate_times.time
        Maze.calculate_times.visited[(x, y)] = 1
        possible_cells: List[Tuple[int, int]] = []
        dir_coords = {Directions.TOP: (x, y - 1),
                      Directions.BOTTOM: (x, y + 1),
                      Directions.LEFT: (x - 1, y),
                      Directions.RIGHT: (x + 1, y)}
        for direction, cords in dir_coords.items():
            if not self.cells[(x, y)].walls[direction]:
                possible_cells.append(cords)

        for next_cell in possible_cells:
            if Maze.calculate_times.visited[next_cell] == 0:
                self.calculate_times(next_cell)

        Maze.calculate_times.time += 1
        Maze.calculate_times.t_out[(x, y)] = Maze.calculate_times.time

    def calculate_path(self, ending_cords: Tuple[int, int] = None,
                       starting_cords: Tuple[int, int] = None):
        if starting_cords is None:
            starting_cords = self.entrance
        if ending_cords is None:
            ending_cords = self.exit

        self.calculate_times(starting_cords)
        for cell in self.cells.keys():
            if Maze.calculate_times.t_in[cell] <= \
                    Maze.calculate_times.t_in[ending_cords] and \
                    Maze.calculate_times.t_out[cell] >= \
                    Maze.calculate_times.t_out[ending_cords]:
                if self.cells[cell].cell_type == CellType.REGULAR:
                    self.cells[cell].cell_type = CellType.PATH


class CircularMaze(Maze):
    radius: int

    def __init__(self, radius: int):
        super().__init__()
        self.cells = {(x, y): Cell(x, y) for x in range(radius * 2 + 1)
                      for y in range(radius * 2 + 1)
                      if ((x - radius + 1) ** 2 + (y - radius + 1) ** 2) <
                      radius ** 2}
        self.entrance = (radius-1, radius-1)
        self.cells[self.entrance].cell_type = CellType.IN
        self.radius = radius

    def reset(self):
        radius = self.radius
        self.cells = {(x, y): Cell(x, y) for x in range(radius * 2 + 1) for y in
                      range(radius * 2 + 1) if
                      ((x - radius + 1) ** 2 + (
                                  y - radius + 1) ** 2) < radius ** 2}
        self.set_enter(self.entrance)
        self.set_exit(self.exit)
        Maze.calculate_times.visited = {cell: 0 for cell in self.cells.keys()}

    def save_maze(self, name, gen):
        with open(f'saves/{name}.json', 'w') as file:
            json.dump(('circular', self.radius), file)
            file.write('\n')
        super(CircularMaze, self).save_maze(name, gen)


class RectMaze(Maze):
    width: int
    length: int

    def __init__(self, length: int, width: int):
        super().__init__()
        self.cells = {(x, y): Cell(x, y) for x in range(length)
                      for y in range(width)}
        self.width = width
        self.length = length
        self.entrance = (0, 0)
        self.cells[self.entrance].cell_type = CellType.IN

    def reset(self):
        self.cells = {(x, y): Cell(x, y) for x in range(self.length) for y in
                      range(self.width)}
        self.set_enter(self.entrance)
        self.set_exit(self.exit)
        Maze.calculate_times.visited = {cell: 0 for cell in self.cells.keys()}

    def save_maze(self, name, gen):
        with open(f'saves/{name}.json', 'w') as file:
            json.dump(('rectangular', self.length, self.width), file)
            file.write('\n')
        super(RectMaze, self).save_maze(name, gen)


def draw_maze(gen):
    for cell in gen.maze.cells.values():
        draw_cell(cell, gen)


def draw_cell(cell: Cell, gen, x0: int = 0, y0: int = 0):
    cell_size = gen.cell_size
    wall_width = gen.wall_width
    screen = gen.screen
    x, y = x0 + cell.x * cell_size, y0 + cell.y * cell_size
    # if cell.visited == 1:
    pygame.draw.rect(screen, 'darkgreen', (x, y, cell_size, cell_size))
    if gen.with_path:
        if cell.cell_type == CellType.PATH:
            pygame.draw.circle(screen, 'blue', (x + cell_size / 2, y + cell_size / 2), cell_size / 4)
    if cell.cell_type == CellType.IN:
        pygame.draw.circle(screen, 'orange', (x + cell_size/2, y + cell_size/2), cell_size/2.7)
    if cell.cell_type == CellType.OUT:
        pygame.draw.circle(screen, 'red', (x + cell_size/2, y + cell_size/2), cell_size/2.7)

    if cell.walls[Directions.TOP]:
        pygame.draw.line(screen, 'black', (x, y), (x + cell_size, y), wall_width)
    if cell.walls[Directions.BOTTOM]:
        pygame.draw.line(screen, 'black', (x, y + cell_size), (x + cell_size, y + cell_size), wall_width)
    if cell.walls[Directions.LEFT]:
        pygame.draw.line(screen, 'black', (x, y), (x, y + cell_size), wall_width)
    if cell.walls[Directions.RIGHT]:
        pygame.draw.line(screen, 'black', (x + cell_size, y), (x + cell_size, y + cell_size), wall_width)

def reconstruct_maze(gen):
    gen.maze.reset()
    if gen.maze_generator == 0:
        gen.maze.generate_maze_prims(gen)
    if gen.maze_generator == 1:
        gen.maze.generate_maze_dfs(gen)
    gen.maze.calculate_path()


def set_entrance_with_mouse(gen):
    x, y = pygame.mouse.get_pos()
    x //= gen.cell_size
    y //= gen.cell_size
    if (x, y) in gen.maze.cells:
        gen.maze.reset_cells_path()
        gen.maze.set_enter((x, y))
        gen.maze.calculate_path()


def set_exit_with_mouse(gen):
    x, y = pygame.mouse.get_pos()
    x //= gen.cell_size
    y //= gen.cell_size
    if (x, y) in gen.maze.cells.keys():
        gen.maze.reset_cells_path()
        gen.maze.set_exit((x, y))
        gen.maze.calculate_path()