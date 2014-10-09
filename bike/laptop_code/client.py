import pygame
import pickle
from net_threads import *
from Queue import Queue
from time import sleep
import marshal
import math

from random import randint

push_queue = Queue()
push_thread = PushThread(push_queue, '192.168.1.2', 9000)
push_thread.start()

pull_queue = Queue()
pull_thread = PullThread(pull_queue, 9001)
pull_thread.start()

BLACK    = (   0,   0,   0)
WHITE    = ( 208, 208, 208)
GREEN    = (   0, 255,   0)

GREY     = (  35,  35,  35)
RED      = ( 209,  72,  54)

r = 0

def txtprint(screen, txtstr, x, y, color):
    bmp = pygame.font.Font(None, 20).render(txtstr, True, color)
    screen.blit(bmp, [x,y])
    

def draw_pushed_data(x,y):
    txtprint(screen, "--- To Bicycle ---", x, y, RED)
    txtprint(screen, "Reference angle (degrees): r = " + str(r), x, y+14, RED)


def draw_pulled_data(x,y):
    txtprint(screen, "--- From Bicycle ---", x,y, RED)
    txtprint(screen, "IMU data:  = 12312" + str(r), x, y+14, RED)

class Leaner:
    def __init__(self,screen,name,x,y,w,h,coords):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.coords = coords
        self.tcoords = coords
        self.title_bitmap = fontz[0].render(self.name, True, RED)
        self.tilt = 0

    def setangle(self,val):

        self.tilt = val
        val =val / 57.296
        self.tcoords = []

        for i in range(0, len(self.coords)):

            r = math.sqrt(self.coords[i][0]**2 + self.coords[i][1]**2)
            angle = math.atan2(self.coords[i][1],self.coords[i][0])
            self.tcoords += [(self.x + self.w/2 + math.cos(val+angle)*r, self.y + self.h/2 + -math.sin(val+angle)*r)]
            
    #    print self.tcoords



    def render(self, screen):
        #Draw border:
        x=self.x
        y=self.y
        w=self.w
        h=self.h
        pygame.draw.line(screen, WHITE, (x,y), (x+w, y),2)
        pygame.draw.line(screen, WHITE, (x+w, y), (x+w, y+h),2)
        pygame.draw.line(screen, WHITE, (x+w, y+h), (x, y+h),2)
        pygame.draw.line(screen, WHITE, (x, y+h), (x, y),2)

        #Draw Title
        screen.blit(self.title_bitmap,[self.x+4, self.y])

        

        text_print(screen,0,(x+4,y + 32), str(self.tilt))

        for i in range(0,len(self.tcoords)-1):
            pygame.draw.line(screen, WHITE, self.tcoords[i], self.tcoords[i+1])

        pygame.draw.line(screen,WHITE,self.tcoords[len(self.tcoords)-1],self.tcoords[0])



class Rotoslider:
    def __init__(self,x,y,r,dr,numblox,oncolor,offcolor):
        self.x = x
        self.y = y
        self.r = r
        self.dr = dr
        self.numblox = numblox
        self.oncolor = oncolor
        self.offcolor = offcolor
        self.val = 0
        self.ratio = .60

    def setval(self,inval):
        self.val = inval

    def render(self,screen):
        for i in range(0, self.numblox):
            if self.val > i*100/self.numblox:
                col = self.offcolor
            else:
                col = self.oncolor

            theta = i * math.pi / self.numblox       

            r=self.r
            dr = self.dr
            dt = self.ratio * math.pi / self.numblox
            bl = (self.x + r*math.cos(theta), self.y - r*math.sin(theta))
            br = (self.x + r*math.cos(theta+dt), self.y - r*math.sin(theta+dt))
            tl = (self.x + (r+dr)*math.cos(theta), self.y - (r+dr)*math.sin(theta))
            tr = (self.x + (r+dr)*math.cos(theta+dt), self.y - (r+dr)*math.sin(theta+dt))

            pygame.draw.polygon(screen, col, (bl,br,tr,tl), 0)
            
    

