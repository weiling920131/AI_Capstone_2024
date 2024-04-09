import STcpClient
import numpy as np
import random
import threading

num_threads = 4
num_simulations = 10000
boardSize = 12

def legalSteps(playerID, mapStat, sheepStat):
    legalSteps = []
    dirMove = {1:[-1, -1], 2:[0, -1], 3:[1, -1], 4:[-1, 0], 6:[1, 0], 7:[-1, 1], 8:[0, 1], 9:[1, 1]}
    for i in range(boardSize):
        for j in range(boardSize):
            if mapStat[i][j] == playerID and sheepStat[i][j] > 1:
                for dir, move in dirMove.items():
                    x = i + move[0]
                    y = j + move[1]
                    if x >= 0 and x < boardSize and y >= 0 and y < boardSize and mapStat[x][y] == 0:
                        for m in range(1, sheepStat[i][j]):
                            legalSteps.append([(x, y), m, dir])
    return legalSteps

class Node:
    def __init__(self):
        self.num_visits = 0
        self.parent_player_value_sum = 0.0
        self.current_player_value_sum = 0.0
        self.children = []

class MCTS:
    def __init__(self):
        self.threads = []
        self.roots = list([Node()] * num_threads)

        for i in range(num_threads):
            thread = threading.Thread(target=self.run, args=(i))
            self.threads.append(thread)

        for thread in self.threads:
            thread.start()

        for thread in self.threads:
            thread.join()

    def run(self, threadID):
        for _ in range(num_simulations):
            self.simulation(self.roots[threadID])

    def simulation(self, root):
        self.select()
        self.evaluate()
        self.update()

    def select(self):
        pass

    def evaluate(self):
        pass

    def update(self):
        pass



'''
    選擇起始位置
    選擇範圍僅限場地邊緣(至少一個方向為牆)
    
    return: init_pos
    init_pos=[x,y],代表起始位置
    
'''

def InitPos(mapStat):
    init_pos = [0, 0]
    '''
        Write your code here

    '''
    return init_pos


'''
    產出指令
    
    input: 
    playerID: 你在此局遊戲中的角色(1~4)
    mapStat : 棋盤狀態(list of list), 為 12*12矩陣, 
              0=可移動區域, -1=障礙, 1~4為玩家1~4佔領區域
    sheepStat : 羊群分布狀態, 範圍在0~16, 為 12*12矩陣

    return Step
    Step : 3 elements, [(x,y), m, dir]
            x, y 表示要進行動作的座標 
            m = 要切割成第二群的羊群數量
            dir = 移動方向(1~9),對應方向如下圖所示
            1 2 3
            4 X 6
            7 8 9
'''
def GetStep(playerID, mapStat, sheepStat):
    step = [(0, 0), 0, 1]
    '''
    Write your code here
    
    '''
    return step


# player initial
(id_package, playerID, mapStat) = STcpClient.GetMap()
init_pos = InitPos(mapStat)
STcpClient.SendInitPos(id_package, init_pos)

# start game
while (True):
    (end_program, id_package, mapStat, sheepStat) = STcpClient.GetBoard()
    if end_program:
        STcpClient._StopConnect()
        break
    Step = GetStep(playerID, mapStat, sheepStat)

    STcpClient.SendStep(id_package, Step)
