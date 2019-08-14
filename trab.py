#!/usr/bin/python3

import threading
import time
import random

random.seed(time.time())

N = 10  #número de boxes livres
gen_restroom = 0   #gênero que está no banheiro
fila_gen = [[],[],[]]
counterGen = [0,0,0]   #conta as quantidades de pessoas de cada gênero
counterWait = [0,0,0]
ocupTime = 0

class PersonThread(threading.Thread):
    def __init__(self, threadID, gender):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.gender = gender
        self.timeInLine = 0
    
    def run(self):
        global N, gen_restroom, fila_gen, counterWait, ocupTime
        print("Pessoa{} chegou no banheiro, do gênero {}".format(self.threadID,self.gender))
        
        if N > 0:
            if (gen_restroom == self.gender or gen_restroom == 0):
                
                print("Pessoa{}, do gênero {}, entrando no box.".format(self.threadID, self.gender))
                gen_restroom = self.gender
                N -= 1
                time.sleep(5)
                self.timeInLine = time.time() - self.timeInLine
                counterWait[self.gender] += self.timeInLine
                ocupTime += 5
                print("Pessoa{}, do gênero {}, saindo do box.".format(self.threadID, self.gender))
                N += 1
                
                if not fila_gen[self.gender] or len(fila_gen[self.gender]) == 0:
                    if self.gender == 0:
                        if not fila_gen[1] or len(fila_gen[1]) == 0:
                            return 2
                        elif not fila_gen[2] or len(fila_gen[2]) == 0:
                            return 1
                        else:
                            if time.time() - fila_gen[1][0].timeInLine > time.time() - fila_gen[2][0].timeInLine:
                                return 1
                            else:
                                return 2
            
                    elif self.gender == 1:
                        if not fila_gen[0] or len(fila_gen[0]) == 0:
                            return 2
                        elif not fila_gen[2] or len(fila_gen[2]) == 0:
                            return 0
                        else:
                            if time.time() - fila_gen[0][0].timeInLine > time.time() - fila_gen[2][0].timeInLine:
                                return 0
                            else:
                                return 2
                    
                    elif self.gender == 2:
                        if not fila_gen[0] or len(fila_gen[0]) == 0:
                            return 1
                        elif not fila_gen[1] or len(fila_gen[1]) == 0:
                            return 0
                        else:
                            if time.time() - fila_gen[0][0].timeInLine > time.time() - fila_gen[1][0].timeInLine:
                                return 0
                            else:
                                return 1
                    
        else:
            time.sleep(random.random())
            

def main():
    threadID = 1
    tempoExec = time.time()
    gender = random.randint(0,2)
    for i in range(15):
        random.seed()
        t = random.randint(1,7)
        while(counterGen[gender] >= 5):
            gender = random.randint(0,2)
        counterGen[gender]+=1
        myThread = PersonThread(threadID, gender)
        gender = random.randint(0,2)
        myThread.start()
        time.sleep(t)
        threadID += 1

        #myThread.join()
                
    tempoExec = time.time() - tempoExec
    print("############")
    print("Tempo de execução: {} segundos".format(tempoExec))
    print("Pessoas do Gênero 0: {}. Tempo médio de espera: {}".format(counterGen[0],counterWait[0]/counterGen[0]))
    print("Pessoas do Gênero 1: {}. Tempo médio de espera: {}".format(counterGen[1],counterWait[1]/counterGen[1]))
    print("Pessoas do Gênero 2: {}. Tempo médio de espera: {}".format(counterGen[2],counterWait[2]/counterGen[2]))
    print("Taxa de Ocupação: {}%".format(ocupTime/tempoExec))
if __name__ == "__main__":
    main()