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

empty = threading.Event()
genEvent = [threading.Event(),threading.Event(),threading.Event()]

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
        global N, genRestroom, waitQueue, ocupTime, empty, genCondition
       
        if genRestroom == -1:
            genRestroom = self.gender
            genEvent[self.gender].set()
            print("Gênero banheiro: {}.".format(genRestroom))

        if genRestroom == self.gender and N > 0:
            self.getStall()

        elif N == 0 and genRestroom == self.gender:
            waitQueue[self.gender].append(self)
            print("Pessoa{} - {} entrou na fila. Esperando box esvaziar.".format(self.threadID,self.gender))
            empty.wait()
        
        elif genRestroom != self.gender:
            waitQueue[self.gender].append(self)
            print("Pessoa{} - {} entrou na fila. Esperando gênero.".format(self.threadID, self.gender))
            genEvent[self.gender].wait()

    def getStall(self):
    
        global N, genRestroom, waitQueue, ocupTime, empty, genCondition

        self.waitTime = time.time() - self.waitTime
        counterWait[self.gender] += self.waitTime
        N -= 1
        print("[{}] Pessoa{} - {} entrando no box. --- {} boxes livres.".format(genRestroom, self.threadID, self.gender, N))
        if N == 0:
            empty.clear()
        try:
            waitQueue[self.gender].remove(self)
        except(ValueError):
            pass
        time.sleep(5)
        ocupTime += 5
        N += 1
        print("Pessoa{} - {} saindo do box. --- {} boxes livres.".format(self.threadID, self.gender, N))
        empty.set()
        self.leaveRestroom()

    def leaveRestroom(self):

        global N, genRestroom, waitQueue, maxB

        if N == maxB and len(waitQueue[self.gender]) == 0:
            if self.gender == 0:

                if len(waitQueue[1]) == 0 and len(waitQueue[2]) == 0: 
                    genRestroom = -1
                    genEvent[0].clear()
                    genEvent[1].clear()
                    genEvent[2].clear()

                elif len(waitQueue[1]) == 0:
                    genRestroom = 2
                    genEvent[2].set()
                    genEvent[1].clear()
                elif len(waitQueue[2]) == 0:
                    genRestroom = 1
                    genEvent[1].set()
                    genEvent[2].clear()

                else:
                    if waitQueue[1][0].waitTime < waitQueue[2][0].waitTime:
                        genRestroom = 1
                        genEvent[1].set()
                        genEvent[2].clear()
                    else:
                        genRestroom = 2
                        genEvent[2].set()
                        genEvent[1].clear()

            elif self.gender == 1:

                if len(waitQueue[0]) == 0 and len(waitQueue[2]) == 0: 
                    genRestroom = -1
                    genEvent[0].clear()
                    genEvent[1].clear()
                    genEvent[2].clear()

                elif len(waitQueue[0]) == 0:
                    genRestroom = 2
                    genEvent[2].set()
                    genEvent[0].clear()
                elif len(waitQueue[2]) == 0:
                    genRestroom = 0
                    genEvent[0].set()
                    genEvent[2].clear()

                else:
                    if waitQueue[0][0].waitTime < waitQueue[2][0].waitTime:
                        genRestroom = 0
                        genEvent[0].set()
                        genEvent[2].clear()
                    else:
                        genRestroom = 2
                        genEvent[2].set()
                        genEvent[0].clear()

            elif self.gender == 2:
                if len(waitQueue[0]) == 0 and len(waitQueue[1]) == 0: 
                    genRestroom = -1
                    genEvent[0].clear()
                    genEvent[1].clear()
                    genEvent[2].clear()

                elif len(waitQueue[1]) == 0:
                    genRestroom = 0
                    genEvent[0].set()
                    genEvent[1].clear()
                elif len(waitQueue[0]) == 0:
                    genRestroom = 1
                    genEvent[1].set()
                    genEvent[0].clear()

                else:
                    if waitQueue[1][0].waitTime < waitQueue[0][0].waitTime:
                        genRestroom = 1
                        genEvent[1].set()
                        genEvent[0].clear()
                    else:
                        genRestroom = 0
                        genEvent[0].set()
                        genEvent[1].clear()

            print("Trocou gênero. Novo gênero: {}.".format(genRestroom))


    def run(self):
        print("Pessoa{} - {} chegou no banheiro.".format(self.threadID, self.gender))
        self.enterRestroom()
        #self.getStall()

def menu():
    global N, P, maxB
   
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
        P = 30 
    elif op == 3: 
        N = 5 
        P = 200

    maxB = N
    semaphore = threading.Semaphore(N)
    print("\n\n")
        
def main():
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

    tempoExec = time.time() - tempoExec
    print("\n\n############")
    print("Tempo de execução: {}min {:.2f}s".format(int(tempoExec/60),tempoExec%60))
    for i in range(3):
        print("Pessoas do Gênero {}: {}. Tempo médio de espera: {}min{:.2f}s".format(i,counterGen[i],int((counterWait[i]/counterGen[i])/60), (counterWait[i]/counterGen[i])%60))
    print("Taxa de Ocupação: {:.2f}%".format(ocupTime/tempoExec))
if __name__ == "__main__":
    main()