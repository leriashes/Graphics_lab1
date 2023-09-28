import pygame as pg
from matrixFunctions import *

class Object3D:
    def __init__(self, render):
        self.render = render

        self.start = False
        self.x = 1
        self.y = 1
        self.z = 1
        self.t = 0


        self.moving_speed = 0.02
        self.rotation_speed = 0.01

        self.vertexes = np.array([
            (0, 0, 0, 1), (0, 0.6, 0, 1), (0.2, 0.6, 0, 1), (0.2, 0.2, 0, 1), 
            (0.4, 0.2, 0, 1), (0.4, 0.4, 0, 1), (0.6, 0.4, 0, 1), (0.6, 0.2, 0, 1),
            (0.8, 0.2, 0, 1), (0.8, 0.6, 0, 1), (1, 0.6, 0, 1), (1, 0, 0, 1),
            (0, 0, 0.6, 1), (0, 0.6, 0.6, 1), (0.2, 0.6, 0.6, 1), (0.2, 0.2, 0.6, 1), 
            (0.4, 0.2, 0.6, 1), (0.4, 0.4, 0.6, 1), (0.6, 0.4, 0.6, 1), (0.6, 0.2, 0.6, 1),
            (0.8, 0.2, 0.6, 1), (0.8, 0.6, 0.6, 1), (1, 0.6, 0.6, 1), (1, 0, 0.6, 1)
        ])

        self.edges = []

        for i in range(12):
            self.edges.append((i, (i + 1) % 12))
            self.edges.append((i, i + 12))
            self.edges.append((i + 12, (i + 1) % 12 + 12))

        self.edges = np.array(self.edges)

        self.font = pg.font.SysFont('Arial', 30, bold=True)
        self.color_edges = [(pg.Color(219, 189, 33, 1), edge) for edge in self.edges]
        self.movement_flag, self.draw_vertexes = True, True
        self.label = ''

    def remap(self, val, low1, high1, low2, high2):
        return low2 + (val - low1) * (high2 - low2) / (high1 - low1)

    def draw(self):
        if (self.start):
            if (self.t < 30000):
                time_n = max(self.remap(self.t, 0, 30000, 0, 1), 0)
                s = (1 - time_n)
                s *= s
                s *= s
                s = 1 - s
                nx = 1 + self.remap(s, 0, 1, 0, self.x - 1)
                self.x /= nx
                ny = 1 + self.remap(s, 0, 1, 0, self.y - 1)
                self.y /= ny
                nz = 1 + self.remap(s, 0, 1, 0, self.z - 1)
                self.z /= nz
                self.dilatate((nx, ny, nz))
                self.t += 1
            else:
                self.start = False


        self.screen_projection()
        #self.movement()


    def control(self):
        key = pg.key.get_pressed()
        if key[pg.K_a]:
            self.translate((-self.moving_speed, 0, 0))
        if key[pg.K_d]:
            self.translate((self.moving_speed, 0, 0))
        if key[pg.K_w]:
            self.translate((0, 0, self.moving_speed))
        if key[pg.K_s]:
            self.translate((0, 0, -self.moving_speed))
        if key[pg.K_q]:
            self.translate((0, -self.moving_speed, 0))
        if key[pg.K_e]:
            self.translate((0, self.moving_speed, 0))

        if key[pg.K_i]:
            self.rotate_x((self.rotation_speed))
        if key[pg.K_k]:
            self.rotate_x((-self.rotation_speed))
        if key[pg.K_j]:
            self.rotate_y((self.rotation_speed))
        if key[pg.K_l]:
            self.rotate_y((-self.rotation_speed))
        if key[pg.K_u]:
            self.rotate_z((self.rotation_speed))
        if key[pg.K_o]:
            self.rotate_z((-self.rotation_speed))

        if key[pg.K_z]:
            self.scale((1.02))
        if key[pg.K_x]:
            self.scale((1 / 1.02))

        if key[pg.K_m]:
            self.start = True
            self.x = float(input('Коэффициент для x: '))
            self.y = float(input('Коэффициент для y: '))
            self.z = float(input('Коэффициент для z: '))
            print()

            self.t = 0


    def movement(self):
        if self.movement_flag:
            self.rotate_y(pg.time.get_ticks() % 0.005)

    def screen_projection(self):
        vertexes = self.vertexes @ self.render.camera.camera_matrix()
        vertexes = vertexes @ self.render.projection.projection_matrix
        vertexes /= vertexes[:, -1].reshape(-1, 1)
        vertexes[(vertexes > 3) | (vertexes < -3)] = 0
        vertexes = vertexes @ self.render.projection.to_screen_matrix
        vertexes = vertexes[:, :2]

        for index, color_edge in enumerate(self.color_edges):
            color, edge = color_edge
            polygon = vertexes[edge]
            if not np.any((polygon == self.render.H_WIDTH) | (polygon == self.render.H_HEIGHT)):
                pg.draw.polygon(self.render.screen, color, polygon, 2)
                if self.label:
                    text = self.font.render(self.label[index], True, pg.Color('white'))
                    self.render.screen.blit(text, polygon[-1])

        if self.draw_vertexes:
            for vertex in vertexes:
                if not np.any((vertex == self.render.H_WIDTH) | (vertex == self.render.H_HEIGHT)):
                    pg.draw.circle(self.render.screen, pg.Color('white'), vertex, 4)

    def translate(self, pos):
        self.vertexes = self.vertexes @ translate(pos)

    def dilatate(self, coefs):
        self.vertexes = self.vertexes @ dilatate(coefs)

    def scale(self, scale_to):
        self.vertexes = self.vertexes @ scale(scale_to)

    def rotate_x(self, angle):
        self.vertexes = self.vertexes @ rotate_x(angle)

    def rotate_y(self, angle):
        self.vertexes = self.vertexes @ rotate_y(angle)

    def rotate_z(self, angle):
        self.vertexes = self.vertexes @ rotate_z(angle)


class Axes(Object3D):
    def __init__(self, render):
        super().__init__(render)
        self.vertexes = np.array([(0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)])
        self.edges = np.array([(0, 1), (0, 2), (0, 3)])
        self.colors = [pg.Color('red'), pg.Color('green'), pg.Color('blue')]
        self.color_edges = [(color, edge) for color, edge in zip(self.colors, self.edges)]
        self.draw_vertexes = False
        self.label = 'XYZ'