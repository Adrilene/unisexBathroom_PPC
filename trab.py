#!/usr/bin/python3

import threading
import time
import random

random.seed(time.time())

N = 0  #número de boxes livres
P = 0 #número de pessoas
gen_restroom = -1   #gênero que está no banheiro
fila_gen = [[],[],[]]
counterGen = [0,0,0]   #conta as quantidades de pessoas de cada gênero
counterWait = [0,0,0]
ocupTime = 0

lock = threading.Lock()

class PersonThread(threading.Thread):
    def __init__(self, threadID, gender):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.gender = gender
        self.timeInLine = 0

    def run(self):
        global N, gen_restroom, fila_gen, counterWait, ocupTime
        print("Pessoa{} chegou no banheiro, do gênero {}".format(self.threadID,self.gender))
        fila_gen[self.gender].append(self)
        
        if N > 0:
            if (gen_restroom == self.gender or gen_restroom == -1):
                
                #entrar no banheiro
                print("Pessoa{}, do gênero {}, entrando no box.".format(self.threadID, self.gender))
                fila_gen[self.gender].pop(0)
                gen_restroom = self.gender

                N -= 1
                print("####{} boxes livres####".format(N))
                self.timeInLine = time.time() - self.timeInLine
                counterWait[self.gender] += self.timeInLine
                if N == 0:
                    lock.acquire()
                time.sleep(5)
                ocupTime += 5
                
                #sair do banheiro
                print("Pessoa{}, do gênero {}, saindo do box.".format(self.threadID, self.gender))
                N += 1
                print("####{} boxes livres####".format(N))
                if N == 1:
                    lock.release()
                    if len(fila_gen[self.gender]) > 0: 
                        self.notify(fila_gen[self.gender][0].get_ident())
                
                if not fila_gen[self.gender] or len(fila_gen[self.gender]) == 0:
                   
                    if self.gender == 0:
                        if not fila_gen[1] or len(fila_gen[1]) == 0:
                            gen_restroom = 2
                            self.notify_all()
                        elif not fila_gen[2] or len(fila_gen[2]) == 0:
                            gen_restroom = 1
                            self.notify_all()
                        else:
                            if time.time() - fila_gen[1][0].timeInLine > time.time() - fila_gen[2][0].timeInLine:
                                gen_restroom = 1
                                self.notify_all()
                            else:
                                gen_restroom = 2
                                self.notify_all()
            
                    elif self.gender == 1:
                        if not fila_gen[0] or len(fila_gen[0]) == 0:
                            gen_restroom = 2
                            self.notify_all()
                        elif not fila_gen[2] or len(fila_gen[2]) == 0:
                            gen_restroom = 0
                            self.notify_all()
                        else:
                            if time.time() - fila_gen[0][0].timeInLine > time.time() - fila_gen[2][0].timeInLine:
                                gen_restroom = 0
                                self.notify_all()
                            else:
                                gen_restroom = 2
                                self.notify_all()
                    
                    elif self.gender == 2:
                        if not fila_gen[0] or len(fila_gen[0]) == 0:
                            gen_restroom = 1
                            self.notify_all()
                        elif not fila_gen[1] or len(fila_gen[1]) == 0:
                            gen_restroom = 0
                            self.notify_all()
                        else:
                            if time.time() - fila_gen[0][0].timeInLine > time.time() - fila_gen[1][0].timeInLine:
                                gen_restroom = 1
                                self.notify_all()

        elif N == 0 and gen_restroom == self.gender:
            fila_gen[self.gender].append(self)
            self.wait()

        else:
            fila_gen[self.gender].append(self)
            self.wait()
            

def genGender():
    random.seed()
    gender = random.randint(0,2)
    while(counterGen[gender] >= P/3):
        gender = random.randint(0,2)
    
    counterGen[gender]+=1
    
    return gender

def menu():
    global N, P
   
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
        P = 10
    elif op == 2:
        N = 3
        P = 150 
    elif op == 3: 
        N = 5 
        P = 200
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
        myThread = PersonThread(threadID, genGender())
        threadList.append(myThread)
        myThread.start()
        time.sleep(t)
        threadID += 1

    for i in range(len(threadList)):
        threadList[i].join()
                
    tempoExec = time.time() - tempoExec
    print("\n\n############")
    print("Tempo de execução: {} segundos".format(tempoExec))
    print("Pessoas do Gênero 0: {}. Tempo médio de espera: {}".format(counterGen[0],counterWait[0]/counterGen[0]))
    print("Pessoas do Gênero 1: {}. Tempo médio de espera: {}".format(counterGen[1],counterWait[1]/counterGen[1]))
    print("Pessoas do Gênero 2: {}. Tempo médio de espera: {}".format(counterGen[2],counterWait[2]/counterGen[2]))
    print("Taxa de Ocupação: {}%".format(ocupTime/tempoExec))
if __name__ == "__main__":
    main()