'''
py to exe:
pyinstaller --onefile --name agent1 Sample.py
'''

import STcpClient
import numpy as np
import random
import threading
import time

num_threads = 4
num_simulations = 50
# time_threshold = 2.5
boardSize = 12
sheepNum = 16
C_PUCT = 1.5
tensor_shape = [1+2+2, boardSize, boardSize] # 1: wall, 2: me and others, 2: my sheep and others'
num_distinct_actions = (sheepNum - 1) * 8

def legalSteps(playerID, mapStat, sheepStat):
    legalSteps = []
    # dirMove = {1:[-1, -1], 2:[0, -1], 3:[1, -1], 4:[-1, 0], 6:[1, 0], 7:[-1, 1], 8:[0, 1], 9:[1, 1]}
    dirMove = {1:[-1, -1], 2:[-1, 0], 3:[-1, 1], 4:[0, -1], 6:[0, 1], 7:[1, -1], 8:[1, 0], 9:[1, 1]}
    
    cnt = np.sum(mapStat == playerID)
    if cnt == 0:    # init
        for i in range(boardSize):
            for j in range(boardSize):
                if mapStat[i][j] == 0:
                    isLegal = False
                    for dir in [2, 4, 6, 8]:
                        move = dirMove[dir]
                        x = j + move[0]
                        y = i + move[1]
                        if x < 0 or x == boardSize or y < 0 or y == boardSize:  # border
                            isLegal = True
                            break
                        if x >= 0 and x < boardSize and y >= 0 and y < boardSize and mapStat[y][x] == -1:   # adjacant to -1
                            isLegal = True
                            break
                    if isLegal:
                        legalSteps.append([i, j])
        return legalSteps

    for i in range(boardSize):
        for j in range(boardSize):
            if mapStat[i][j] == playerID and sheepStat[i][j] > 1:
                for dir, move in dirMove.items():
                    x = j + move[0]
                    y = i + move[1]
                    if x >= 0 and x < boardSize and y >= 0 and y < boardSize and mapStat[y][x] == 0:
                        for m in range(1, sheepStat[i][j]):
                            legalSteps.append([(i, j), m, dir])
    return legalSteps

def isTerminal(mapStat, sheepStat):
    for playerID in range(1, 5):
        if len(legalSteps(playerID, mapStat, sheepStat)) != 0:
            return False
    return True

def getValue_dfs(playerID, mapStat, visited, y, x):
    if y < 0 or y >= boardSize or x < 0 or x >= boardSize or visited[y][x] or mapStat[y][x] != playerID:
        return 0
    
    visited[y][x] = True
    area = 1
    
    area += getValue_dfs(playerID, mapStat, visited, y - 1, x)  # up
    area += getValue_dfs(playerID, mapStat, visited, y + 1, x)  # down
    area += getValue_dfs(playerID, mapStat, visited, y, x - 1)  # left
    area += getValue_dfs(playerID, mapStat, visited, y, x + 1)  # right
    
    return area

def getValue(playerID, mapStat):
    visited = [[False for _ in range(boardSize)] for _ in range(boardSize)]
    areas = []
    for y in range(boardSize):
        for x in range(boardSize):
            if not visited[y][x] and mapStat[y][x] == playerID:
                areas.append(getValue_dfs(playerID, mapStat, visited, y, x))

    value = 0
    for area in areas:
        value += pow(area, 1.25)
    value = round(value)
    
    return value

def applyStep(playerID, mapStat, sheepStat, step):
    if len(step) == 2:  #initPos
        [y, x] = step
        if mapStat[y][x] != 0 or sheepStat[y][x] != 0: 
            print("applyStep: error1")
            return False
        mapStat[y][x] = playerID
        sheepStat[y][x] = sheepNum
        return True

    [(y, x), m, dir] = step
    # dirMove = {1:[-1, -1], 2:[0, -1], 3:[1, -1], 4:[-1, 0], 6:[1, 0], 7:[-1, 1], 8:[0, 1], 9:[1, 1]}
    dirMove = {1:[-1, -1], 2:[-1, 0], 3:[-1, 1], 4:[0, -1], 6:[0, 1], 7:[1, -1], 8:[1, 0], 9:[1, 1]}
    move = dirMove[dir]

    if m >= sheepStat[y][x] or m <= 0: 
        print("applyStep: error2")
        return False
    if mapStat[y + move[1]][x + move[0]] != 0: 
        print("applyStep: error3")
        return False

    sheepStat[y][x] -= m
    while 0 <= y + move[1] < boardSize and 0 <= x + move[0] < boardSize and mapStat[y + move[1]][x + move[0]] == 0:
        x += move[0]
        y += move[1]

    mapStat[y][x] = playerID
    sheepStat[y][x] = m

    return True


class Node:
    def __init__(self, playerID, chosen_step = [], parent = None):
        self.num_visits = 0
        self.value_sum = 0.0
        self.policy = 0.0
        self.chosen_step = chosen_step
        self.parent = parent
        self.children = []
        self.playerID = playerID
        # weiling add 
        self.mapStat = np.zeros((boardSize, boardSize), dtype=int)
        self.sheepStat = np.zeros((boardSize, boardSize), dtype=int)
        # weiling add
    
    # weiling add
    def observation_tensor(self):
        tensor = np.zeros(tensor_shape, dtype=int)
        tensor[0][self.mapStat == -1] = 1
        tensor[1][self.mapStat == self.playerID] = 1
        tensor[2][self.mapStat != self.playerID] = 1
        tensor[3] = [self.sheepStat[i][j]  for i in range(boardSize) for j in range(boardSize) if self.mapStat[i][j] == self.playerID]
        tensor[4] = [self.sheepStat[i][j]  for i in range(boardSize) for j in range(boardSize) if self.mapStat[i][j] != self.playerID]
        return tensor


    # weiling add


