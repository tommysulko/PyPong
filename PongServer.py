from tokenize import Double
import pygame, sys
from threading import Thread
import time 
import serial
import threading, queue
import keyboard
import socket
import random
#------------------------Conf. Python---------------------------

clock = pygame.time.Clock()
screen = pygame.display.set_mode((500, 500))
icon = pygame.image.load("C:/Users/mattia/Documents/3A/SISTEMI/python/GiocoConSocketPong/icon.png")
sfondo = pygame.image.load("C:/Users/mattia/Documents/3A/SISTEMI/python/GiocoConSocketPong/sfondo.png")

sfondo=pygame.transform.scale(sfondo,(500,500))
pygame.display.set_icon(icon)
pygame.display.set_caption("Pong Sparla e Sulko ")
pygame.init()
musicaSfondo = pygame.mixer.Sound("C:/Users/mattia/Documents/3A/SISTEMI/python/GiocoConSocketPong/Sound_SoundMenu.mp3")
Error_sound = pygame.mixer.Sound("C:/Users/mattia/Documents/3A/SISTEMI/python/GiocoConSocketPong/Microsoft Windows XP Error - Sound Effect (HD).mp3")
Error_sound.set_volume(5.00)

musicaSfondo.set_volume(0.30)
hitSound = pygame.mixer.Sound("C:/Users/mattia/Documents/3A/SISTEMI/python/GiocoConSocketPong/Sound_Hitsound.mp3")

#------------------------Colore---------------------------

BIANCO = (255, 255, 255)

#------------------------Variabili Globali utili per il gioco---------------------------
# qui abbiamo le coordinate dle giocatore 1 e del giocatore 2

x1 = (490)
y1 = 250
x2 = (0)
y2 = 250

# le coordinate della palla
xb = 500
yb = 300
speedball = 10

# direzione orizzontale e verticale della palla
dbo = 0 #sinistra
dbv = 0 #sotto

# il punteggio dei due giuocatori
scorep1 = 0
scorep2 = 0
t=0

#------------------------Thread Per Leggere dal Micro:bit---------------------------
dt=50
gamma = 0.05
q = queue.Queue()   #Creo la coda

class Read_Microbit(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._running = True

    def terminate(self):
        self._running = False
        
    def run(self):
        #serial config
        port = "COM7"  #Porta del microbit da controllare ogni volta
        s = serial.Serial(port)
        s.baudrate = 115200
        while self._running:
            data = s.readline().decode() 
            acc = [float(x) for x in data[1:-3].split(",")]
            q.put(acc)     #metto i dati che leggo nella coda
            time.sleep(0.01)

#------------------------Funz. Per la lettura---------------------------

def CalcolaAcc(speed):
        acc = q.get()   #Prendo l'head dalla coda, ovvero l'accelerazione 
        speed[0] = (1.-gamma)*speed[0] + dt*acc[0]/1024. #x di microbit converita 
        speed[1] = (1.-gamma)*speed[1] + dt*acc[1]/1024. #y microbit convertita
        q.task_done()
        return speed[1]  #restituisco la y che è quella che mi serve

#------------------------MainThread (Thread Gioco)---------------------------

class MainThread (Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.ok=0
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  #creo il socket
        #SOCK_STREAM = TCP
        self.s.bind(("172.20.10.4",8000)) #indirizzo del server
        self.s.listen()     #Rimango in ascolto fino a quando il client non si collega
        print("In attesa di conessione...")
        self.connection,self.address = self.s.accept()

    def run(self):
        while self.running:
            speed = [0,0]
            loop = 1
            while loop:
                screen.blit(sfondo,(0,0))
                
                yServer = CalcolaAcc(speed) #y microbit Server
                data = self.connection.recv(4096)

                YSTring=data.decode() #stringa dell altro microbit mandata tramite socket
                listaY = YSTring.split(".") #faccio un split e leggo il primo valore che è quello corretto
                yInt=int(listaY[0]) #Faccio il cast alla stringa inviata dal client

                self.move_ball(xb, yb)
                self.ball()

                
                self.sprite1(yServer) #racchetta 1 gli passo le coordinate y di micorbit server
                self.sprite2(yInt) #racchetta 2 gli passo quelle del socket
                self.collision(yServer,yInt)

                pygame.display.update()
                screen.fill((255,225,226))  
                clock.tick(60)

                if(self.ok == 10):
                    loop=0

            self.connection.close() #se finisce il ciclo chiudo la connessione con il socket
            pygame.quit()   #Fine del gioco
            sys.exit(0)

    #tutte le funzioni-->
    def ball(self):
        "Disegna la palla"
        global xb, yb
        pygame.draw.ellipse(screen, BIANCO, (xb, yb, 10, 10))
    
    def sprite1(self,y): # x e y sono le posizioni del microbit
        "Disegna il giocatore 1"
        pygame.draw.rect(screen, BIANCO, (x1, y, 10, 70))
    
    def sprite2(self,y):
        "Disegna il giocatore 2"
        pygame.draw.rect(screen, BIANCO, (x2, y, 10, 70))
    
    def move_ball(self,x,y):
        "I movimenti della palla"
        global xb, yb, dbo, dbv, speedball
        if dbo == 0:
            xb -= speedball
            #hitSound.play()
        if dbv == 0:
            yb += speedball
            #hitSound.play()
            if yb > 490:
                dbv = 1
        if dbv:
            yb -= speedball
            #hitSound.play()
            if yb < speedball:
                dbv = 0
        if dbo:
            xb += speedball
           # hitSound.play()
	
    def collision(self,yS,YC):
        global x1, y1 # giocatore 1 x e y (sulla destra)
        global x2, y2 # giocatore 2 x e y (sulla sinistra)
        global xb, yb # la palla x e y
        global x, y
        global dbo
        global scorep1, scorep2

        if dbo:
            if xb > 480:
                if yb >= yS-10 and  yb < yS + 80:
                    dbo = 0		
                else:
                    Error_sound.play()
                    self.ok+=1
                    xb, yb,scorep1 = 10, 20,scorep1+10
                    pygame.display.update()
                    pygame.time.delay(500)
                    print(f"G1:{scorep1} | G2:{scorep2}")
                    #restart()
    
        else:
            if xb < 10:
                if yb >= YC-10 and  yb < YC + 80:
                    dbo = 1
                else:
                    Error_sound.play()
                    self.ok+=1
                    xb, yb,scorep2 = 480, 20,scorep2+10
                    pygame.display.update()
                    pygame.time.delay(500)
                    print(f"G1:{scorep1} | G2:{scorep2}")

    def stop(self):
        self.running = False

#------------------------Main---------------------------

def main():   
    pygame.mouse.set_visible(False)  #tolgo la visibilità del mouse    
    t=MainThread() #inizializzo e starto il thread principale
    musicaSfondo.play(-1)
    t.start()   #start del Thread
    rm = Read_Microbit()  #inizializzo anche il thread microbit
    rm.start()  #start del Thread
    
if __name__ == "__main__":
    main()

