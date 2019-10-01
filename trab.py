#!usr/bin/python3

import threading
import time
import random



#Variáveis Globais
N = 0   #número de boxes livres
maxB = 0    #max boxes
P = 0   #número de pessoas
genRestroom = -1    #gênero banheiro (-1 significa que está livre)
waitQueue = [[], [], []]    #fila de espera
counterGen = [0,0,0]    #contador para cada gênero
counterWait = [0,0,0]   #contador para o tempo de espera de cada gênero
ocupTime = 0    #tempo de ocupação do banheiro 

#variáveis para sincronizaçãp
semaphore = None
mutexGender = threading.Semaphore()     #mutex para acesso a variável genRestroom
genEvent = [threading.Event(),threading.Event(),threading.Event()]      #eventos que monitoram o gênero do banheiro

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
        global N, genRestroom, waitQueue, genCondition, mutexGender

        self.waitTime = time.time()       

        if genRestroom == -1:
            mutexGender.acquire()
            genRestroom = self.gender
            mutexGender.release()
            genEvent[self.gender].set()
            print("Banheiro Livre. Gênero do banheiro: {}.".format(genRestroom))

        if genRestroom != self.gender:
            waitQueue[self.gender].append(self)
            
            print("[FILA] Pessoa{} - Gênero: {} entrou na fila. Esperando gênero.".format(self.threadID, self.gender))

            print("Fila Gênero {}: [".format(self.gender),end="")
            for i in range(len(waitQueue[self.gender])):
                print("{} ".format(waitQueue[self.gender][i].threadID), end="")
            print("]")

            genEvent[self.gender].wait()
            print("Pessoa {} - {} acordei. Gênero do banheiro: {}.".format(self.threadID, self.gender, genRestroom))
            
        if N == 0:
            if self not in waitQueue[self.gender]:
                waitQueue[self.gender].append(self)
                print("[FILA] Pessoa {} - Gênero: {} entrou na fila. Esperando vaga.".format(self.threadID, self.gender))

                print("Fila Gênero {}: [".format(self.gender),end="")
                for i in range(len(waitQueue[self.gender])):
                    print("{} ".format(waitQueue[self.gender][i].threadID), end="")
                print("]")
            else: 
                print("[FILA] Pessoa {} - Gênero: {} esperando vaga.".format(self.threadID, self.gender))
        
        if self in waitQueue[self.gender] and genRestroom == self.gender:
            while waitQueue[self.gender].index(self) != 0:
                time.sleep(random.random())   
        
        self.getStall()

    def getStall(self):
    
        global N, genRestroom, waitQueue, ocupTime, semaphore, counterWait
        if genRestroom != self.gender:
            print("fail")
        
        semaphore.acquire()

        counterWait[self.gender] += time.time() - self.waitTime
       
        try:
            waitQueue[self.gender].remove(self)
        except(ValueError):
            pass

        N -= 1 
        
        print("[ENTRADA] Pessoa {} - Gênero {} entrando no box. --- {} boxes livres.".format(self.threadID, self.gender, N))
        
        if len(waitQueue[self.gender]) > 0:
            print("Fila Gênero {}: [".format(self.gender),end="")
            for i in range(len(waitQueue[self.gender])):
                print("{} ".format(waitQueue[self.gender][i].threadID), end="")
            print("]")
        
        time.sleep(5)
        if N==maxB-1:
            ocupTime += 5

        N += 1
       
        print("[SAÍDA] Pessoa {} - Gênero {} saindo do box. --- {} boxes livres.".format(self.threadID, self.gender, N))
        
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
            print("Trocou gênero. Novo gênero: {}. {}   {}".format(genRestroom, genRestroom-1, genRestroom-2))
            mutexGender.release()
    
    def run(self):
        
        print("[CHEGADA] Pessoa{} - Gênero {} chegou no banheiro.".format(self.threadID, self.gender))
        self.enterRestroom()

def init():
    global N, P, maxB, semaphore, genEvent 
   
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

    maxB = N
    semaphore = threading.Semaphore(N)
    for i in genEvent:
        i.clear()
    print("\n\n")
        
def main():
    
    global ocupTime, counterWait, N, P

    threadID = 1
    threadList = []

    init()
    tempoExec = time.time()

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

    tempoExec = time.time() - tempoExec
    print("\n\n############")
    print("Tempo de execução: {}min {:.2f}s".format(int(tempoExec/60),tempoExec%60))
    for i in range(3):
        print("Pessoas do Gênero {}: {}. Tempo médio de espera: {}min{:.2f}s".format(i,counterGen[i],int((counterWait[i]/counterGen[i])/60), (counterWait[i]/counterGen[i])%60))
    print("Taxa de Ocupação: {:.2f}%.".format(ocupTime*100/tempoExec))

if __name__ == "__main__":
    main()