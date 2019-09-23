#!usr/bin/python3

import threading
import time
import random

N = 0   #número de boxes livres
maxB = 0    #max boxes
P = 0   #número de pessoas
genRestroom = -1    #gênero banheiro
waitQueue = [[], [], []]    #fila de espera
counterGen = [0,0,0]    #contador para cada gênero
counterWait = [0,0,0]
ocupTime = 0

log = [open("logP0.txt", 'a'), open("logP1.txt", 'a'), open("logP2.txt", 'a')]

semaphore = None
mutexGender = threading.Semaphore()
genEvent = [threading.Event(),threading.Event(),threading.Event()]
openBox = threading.Event()

class Person(threading.Thread):

    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.gender = self.genGender()
        self.waitTime = time.time()

    def genGender(self):
        random.seed()
        gender = random.randint(0,2)
        
        while(counterGen[gender] >= P/3):
            gender = random.randint(0,2)
        
        counterGen[gender]+=1
        
        return gender

    def enterRestroom(self):
        global N, genRestroom, waitQueue, genCondition, mutexGender, log
       
        if genRestroom == -1:
            mutexGender.acquire()
            genRestroom = self.gender
            mutexGender.release()
            genEvent[self.gender].set()
            print("Gênero banheiro: {}.".format(genRestroom))

        if genRestroom != self.gender:
            waitQueue[self.gender].append(self)
            print("[FILA] Pessoa{} - Gênero: {} entrou na fila. Esperando gênero.".format(self.threadID, self.gender))
            log[self.gender].write("Pessoa{} entrou na fila no tempo:{}.\n".format(self.threadID, int(time.time())))
            genEvent[self.gender].wait()
           

        if genRestroom == self.gender and N == 0:
            waitQueue[self.gender].append(self)
            print("[FILA] Pessoa{} - Gênero: {} entrou na fila. Esperando vaga.".format(self.threadID, self.gender))
            log[self.gender].write("Pessoa{} entrou na fila no tempo:{}.\n".format(self.threadID, int(time.time())))
            openBox.wait()
           
        self.getStall()     

    def getStall(self):
    
        global N, genRestroom, waitQueue, ocupTime, semaphore
        
        semaphore.acquire()

        self.waitTime = time.time() - self.waitTime
        counterWait[self.gender] += self.waitTime
       
        try:
            waitQueue[self.gender].remove(self)
        except(ValueError):
            pass

        N -= 1    
        if N == 0:
            openBox.clear() 
        

        print("[ENTRADA] Pessoa{} - {} entrando no box. --- {} boxes livres.".format(self.threadID, self.gender, N))
        log[self.gender].write("Pessoa{} entrou no box no tempo:{}.\n".format(self.threadID, int(time.time())))        
        
        
        time.sleep(5)
        ocupTime += 5

        N += 1
        if N>=1:
            openBox.set()
       
        print("[SAÍDA] Pessoa{} - {} saindo do box. --- {} boxes livres.".format(self.threadID, self.gender, N))
        log[self.gender].write("Pessoa{} saiu do box no tempo:{}.\n".format(self.threadID, int(time.time()))) 
        self.leaveRestroom()
        
        semaphore.release()


    def genderTurn(self): 
        global genEvent, waitQueue
        
        if len(waitQueue[self.gender-1]) == 0 and len(waitQueue[self.gender-2]) == 0:
            return -1

        elif len(waitQueue[self.gender-1]) == 0 and len(waitQueue[self.gender-2]) > 0:
            return waitQueue[self.gender-2][0].gender
        
        elif len(waitQueue[self.gender-1]) > 0 and len(waitQueue[self.gender-2]) == 0:
            return waitQueue[self.gender-1][0].gender
        
        else: 
            if waitQueue[self.gender-1][0].waitTime < waitQueue[self.gender-2][0].waitTime:
                return waitQueue[self.gender-1][0].gender
            else: 
                return waitQueue[self.gender-2][0].gender
        return -1

    def leaveRestroom(self):

        global N, genRestroom, waitQueue, mutexGender

        #troca de gêneros, caso não tenha ninguém do mesmo gênero da thread atual na fila
        if N == maxB and len(waitQueue[self.gender]) == 0:
            mutexGender.acquire()
            genRestroom = self.genderTurn()
            genEvent[genRestroom].set()
            genEvent[genRestroom-1].clear()
            genEvent[genRestroom-2].clear()
            print("Trocou gênero. Novo gênero: {}.".format(genRestroom))
            mutexGender.release()

    def run(self):
        global log
        print("[CHEGADA] Pessoa{} - {} chegou no banheiro.".format(self.threadID, self.gender))
        log[self.gender].write("Pessoa{} chegou no banheiro no tempo: {}.\n".format(self.threadID, int(time.time())))
        self.enterRestroom()

def menu():
    global N, P, maxB, semaphore
   
    print("#######################")
    print("1 - 1 box e 60 pessoas")
    print("2 - 3 boxes e 150 pessoas")
    print("3 - 5 boxes e 200 pessoas")
    op = int(input("opção: "))
    while (op != 1 and op != 2 and op != 3):
       print("Invalido!")
       op = input("opção: ")
    
    if op == 1:
        N = 1
        P = 60
    elif op == 2:
        N = 3
        P = 150 
    elif op == 3: 
        N = 5 
        P = 200

    maxB = N
    semaphore = threading.Semaphore(N)
    print("\n\n")
        
def main():
    global log
    
    tempoExec = time.time()
    threadID = 1
    threadList = []

    menu()

    print("{} boxes e {} Pessoas".format(N, P))
    for i in range(P):
        
        random.seed()
        t = random.randint(1,7)
        myThread = Person(threadID)
        threadList.append(myThread)
        myThread.start()
        time.sleep(t)
        threadID += 1
           
    for t in threadList:
        t.join()

    for i in log:
        i.close()
    tempoExec = time.time() - tempoExec
    print("\n\n############")
    print("Tempo de execução: {}min {:.2f}s".format(int(tempoExec/60),tempoExec%60))
    for i in range(3):
        print("Pessoas do Gênero {}: {}. Tempo médio de espera: {}min{:.2f}s".format(i,counterGen[i],int((counterWait[i]/counterGen[i])/60), (counterWait[i]/counterGen[i])%60))
    print("Taxa de Ocupação: {:.2f}".format(ocupTime/tempoExec))

if __name__ == "__main__":
    main()