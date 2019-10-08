#!usr/bin/python3

import threading
import time
import random

#Variáveis Globais
waitQueue = [[], [], []]    #fila de espera
counterGen = [0,0,0]    #contador para cada gênero
counterWait = [0,0,0]   #contador para o tempo de espera de cada gênero
bathroom = None
P = 0

#variáveis para sincronizaçãp
mutexGender = threading.Semaphore()     #mutex para acesso a variável genRestroom
genEvent = [threading.Event(),threading.Event(),threading.Event()]      #eventos que monitoram o gênero do banheiro

class Bathroom(threading.Thread):
    
    def __init__(self, N):
        threading.Thread.__init__(self)
        self.N = N
        self.maxB = N
        self.ocupTime = 0
        self.semaphore = threading.Semaphore(N)
        self.genRestroom = -1
        self.tempoExec = 0
    
    def run(self):
        global P
        
        self.tempoExec = time.time()
        
        threadID = 1
        threadList = []

        print("{} boxes e {} Pessoas".format(self.N, P))

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

        self.tempoExec = time.time() - self.tempoExec


class Person(threading.Thread):

    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.gender = self.genGender()
        self.waitTime = 0

    def genGender(self):
        random.seed()
        gender = random.randint(0,2)
        while(counterGen[gender] >= P/3):
            gender = random.randint(0,2)
        counterGen[gender]+=1
        return gender

    def enterRestroom(self):
        global bathroom, waitQueue, genCondition, mutexGender

        self.waitTime = time.time()      
        
        if bathroom.genRestroom == -1:
            mutexGender.acquire()
            bathroom.genRestroom = self.gender
            mutexGender.release()
            genEvent[self.gender].set()
            genEvent[self.gender-1].clear()
            genEvent[self.gender-2].clear()
            print("Banheiro Livre. Gênero do banheiro: {}.".format(bathroom.genRestroom))

        elif bathroom.genRestroom != self.gender:
            waitQueue[self.gender].append(self)
            
            print("[FILA] Pessoa{} - Gênero: {} entrou na fila.".format(self.threadID, self.gender))

            print("Fila Gênero {}: [".format(self.gender),end="")
            for i in range(len(waitQueue[self.gender])):
                print("{} ".format(waitQueue[self.gender][i].threadID), end="")
            print("]")

            genEvent[self.gender].wait()
            
        if bathroom.N == 0:
            if self not in waitQueue[self.gender]:
                waitQueue[self.gender].append(self)
                print("[FILA] Pessoa {} - Gênero: {} entrou na fila.".format(self.threadID, self.gender))

                print("Fila Gênero {}: [".format(self.gender),end="")
                for i in range(len(waitQueue[self.gender])):
                    print("{} ".format(waitQueue[self.gender][i].threadID), end="")
                print("]")
        
        if self in waitQueue[self.gender]:
            while waitQueue[self.gender].index(self) != 0:
                time.sleep(random.random())   
        
        self.getStall()

    def getStall(self):
    
        global bathroom, waitQueue, counterWait
        
        bathroom.semaphore.acquire()
        counterWait[self.gender] += time.time() - self.waitTime
        try:
            waitQueue[self.gender].remove(self)
        except(ValueError):
            pass

        bathroom.N -= 1 
        
        print("[ENTRADA] Pessoa {} - Gênero {} entrando no box. --- {} boxes livres.".format(self.threadID, self.gender, bathroom.N))
        
        if len(waitQueue[self.gender]) > 0:
            print("Fila Gênero {}: [".format(self.gender),end="")
            for i in range(len(waitQueue[self.gender])):
                print("{} ".format(waitQueue[self.gender][i].threadID), end="")
            print("]")
        
        time.sleep(5)
        if bathroom.N == (bathroom.maxB-1):
            bathroom.ocupTime += 5

        bathroom.N += 1
       
        self.leaveRestroom()
        
        bathroom.semaphore.release()

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

        global bathroom, waitQueue, mutexGender
        
        print("[SAÍDA] Pessoa {} - Gênero {} saindo do box. {} boxes livres.".format(self.threadID, self.gender, bathroom.N))

        #troca de gêneros, caso não tenha ninguém do mesmo gênero da thread atual na fila
        if bathroom.N == bathroom.maxB and len(waitQueue[self.gender]) == 0:
            mutexGender.acquire()
            bathroom.genRestroom = self.genderTurn()
            if bathroom.genRestroom != -1:
                genEvent[bathroom.genRestroom].set()
                genEvent[bathroom.genRestroom-1].clear()
                genEvent[bathroom.genRestroom-2].clear()
            print("Trocou gênero. Novo gênero: {}.".format(bathroom.genRestroom, bathroom.genRestroom-1, bathroom.genRestroom-2))
            mutexGender.release()
    
    def run(self):
        
        print("[CHEGADA] Pessoa{} - Gênero {} chegou no banheiro.".format(self.threadID, self.gender))
        self.enterRestroom()

def init():
    global bathroom, P
    N = 0
    print("#######################")
    print("1 - 1 box e 60 pessoas")
    print("2 - 3 boxes e 150 pessoas")
    print("3 - 5 boxes e 300 pessoas")
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
        P = 300

    bathroom = Bathroom(N)
    bathroom.start()
    bathroom.join()

    print("\n\n")
        
def main():
    
    global bathroom, counterWait, P

    init()
    
    print("\n\n############")
    print("Tempo de execução: {}min {:.2f}s".format(int(bathroom.tempoExec/60),bathroom.tempoExec%60))
    for i in range(3):
        print("Pessoas do Gênero {}: {}. Tempo médio de espera: {}min{:.2f}s".format(i,counterGen[i],int((counterWait[i]/counterGen[i])/60), (counterWait[i]/counterGen[i])%60))
    print("Taxa de Ocupação: {:.2f}%.".format(bathroom.ocupTime*100/bathroom.tempoExec))

if __name__ == "__main__":
    main()