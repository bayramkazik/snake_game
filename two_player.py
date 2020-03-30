"""
TWO PLAYER SNAKE GAME BY BAYRAM KAZIK

GitHub -> https://github.com/bayramkazik
"""


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
        self.moving = True
        self.root = root
        self.color = color
        self.square_width, self.square_height = square_size
        self.squares: List[Square] = [
            Square(pos, (1, 0), tuple(max(0, i - 50) for i in color)),
        ]
        
        self.grow_up(length - 1)
    
    @property
    def score(self):
        return len(self.squares)

    def update(self):
        if not self.is_dead and len(self.squares) and self.moving:
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
                (int(square.pos[0] * self.square_width),
                 int(square.pos[1] * self.square_height),
                 int(self.square_width), int(self.square_height))
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
        
        self.init_objects()
        
        self.running = False
    
    def init_objects(self):
        total_x_grids = self.width / self.grid_width
        total_y_grids = self.height / self.grid_height
        snakes_y = total_y_grids / 3
        self.snakes: List[Snake] = [
            Snake(self.root, (255, 0, 0), (int(total_x_grids * 2 / 3 + random.randint(-20, 20)), snakes_y), self.grid_size, 20),
            Snake(
                self.root, (0, 0, 255), (int(total_x_grids * 2 / 3 + random.randint(-20, 20)), total_y_grids - snakes_y),
                self.grid_size, 20
            ),
        ]
        self.food = Food(
            root=self.root, color=(255, 128, 0), size=self.grid_size
        )
    
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
        self.init_objects()
        
        self.running = True
        ended = False
        while self.running:
            pygame.time.delay(1000 // fps)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            keys = pygame.key.get_pressed()
            
            snake1_head_dir = self.snakes[0].squares[0].direction
            if keys[pygame.K_UP] and snake1_head_dir != (0, 1):
                self.snakes[0].squares[0].direction = (0, -1)
            if keys[pygame.K_LEFT] and snake1_head_dir != (1, 0):
                self.snakes[0].squares[0].direction = (-1, 0)
            if keys[pygame.K_DOWN] and snake1_head_dir != (0, -1):
                self.snakes[0].squares[0].direction = (0, 1)
            if keys[pygame.K_RIGHT] and snake1_head_dir != (-1, 0):
                self.snakes[0].squares[0].direction = (1, 0)
            
            snake2_head_dir = self.snakes[1].squares[0].direction
            if keys[pygame.K_w] and snake2_head_dir != (0, 1):
                self.snakes[1].squares[0].direction = (0, -1)
            if keys[pygame.K_a] and snake2_head_dir != (1, 0):
                self.snakes[1].squares[0].direction = (-1, 0)
            if keys[pygame.K_s] and snake2_head_dir != (0, -1):
                self.snakes[1].squares[0].direction = (0, 1)
            if keys[pygame.K_d] and snake2_head_dir != (-1, 0):
                self.snakes[1].squares[0].direction = (1, 0)
            
            self.root.fill(self.background)

            self.food.draw()

            # todo : also, test pythonic - for loop
            for i in range(2):
                self.snakes[i].update()
                self.snakes[i].draw()

            self.draw_grids()
            
            for i, snake in enumerate(self.snakes):
                if snake.squares[0].pos == self.food.pos:
                    self.snakes[i].grow_up(5)
                    while any(sq.pos == self.food.pos for sq in snake.squares):
                        self.food.reset_pos()
            
            for snake_i in range(2):
                is_dead = True
                snake_head = self.snakes[snake_i].squares[0]
                self_squares = self.snakes[snake_i].squares[1:]
                other_squares = self.snakes[1 - snake_i].squares
                for sq in self_squares + other_squares:
                    if snake_head.pos == sq.pos:
                        break
                else:
                    is_dead = False

                if is_dead:
                    self.snakes[snake_i].is_dead = True
            
            if ended:
                for snake in self.snakes:
                    if snake.is_dead:
                        pygame.draw.rect(
                            self.root, (0, 0, 0), 
                            (
                                int(snake.squares[0].pos[0] * snake.square_width),
                                int(snake.squares[0].pos[1] * snake.square_height),
                                int(snake.square_width), 
                                int(snake.square_height)
                            )
                        )

                if keys[pygame.K_SPACE]:
                    return self.mainloop(fps)

                font = pygame.font.Font("font/JetBrainsMono_Medium.ttf", 40)
                text = font.render(text_content, True, (0, 0, 0), winner_color)
                text_rect = text.get_rect()
                text_rect.center = (self.width // 2, self.height // 2)
                self.root.blit(text, text_rect)
            elif any(snake.is_dead for snake in self.snakes):
                red_dead = self.snakes[0].is_dead
                blue_dead = self.snakes[1].is_dead

                if red_dead and blue_dead:
                    if self.snakes[0].score > self.snakes[1].score:
                        text_content = " SLAUGHTER!\nRED WINS ! "
                        winner_color = (150, 0, 0)
                    elif self.snakes[0].score < self.snakes[1].score:
                        text_content = " SLAUGHTER!\nBLUE WINS ! "
                        winner_color = (0, 0, 150)
                    else:
                        text_content = " THERE IS A DRAW! "
                        winner_color = (100, 0, 100)
                    
                elif red_dead:
                    text_content = " BLUE WINS! "
                    winner_color = (0, 0, 255)
                else:
                    text_content = " RED WINS! "
                    winner_color = (255, 0, 0)

                for s in self.snakes:
                    s.moving = False

                ended = True

            score_font = pygame.font.Font("font/JetBrainsMono_Medium.ttf", 25)
            red_score_text = score_font.render(str(self.snakes[0].score), True, self.snakes[0].color)
            red_rect = red_score_text.get_rect()
            red_rect.topleft = (20, 0)
            self.root.blit(red_score_text, red_rect)

            blue_score_text = score_font.render(str(self.snakes[1].score), True, self.snakes[1].color)
            blue_rect = blue_score_text.get_rect()
            blue_rect.topright = (self.width - 20, 0)
            self.root.blit(blue_score_text, blue_rect)

            pygame.display.update()



def main():
    size = 1200, 600
    grid_size = 20, 20
    root = Game(size, grid_size)
    root.mainloop(fps=30)


if __name__ == "__main__":
    main()
