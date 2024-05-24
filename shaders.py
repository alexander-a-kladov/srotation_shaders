#!/usr/bin/python3
import sys
from array import array

import pygame
import moderngl

pygame.init()

screen = pygame.display.set_mode((800, 800), pygame.OPENGL | pygame.DOUBLEBUF)
display = pygame.Surface((800, 800))
ctx = moderngl.create_context()

clock = pygame.time.Clock()

quad_buffer = ctx.buffer(data=array('f', [
    # position (x, y), uv coords (x, y)
    -1.0, 1.0, 0.0, 0.0,  # topleft
    1.0, 1.0, 1.0, 0.0,   # topright
    -1.0, -1.0, 0.0, 1.0, # bottomleft
    1.0, -1.0, 1.0, 1.0,  # bottomright
]))

vert_shader = '''
#version 330 core

in vec2 vert;
in vec2 texcoord;
out vec2 uvs;

void main() {
    uvs = texcoord;
    gl_Position = vec4(vert, 0.0, 1.0);
}
'''

frag_shader = '''
#version 330 core

uniform sampler2D tex;
uniform float angle;
uniform float scale;
uniform vec2 resolution;

in vec2 uvs;
out vec4 f_color;

vec2 rotate2D(vec2 uv, float a) {
 float s = sin(a);
 float c = cos(a);
 return mat2(c, -s, s, c) * uv;
}

vec2 scale2D(vec2 uv) {
 return scale*uv;
}

vec2 rotateDist2D(vec2 uv, float a) {
 float dist = sqrt(uv.x*uv.x+uv.y*uv.y);
 return rotate2D(uv, a*(0.2+dist));
}

void main() {
    vec2 sample_pos = rotate2D(scale2D(vec2(uvs.x-0.5, uvs.y-0.5)), -angle)+vec2(0.5,0.5);
    if (sample_pos.x > 1.0 || sample_pos.x < 0.0 || sample_pos.y > 1.0 || sample_pos.y < 0.0) {
        sample_pos = vec2(0.0, 0.0);
    } 
    f_color = vec4(texture(tex, sample_pos).rgb, 1.0);
}
'''

program = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
render_object = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

def surf_to_texture(surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
    tex.swizzle = 'BGRA'
    tex.write(surf.get_view('1'))
    return tex


if __name__ == "__main__":
    t = 0
    speed = 0.0
    angle = 0.0
    zoom = 1.0
    zoom_speed = 0
    MAX_SPEED = 180.0
    MAX_ZOOM_SPEED = 25
    MAX_ZOOM = 100.0
    MIN_ZOOM = 0.04
    
    if len(sys.argv)>1:
        image_name = sys.argv[1]
    else:
        image_name = "images/img.png"
        
    if len(sys.argv)>2:
        speed = float(sys.argv[2])
    else:
        speed = 0.0
        
    if speed < -180.0 or speed > 180.0:
        speed = 0.0
    
    pygame.display.set_caption(f'Zoom {round(1.0/zoom,3)} rotation speed {-speed} deg zoom_speed {-zoom_speed/100.0}')
    
    img = pygame.image.load(image_name)
    
    pygame.key.set_repeat(150)

    while True:
        display.fill((0, 0, 0))
        display.blit(img, (0,0))
    
        t += 1
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if speed < MAX_SPEED:
                        speed += 0.5
                elif event.key == pygame.K_RIGHT:
                    if speed > -MAX_SPEED:
                        speed -= 0.5
                elif event.key == pygame.K_DOWN:
                    if zoom_speed < MAX_ZOOM_SPEED:
                        zoom_speed += 1
                elif event.key == pygame.K_UP:
                    if zoom_speed > -MAX_ZOOM_SPEED:
                        zoom_speed -= 1
                elif event.key == pygame.K_SPACE:
                    speed = 0.0
                    zoom_speed = 0
        pygame.display.set_caption(f'Zoom {1.0/zoom:.3f} rotation speed {-speed} deg zoom_speed {-zoom_speed/100.0}')
        angle += speed
    
        if zoom > MIN_ZOOM and zoom < MAX_ZOOM:
            zoom += zoom_speed/100.0
        if zoom <= MIN_ZOOM:
            zoom_speed = 0
            zoom = MIN_ZOOM+0.1
        if zoom >= MAX_ZOOM:
            zoom_speed = 0
            zoom = MAX_ZOOM-0.1
    
        frame_tex = surf_to_texture(display)
        frame_tex.use(0)
        program['tex'] = 0
        program['angle'] = angle*(3.1415926535 / 180.0)
        program['scale'] = zoom
        render_object.render(mode=moderngl.TRIANGLE_STRIP)
    
        pygame.display.flip()
    
        frame_tex.release()
    
        clock.tick(25)
    
