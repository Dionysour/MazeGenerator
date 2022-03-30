import pygame
import random
import enum
import sys

from typing import Dict, Tuple, List


class Directions(enum.Enum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


class CellType(enum.Enum):
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

    def generate_maze_dfs(self, starting_cords: Tuple[int, int] = None):
        if starting_cords is None:
            starting_cords = self.entrance
        if not hasattr(Maze.generate_maze_dfs, 'time'):
            setattr(Maze.generate_maze_dfs, 't_in', {})
            setattr(Maze.generate_maze_dfs, 't_out', {})
            setattr(Maze.generate_maze_dfs, 'time', 0)
        x, y = starting_cords
        Maze.generate_maze_dfs.time += 1
        self.generate_maze_dfs.t_in[(x, y)] = Maze.generate_maze_dfs.time
        self.cells[(x, y)].visited = 1
        possible_cells: List[Tuple[int, int]] = []

        if (x+1, y) in self.cells:
            possible_cells.append((x+1, y))
        if (x, y+1) in self.cells:
            possible_cells.append((x, y+1))
        if (x-1, y) in self.cells:
            possible_cells.append((x-1, y))
        if (x, y-1) in self.cells:
            possible_cells.append((x, y-1))
        random.shuffle(possible_cells)

        for next_cell in possible_cells:
            if not self.cells[next_cell].visited:
                self.distruct_walls((x, y), next_cell)
                self.generate_maze_dfs(next_cell)

        Maze.generate_maze_dfs.time += 1
        Maze.generate_maze_dfs.t_out[(x, y)] = Maze.generate_maze_dfs.time

    def calculate_times(self, starting_cords: Tuple[int, int] = None):
        if starting_cords is None:
            starting_cords = self.entrance
        if not hasattr(Maze.calculate_times, 'time'):
            setattr(Maze.calculate_times, 't_in', {})
            setattr(Maze.calculate_times, 't_out', {})
            setattr(Maze.calculate_times, 'visited', {})
            Maze.calculate_times.visited = {cell: 0 for cell in self.cells.keys()}
            setattr(Maze.calculate_times, 'time', 0)
        x, y = starting_cords
        Maze.calculate_times.time += 1
        Maze.calculate_times.t_in[(x, y)] = Maze.calculate_times.time
        Maze.calculate_times.visited[(x, y)] = 1
        possible_cells: List[Tuple[int, int]] = []

        if not self.cells[(x, y)].walls[Directions.LEFT]:
            possible_cells.append((x - 1, y))
        if not self.cells[(x, y)].walls[Directions.RIGHT]:
            possible_cells.append((x + 1, y))
        if not self.cells[(x, y)].walls[Directions.BOTTOM]:
            possible_cells.append((x, y + 1))
        if not self.cells[(x, y)].walls[Directions.TOP]:
            possible_cells.append((x, y - 1))

        for next_cell in possible_cells:
            if Maze.calculate_times.visited[next_cell] == 0:
                self.calculate_times(next_cell)

        Maze.calculate_times.time += 1
        Maze.calculate_times.t_out[(x, y)] = Maze.calculate_times.time

    def calculate_path(self, ending_cords: Tuple[int, int] = None, starting_cords: Tuple[int, int] = None):  # assigns PATH type to all cells on path
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
        self.cells = {(x, y): Cell(x, y) for x in range(radius * 2 + 1) for y in
                      range(radius * 2 + 1) if
                      ((x - radius + 1) ** 2 + (y - radius + 1) ** 2) < radius ** 2}
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


class RectMaze(Maze):
    width: int
    length: int

    def __init__(self, length: int, width: int):
        super().__init__()
        self.cells = {(x, y): Cell(x, y) for x in range(length) for y in range(width)}
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


def draw_maze(maze: Maze, cell_size: int = 50, wall_width: int = 4, with_path: bool = False):
    for cell in maze.cells.values():
        draw_cell(cell, cell_size=cell_size, wall_width=wall_width, with_path=with_path)


def draw_cell(cell: Cell, cell_size: int = 50, wall_width: int = 4, with_path: bool = False, x0: int = 0, y0: int = 0):
    x, y = x0 + cell.x * cell_size, y0 + cell.y * cell_size
    pygame.draw.rect(screen, 'darkgreen', (x, y, cell_size, cell_size))
    if with_path:
        if cell.cell_type == CellType.PATH:
            pygame.draw.circle(screen, 'blue', (x + cell_size / 2, y + cell_size / 2), cell_size / 7)
    if cell.cell_type == CellType.IN:
        pygame.draw.circle(screen, 'orange', (x + cell_size/2, y + cell_size/2), cell_size/3.5)
    if cell.cell_type == CellType.OUT:
        pygame.draw.circle(screen, 'red', (x + cell_size/2, y + cell_size/2), cell_size/3.5)

    if cell.walls[Directions.TOP]:
        pygame.draw.line(screen, 'black', (x, y), (x + cell_size, y), wall_width)
    if cell.walls[Directions.BOTTOM]:
        pygame.draw.line(screen, 'black', (x, y + cell_size), (x + cell_size, y + cell_size), wall_width)
    if cell.walls[Directions.LEFT]:
        pygame.draw.line(screen, 'black', (x, y), (x, y + cell_size), wall_width)
    if cell.walls[Directions.RIGHT]:
        pygame.draw.line(screen, 'black', (x + cell_size , y), (x + cell_size, y + cell_size), wall_width)


def init_circular_maze():
    global maze
    global cell_size
    global wall_width
    global screen
    radius = input('Radius: ')
    if radius == '':
        radius = 10
    radius = int(radius)
    cell_size = input('Cell_size: ')
    if cell_size == '':
        cell_size = 20
    cell_size = int(cell_size)
    wall_width = input('Wall_width: ')
    if wall_width == '':
        wall_width = 3
    wall_width = int(wall_width)
    maze = CircularMaze(radius)
    maze.generate_maze_dfs()
    maze.set_exit(random.choice(list(maze.cells.keys())))
    maze.calculate_path()
    screen = pygame.display.set_mode(((radius*2-1)*cell_size, (radius*2-1)*cell_size))


def init_rectangular_maze():
    global maze
    global cell_size
    global wall_width
    global screen
    length = input('Length:')
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
    cell_size = int(cell_size)
    wall_width = input('Wall_width: ')
    if wall_width == '':
        wall_width = 3
    wall_width = int(wall_width)
    maze = RectMaze(length, width)
    maze.generate_maze_dfs()
    maze.set_exit(random.choice(list(maze.cells.keys())))
    maze.calculate_path()
    screen = pygame.display.set_mode((length*cell_size, width*cell_size))


def init_maze():
    maze_type = input('maze_type(rectangular, circular): ')
    if maze_type == 'rectangular':
        init_rectangular_maze()
    if maze_type == 'circular':
        init_circular_maze()


def set_entrance_with_mouse():
    x, y = pygame.mouse.get_pos()
    x //= cell_size
    y //= cell_size
    if (x, y) in maze.cells:
        maze.reset_cells_path()
        maze.set_enter((x, y))
        maze.calculate_path()


def set_exit_with_mouse():
    x, y = pygame.mouse.get_pos()
    x //= cell_size
    y //= cell_size
    if (x, y) in maze.cells.keys():
        maze.reset_cells_path()
        maze.set_exit((x, y))
        maze.calculate_path()


if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()
    sys.setrecursionlimit(100000)

    maze: Maze
    cell_size: int
    wall_width: int
    screen: pygame.display
    init_maze()
    running = True
    with_path = False
    while running:
        screen.fill('grey')
        draw_maze(maze, cell_size=cell_size, wall_width=wall_width, with_path=with_path)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    with_path = True
                if event.key == pygame.K_l:
                    with_path = False
                if event.key == pygame.K_r:
                    maze.reset()
                    maze.generate_maze_dfs()
                    maze.calculate_path()
                if event.key == pygame.K_e:
                    set_entrance_with_mouse()
                if event.key == pygame.K_x:
                    set_exit_with_mouse()
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(60)

