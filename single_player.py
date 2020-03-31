from typing import *
import pygame
import random

pygame.init()


class Food:
    def __init__(self, root: pygame.Surface, color, size: Tuple[int, int],
                 pos=(None, None)):
        self.root = root
        self.color = color

        self.width, self.height = size
        if pos == (None, None):
            self.reset_pos()
        else:
            self.x, self.y = pos

    def draw(self):
        pygame.draw.rect(
            self.root, self.color, (self.x * self.width, self.y * self.height,
                                    self.width, self.height)
        )

    def reset_pos(self):
        root_w, root_h = self.root.get_size()
        max_x, max_y = root_w // self.width - 1, root_h // self.height - 1
        self.x, self.y = random.randint(0, max_x), random.randint(0, max_y)

    @property
    def pos(self):
        return [self.x, self.y]


class Square:
    def __init__(self, pos: Tuple[int, int], direction: Tuple[int, int], color):
        self.pos = list(pos)
        self.direction: Tuple[int, int] = direction
        self.color = color
        # example: for right -> (1, 0), for up -> (0, -1)

    def update(self):
        self.pos[0] += self.direction[0]
        self.pos[1] += self.direction[1]


class Snake:
    def __init__(self, root: pygame.Surface, color, pos,
                 square_size: Tuple[int, int], length=3):
        self.is_dead = False
        self.root = root
        self.color = color
        self.square_width, self.square_height = square_size
        self.squares: List[Square] = [
            Square(pos, (1, 0), tuple(max(0, i - 25) for i in color))
        ]

        self.grow_up(length - 1)

    def update(self):
        if not self.is_dead and len(self.squares):
            for sq_index in range(len(self.squares)):
                sq = self.squares[sq_index]
                sq.update()

                root_x, root_y = self.root.get_size()
                max_x = root_x // self.square_width - 1
                max_y = root_y // self.square_height - 1

                if sq.pos[0] < 0:
                    self.squares[sq_index].pos[0] = max_x
                if sq.pos[1] < 0:
                    self.squares[sq_index].pos[1] = max_y
                if sq.pos[0] > max_x:
                    self.squares[sq_index].pos[0] = 0
                if sq.pos[1] > max_y:
                    self.squares[sq_index].pos[1] = 0

                for other_sq_index in range(len(self.squares)):
                    if other_sq_index != sq_index and sq.pos ==\
                            self.squares[other_sq_index].pos:
                        self.is_dead = True
                        break

            for sq_index in range(len(self.squares) - 1, 0, -1):
                self.squares[sq_index].direction = \
                    self.squares[sq_index - 1].direction

    def draw(self):
        for square in self.squares:
            pygame.draw.rect(
                self.root, square.color,
                (square.pos[0] * self.square_width,
                 square.pos[1] * self.square_height,
                 self.square_width, self.square_height)
            )

    def grow_up(self, count=1):
        for _ in range(count):
            last_x, last_y = self.squares[-1].pos
            last_dir_x, last_dir_y = self.squares[-1].direction
            self.squares.append(
                Square((last_x - last_dir_x, last_y - last_dir_y),
                       (last_dir_x, last_dir_y), self.color)
            )


class Game:
    def __init__(self, size: Tuple[int, int], grid_size=(30, 30)):
        xr, yr = size[0] % grid_size[0], size[1] % grid_size[1]  # remaining's
        if xr or yr:
            raise ValueError(
                "incompatible window and grid size: {} % {} => {}".format(
                    size, grid_size, (xr, yr)
                )
            )

        self.root = pygame.display.set_mode(size)
        pygame.display.set_caption("OOP SNAKE GAME")

        self.width, self.height = size
        self.grid_width, self.grid_height = grid_size

        self.background = (50, 200, 100)

        self.snake = Snake(self.root, (255, 0, 0), (5, 2), self.grid_size)
        self.food = Food(root=self.root, color=(
            255, 128, 0), size=self.grid_size)

        self.running = False

    @property
    def grid_size(self):
        return self.grid_width, self.grid_height

    def draw_grids(self, color=(0, 0, 0), grid_width=None, grid_height=None):
        if grid_width is None:
            grid_width = self.grid_width

        if grid_height is None:
            grid_height = self.grid_height

        for grid_x in range(0, self.width, grid_width):
            for grid_y in range(0, self.height, grid_height):
                # drawing horizontal lines
                pygame.draw.line(
                    self.root, color, (grid_x, grid_y),
                    (grid_x + grid_width, grid_y)
                )
                # drawing vertical lines
                pygame.draw.line(
                    self.root, color, (grid_x, grid_y),
                    (grid_x, grid_y + grid_height)
                )

    def mainloop(self, fps=60):

        # food_count = 2
        # foods: List[Food] = []
        # for _ in range(food_count):
        #     new = Food(root=self.root, color=(255, 128, 0), size=self.grid_size)
        #     for other in foods:
        #         while new.pos in [other.pos] + [sq.pos for sq in snake.squares]:
        #             new.reset_pos()
        #     foods.append(new)

        self.snake = Snake(self.root, (255, 0, 0), (5, 2), self.grid_size)
        self.food = Food(root=self.root, color=(
            255, 128, 0), size=self.grid_size)

        self.running = True
        while self.running:
            pygame.time.delay(1000 // fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()

            first_dir = self.snake.squares[0].direction
            if keys[pygame.K_w] and first_dir != (0, 1):
                self.snake.squares[0].direction = (0, -1)
            if keys[pygame.K_a] and first_dir != (1, 0):
                self.snake.squares[0].direction = (-1, 0)
            if keys[pygame.K_s] and first_dir != (0, -1):
                self.snake.squares[0].direction = (0, 1)
            if keys[pygame.K_d] and first_dir != (-1, 0):
                self.snake.squares[0].direction = (1, 0)

            self.root.fill(self.background)

            # for food in foods:
            #     food.draw()

            self.food.draw()
            self.snake.update()
            self.snake.draw()

            self.draw_grids()

            # for i, food in enumerate(foods):
            #     if snake.squares[0].pos == food.pos:
            #         snake.grow_up()
            #         while any(sq.pos == food.pos for sq in snake.squares):
            #             food.reset_pos()

            if self.snake.squares[0].pos == self.food.pos:
                self.snake.grow_up()
                while any(sq.pos == self.food.pos for sq in self.snake.squares):
                    self.food.reset_pos()

            if self.snake.is_dead:
                text_content = "YOUR SCORE:\n" + str(len(self.snake.squares))

                font = pygame.font.Font(r"font\JetBrainsMono_Medium.ttf", 50)
                text = font.render(text_content, True, (0, 0, 0), (255, 0, 0))
                text_rect = text.get_rect()
                text_rect.center = (self.width // 2, self.height // 2)
                self.root.blit(text, text_rect)

                if keys[pygame.K_SPACE]:
                    return self.mainloop(fps)

            pygame.display.update()


def main():
    size = 600, 600
    grid_size = 30, 30
    root = Game(size, grid_size)
    root.mainloop(fps=20)


if __name__ == "__main__":
    main()