class Graph:
    def __init__(self,screen,name,x,y,w,h,numsamples,minmax):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.numsamples = numsamples
        self.samples = [0]*numsamples
        self.minmax = minmax
        self.title_bitmap = fontz[0].render(self.name, True, RED)

    def clip(self,val):

        if val > self.h/2: 
            val = self.h/2

        elif val < -1*self.h/2: 
            val = -1*self.h/2

        return val


    def render(self,screen):
        #Draw border:
        x=self.x
        y=self.y
        w=self.w
        h=self.h
        pygame.draw.line(screen, WHITE, (x,y), (x+w, y),2)
        pygame.draw.line(screen, WHITE, (x+w, y), (x+w, y+h),2)
        pygame.draw.line(screen, WHITE, (x+w, y+h), (x, y+h),2)
        pygame.draw.line(screen, WHITE, (x, y+h), (x, y),2)

        #Draw Title
        screen.blit(self.title_bitmap,[self.x+4, self.y])
        
        #Draw samples:
        ctr = self.y + self.h/2
        xx = -1
        yy = -1
        xxold = xx
        yyold = yy

        for i in range(0,self.numsamples):

            #minus sign in following expression because all 2d video games are programmed upside-down
            xxold = xx
            yyold = yy
            xx = int (i * (self.w / self.numsamples)) + self.x
            yy = int(ctr - self.clip(self.h*self.samples[i]/self.minmax))  
            
            pygame.draw.circle(screen, RED, (xx,yy),  2, 0)
            
            if i > 0:
                pygame.draw.line(screen, RED, (xxold,yyold),(xx,yy))
           
    def push(self,val):
        self.samples = self.samples[1:] + [val]


pygame.init()
 
# Set the width and height of the screen [width,height]
size = [1366, 768]
screen = pygame.display.set_mode(size,pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)

pygame.display.set_caption("Bicycle Command")
done = False
clock = pygame.time.Clock()

joy = False
if pygame.joystick.get_count():
    joy = True


pygame.font.init()
font_path = "./font.ttf"
font_sizeS = 32
font_sizeM = 48
font_sizeL = 64
fontz = [pygame.font.Font(font_path, font_sizeS),pygame.font.Font(font_path, font_sizeM),pygame.font.Font(font_path, font_sizeL)]

def text_print(screen,size,location,string):
    bmp = fontz[size].render(string, True, RED)
    screen.blit(bmp, location)


if joy:
    pygame.joystick.init()
    if(pygame.joystick.get_count()):
        the_joystick = pygame.joystick.Joystick(0)
        the_joystick.init()

phi = 0
dell = 0
bat = 0

phigraph = Graph(screen,"phi",10,10,750,275,50,90)
deltagraph = Graph(screen,"delta",10,300,750,275,50,50)
phileaner = Leaner(screen,"phi", 775, 10, 300, 275, [(10,0),(-10,0),(-10,77),(10,77)])
deltaleaner = Leaner(screen,"delta", 775, 300, 300, 275, [(10,0),(-10,0),(-10,77),(10,77)])
rslider = Rotoslider(683,768,100,10,30,RED,WHITE)

while done==False:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            done=True 
            pull_thread.stop()
            push_thread.stop()
        elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_ESCAPE:
                   pygame.quit()
                   

    screen.fill(GREY)

    phigraph.push(phi)
    phigraph.render(screen)

    deltagraph.push(dell-90)
    deltagraph.render(screen)

    phileaner.setangle(phi)
    phileaner.render(screen)

    deltaleaner.setangle(dell-90)
    deltaleaner.render(screen)

    rslider.setval(50+r)
    rslider.render(screen)
    text_print(screen,0,(620, 720), "r = " + str(r)[:5])

    if joy:
        r = the_joystick.get_axis(0)*-50
    
    pygame.display.flip()

    clock.tick(40)

    out_data = {'r':11*r/50,'m':1}
    push_queue.put(marshal.dumps(out_data))

    if(pull_queue.qsize()):
        telemetry = marshal.loads(pull_queue.get())
        phi = telemetry['phi']
        dell = telemetry['del']
        bat = telemetry['bat']

pygame.quit ()