class MCTS:
    def __init__(self, playerID, mapStat, sheepStat):
        self.playerID = playerID
        self.mapStat = mapStat
        self.sheepStat = sheepStat

        self.threads = []
        self.roots = []

        for threadID in range(num_threads):
            self.roots.append(Node(playerID - 1))
            thread = threading.Thread(target=self.run, args=(threadID,))
            self.threads.append(thread)
            thread.start()

        for thread in self.threads:
            thread.join()

    def run(self, threadID):
        # start = time.perf_counter()
        for _ in range(num_simulations):
            self.simulation(self.roots[threadID])
            # end = time.perf_counter()
            # if (end - start) >= time_threshold:
            #     break

    def simulation(self, root):
        leaf_node = root
        leaf_mapStat = self.mapStat.copy()
        leaf_sheepStat = self.sheepStat.copy()

        self.select(root, leaf_node, leaf_mapStat, leaf_sheepStat)
        

    def select(self, root, leaf_node, leaf_mapStat, leaf_sheepStat):
        while len(leaf_node.children) != 0:
            leaf_node.num_visits += 1
    
            best_score = -np.inf
            selected_node = None
            for child in leaf_node.children:
                if child.num_visits == 0:
                    score = np.inf
                else:
                    q = child.value_sum / child.num_visits
                    u = C_PUCT * np.sqrt(np.log(root.num_visits) / child.num_visits)
                    score = q + u

                if score > best_score:
                    best_score = score
                    selected_node = child

            if selected_node != None:
                leaf_node = selected_node
                if not applyStep(leaf_node.playerID, leaf_mapStat, leaf_sheepStat, leaf_node.chosen_step):
                    return
                
        leaf_node.num_visits += 1

        if isTerminal(leaf_mapStat, leaf_sheepStat):
            self.update(root, leaf_node, leaf_mapStat)
            return

        # expand
        legalsteps = legalSteps(leaf_node.playerID % 4 + 1, leaf_mapStat, leaf_sheepStat)
        for step in legalsteps:
            leaf_node.children.append(Node(leaf_node.playerID % 4 + 1, step, leaf_node))

        # rollout
        self.evaluate(root, leaf_node, leaf_mapStat, leaf_sheepStat)
        return


    def evaluate(self, root, leaf_node, leaf_mapStat, leaf_sheepStat):
        # rollout
        if len(leaf_node.children) > 0:
            leaf_node = random.choice(leaf_node.children)
            leaf_node.num_visits += 1

            if not applyStep(leaf_node.playerID, leaf_mapStat, leaf_sheepStat, leaf_node.chosen_step):
                return

        cur_player = leaf_node.playerID
        while not isTerminal(leaf_mapStat, leaf_sheepStat):
            cur_player = cur_player % 4 + 1
            legalsteps = legalSteps(cur_player, leaf_mapStat, leaf_sheepStat)
            if len(legalsteps) > 0:
                step = random.choice(legalsteps)
                if not applyStep(cur_player, leaf_mapStat, leaf_sheepStat, step):
                    return
        
        self.update(root, leaf_node, leaf_mapStat)
        return

    def update(self, root, leaf_node, leaf_mapStat):
        while leaf_node.parent != None:
            leaf_node.policy = leaf_node.num_visits / root.num_visits
            leaf_node.value_sum += getValue(leaf_node.playerID, leaf_mapStat)
            leaf_node = leaf_node.parent

        return
    
    def getStep(self):
        all_steps = {}
        for threadID in range(num_threads):
            for child in self.roots[threadID].children:
                if child.num_visits > 0:
                    step = tuple(child.chosen_step)
                    all_steps[step] = all_steps.get(step, 0) + child.value_sum / child.num_visits

        bestStep = max(all_steps, key=all_steps.get)
        return list(bestStep)


'''
    選擇起始位置
    選擇範圍僅限場地邊緣(至少一個方向為牆)
    
    return: init_pos
    init_pos=[x,y],代表起始位置
    
'''

def InitPos(mapStat, playerID):
    init_pos = [0, 0]
    mapStat = mapStat.astype(int)
    sheepStat = np.zeros((boardSize, boardSize), dtype=int)
    mcts = MCTS(playerID, mapStat, sheepStat)
    init_pos = mcts.getStep()

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
    mapStat = mapStat.astype(int)
    sheepStat = sheepStat.astype(int)
    mcts = MCTS(playerID, mapStat, sheepStat)
    step = mcts.getStep()

    return step


# player initial
(id_package, playerID, mapStat) = STcpClient.GetMap()
init_pos = InitPos(mapStat, playerID)
STcpClient.SendInitPos(id_package, init_pos)

# start game
while (True):
    (end_program, id_package, mapStat, sheepStat) = STcpClient.GetBoard()
    if end_program:
        STcpClient._StopConnect()
        break
    Step = GetStep(playerID, mapStat, sheepStat)

    STcpClient.SendStep(id_package, Step)
