boardSize = 12

def getValue_dfs(mapStat, visited, y, x, playerID):
    if y < 0 or y >= boardSize or x < 0 or x >= boardSize or visited[y][x] or mapStat[y][x] != playerID:
        return 0
    
    visited[y][x] = True
    area = 1
    
    area += getValue_dfs(mapStat, visited, y - 1, x, playerID)  # up
    area += getValue_dfs(mapStat, visited, y + 1, x, playerID)  # down
    area += getValue_dfs(mapStat, visited, y, x - 1, playerID)  # left
    area += getValue_dfs(mapStat, visited, y, x + 1, playerID)  # right
    
    return area

def getValue(mapStat, playerID):
    visited = [[False for _ in range(boardSize)] for _ in range(boardSize)]
    areas = []
    for y in range(boardSize):
        for x in range(boardSize):
            if not visited[y][x] and mapStat[y][x] == playerID:
                areas.append(getValue_dfs(mapStat, visited, y, x, playerID))

    value = 0
    for area in areas:
        value += pow(area, 1.25)
    value = round(value)
    
    return value

# 示例地图
# mapStat = [
#     [-1, -1, -1, -1, -1, 4, 4, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, 4, 4, 4, 3, -1, 3, -1, -1],
#     [-1, -1, -1, 4, 4, 4, 4, 4, 3, 2, 2, 3],
#     [-1, -1, 4, 4, 4, 4, -1, -1, 3, 2, 2, 2],
#     [-1, -1, 1, 1, 1, 1, 2, 3, 2, 4, 2, -1],
#     [-1, -1, -1, 2, 1, 2, 3, 2, 3, 3, 3, -1],
#     [-1, -1, -1, 1, 1, -1, -1, 3, 3, -1, -1, -1],
#     [-1, -1, -1, -1, 1, 1, 0, 3, 3, 0, -1, -1],
#     [-1, 0, 1, 0, 1, 1, -1, 0, 0, 3, -1, -1],
#     [-1, -1, -1, 0, 1, 1, -1, 0, -1, -1, -1, -1],
#     [-1, -1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
# ]

# print(getValue(mapStat, 1))
# print(getValue(mapStat, 2))
# print(getValue(mapStat, 3))
# print(getValue(mapStat, 4))


def applyStep(playerID, mapStat, sheepStat, step):
    if len(step) == 2:  #initPos
        [x, y] = step
        if mapStat[y][x] != 0 or sheepStat[y][x] != 0: return False
        mapStat[y][x] = playerID
        sheepStat[y][x] = 16
        return True

    [(x, y), m, dir] = step
    dirMove = {1:[-1, -1], 2:[0, -1], 3:[1, -1], 4:[-1, 0], 6:[1, 0], 7:[-1, 1], 8:[0, 1], 9:[1, 1]}
    move = dirMove[dir]

    if m >= sheepStat[y][x] or m <= 0: return False
    if mapStat[y + move[1]][x + move[0]] != 0: return False

    sheepStat[y][x] -= m
    while 0 <= y + move[1] < boardSize and 0 <= x + move[0] < boardSize and mapStat[y + move[1]][x + move[0]] == 0:
        x += move[0]
        y += move[1]

    mapStat[y][x] = playerID
    sheepStat[y][x] = m

    return True

mapStat = [
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [-1, -1, -1, -1, -1, 0, 0, 0, -1, -1, -1, -1], 
    [-1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1], 
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1], 
]

sheepStat = [[0 for _ in range(boardSize)] for _ in range(boardSize)]
# sheepStat[4][0] = 16

# print(applyStep(1, mapStat, sheepStat, [(0, 4), 5, 9]))
# print(mapStat)
# print(sheepStat)

def legalSteps(playerID, mapStat, sheepStat):
    legalSteps = []
    dirMove = {1:[-1, -1], 2:[0, -1], 3:[1, -1], 4:[-1, 0], 6:[1, 0], 7:[-1, 1], 8:[0, 1], 9:[1, 1]}
    
    # init
    cnt = sum(row.count(playerID) for row in mapStat)
    if cnt == 0:
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
                        legalSteps.append([j, i])
        return legalSteps

    for i in range(boardSize):
        for j in range(boardSize):
            if mapStat[i][j] == playerID and sheepStat[i][j] > 1:
                for dir, move in dirMove.items():
                    x = j + move[0]
                    y = i + move[1]
                    if x >= 0 and x < boardSize and y >= 0 and y < boardSize and mapStat[y][x] == 0:
                        for m in range(1, sheepStat[i][j]):
                            legalSteps.append([(j, i), m, dir])
    return legalSteps

# steps = legalSteps(1, mapStat, sheepStat)
# print(steps)
# print(applyStep(1, mapStat, sheepStat, steps[0]))
# steps = legalSteps(1, mapStat, sheepStat)
# print(steps)
# print(applyStep(1, mapStat, sheepStat, steps[0]))

# for row in mapStat:
#     print(row)

# for row in sheepStat:
#     print(row)


step = [(0, 1), 0, 1]
step[0] = tuple([step[0][1], step[0][0]])
print(step)

step2 = [0, 1]
step2.reverse()
print(step2)
