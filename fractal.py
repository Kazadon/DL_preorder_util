# theory https://proproprogs.ru/fractals/fractals-kak-postroit-mnozhestva-zhyulia

import pygame
import random
import os


class Objects:
    Triangle = [[300, 0], [0, 600], [600,600]]
    Penta = [[0, 300], [300, 0], [600, 300], [450, 600], [150, 600]]

class Fractal:
    def draw(object: list):
        window = pygame.display.set_mode((600, 600))
        pygame.init()
        x, y = random.randint(0, 600), random.randint(0, 600)
        apex_count = len(object)
        RUN = True
        while RUN:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    RUN = False
            A = random.randint(0, apex_count - 1)
            x, y =  0.5 * (x + object[A][0]), 0.5 * (y + object[A][1])

            pygame.draw.line(window, (0, 255, 180), (x, y), (x, y), 1)
            pygame.display.update()
        pygame.quit()

    def draw_julia():
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        
        # ----------  чтобы окно появлялось в верхнем левом углу ------------
        x = 20
        y = 40
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"
        pygame.init()
 
        W = 1000
        H = 1000
        
        sc = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Множества Жюлиа")
        sc.fill(WHITE)
        FPS = 30        # число кадров в секунду
        clock = pygame.time.Clock()
        
        # c = complex(-0.78, 0.13)
        P = 500                     # размер [2*P+1 x 2*P+1]
        # мондельброт
        scale = P / 0.055
        view = (-4900, -4700)             # масштабный коэффициент

        #scale = P/1
        #view = (-150,0)

        # жюлиа
        # scale = P / 0.9 
        # view = (0, 0)             # масштабный коэффициент
        n_iter = 100                 # число итераций для проверки принадлежности к множеству Жюлиа

        for y in range(-P+view[1], P+view[1]):
            for x in range(-P+view[0], P+view[0]):
                a = x / scale
                b = y / scale
                # мондельброт
                c = complex(a, b)
                z = complex(0)
                
                # жюлиа
                # z = complex(a, b)
                for n in range(n_iter):
                    z = z**2 + c
                    if abs(z) > 2:
                        break
                if n == n_iter-1:
                    r = g = b = 0
                else:
                    number = n % 64
                    # затестить цвета
                    if (number) < 16:
                        r = (number) * 3
                        g = (number) * 3
                        b = (number) * 3
                    elif (number) >= 16 and (number) < 25:
                        r = (number) * 3 + 30
                        g = 0
                        b =  (number) * 3 + 30                   
                    else:
                        r = (number) * 4 + 3
                        g = 0
                        b = 255 - (number * 4) - 3 
                sc.set_at((x + P - view[0], y + P - view[1]), (r, g, b))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

            pygame.display.update()
            clock.tick(FPS)


# Fractal.draw(Objects.Penta)
Fractal.draw_julia()


