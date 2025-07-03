import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from noise import pnoise2
import numpy as np

#PARAMETERS
angle = 0
sample1 = [
    ([0, 1, 0], [1, 0, 0]),
    ([-1, -1, 0], [0, 1, 0]),
    ([1, -1, 0], [0, 0, 1])
]

def draw_triangle(vertices):
    glBegin(GL_TRIANGLES)
    for position, color in vertices:
        glVertex3fv(position)
        glColor3fv(color)
    glEnd()

# Set up window and context
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
clock = pygame.time.Clock()

#Set perspective and view
#set camera: deg FOV, aspect ratio, near clipping plane, far clipping plane
gluPerspective(45, (display[0] / display[1]), 0.5, 50)
glTranslatef(0.0, 0.0, -5)
glShadeModel(GL_SMOOTH)

#Game/Render Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPushMatrix() #save current transformation state
    glRotatef(angle, 0, 1, 0)
    draw_triangle(sample1)
    glPopMatrix()       #restore state (prevents accumulated rotation)

    pygame.display.flip() #swap buffers (double buffering)
    delta_time = clock.tick(60) / 1000  # milliseconds → seconds
    angle += 45 * delta_time   

pygame.quit()
