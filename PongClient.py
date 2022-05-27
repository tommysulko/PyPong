from threading import Thread
import time 
import serial
import threading, queue
import socket

#--------------Thread Lettura-------------------------
dt=50   #variabile per calcolare Y del gioco dal micro:bit
gamma = 0.05    #variabile per calcolare Y del gioco dal micro:bit
q = queue.Queue()   #Creo una coda

class Read_Microbit(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._running = True

    def terminate(self):
        self._running = False
        
    def run(self):
        #serial config
        port = "COM12"   #Porta del microbit da controllare ogni volta
        s = serial.Serial(port)
        s.baudrate = 115200
        while self._running:
            data = s.readline().decode() 
            acc = [float(x) for x in data[1:-3].split(",")]
            q.put(acc)  #Inserisco nella coda l'accelerazione letta dal micro:bit
            time.sleep(0.01)

#--------------Funz. CalcolaAcc -------------------------

def CalcolaAcc(speed):
        acc = q.get()    #Prendo l'head dalla coda, ovvero l'accelerazione 
        speed[0] = (1.-gamma)*speed[0] + dt*acc[0]/1024.
        speed[1] = (1.-gamma)*speed[1] + dt*acc[1]/1024.
        q.task_done()
        return speed[1]   #restituisco la y che è quella che mi serve

#--------------Thread Socket-------------------------

class ThreadSocket (Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)     #creo il socket
        self.s.connect(("172.20.10.4",8000))    #mi connetto con l'indirizzo del server

    def run(self):
        while self.running:
            speed = [0,0]   #speed[0] = X, speed[1] = Y
            loop = 1
            while loop:
                yInt = CalcolaAcc(speed)    #Richiamo la funzione per calcolare l'accelerazione
                y = str(yInt)       #Faccio il cast ad yInt per inviarlo poi al server
                self.s.sendall(y.encode())      #A tutti mando la mia posizione y
            self.s.close()       #chiudo il socket

#--------------Main-------------------------

def main():      
    t=ThreadSocket()    #inizializzo anche il thread per il socket
    t.start()   #start del Thread
    rm = Read_Microbit()    #inizializzo anche il thread microbit
    rm.start()  #start del Thread
    
if __name__ == "__main__":
    main()