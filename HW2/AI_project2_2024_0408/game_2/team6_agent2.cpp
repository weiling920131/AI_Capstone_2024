// g++ -o agent2_cpp.exe Sample.cpp -lws2_32
// team 6
// 110550170 戚維凌
// 110550034 孫承瑞
// 110550175 鄭栩安
#include "STcpClient.h"
#include <stdlib.h>
#include <iostream>
#include <vector>
#include <thread>
#include <cmath>
#include <limits>
#include <random>
#include <unordered_map>
#include <algorithm>
#include <chrono>

int num_threads = 5;
int num_simulations = 50000;
int time_threshold = 2500;
int boardSize = 15;
int sheepNum = 32;
double C_PUCT = 1.5;

std::random_device rd;
std::mt19937 gen(rd());

struct VectorHash {
    size_t operator()(const std::vector<int>& vec) const {
        size_t hash = 0;
        for (int num : vec) {
            hash ^= std::hash<int>()(num);
        }
        return hash;
    }
};

std::vector<std::vector<int>> legalSteps(int playerID, std::vector<std::vector<int>> &mapStat, std::vector<std::vector<int>> &sheepStat) {
	std::vector<std::vector<int>> legal_steps;
	std::vector<std::vector<int>> dir_move = {{}, {-1, -1}, {-1, 0}, {-1, 1}, {0, -1}, {}, {0, 1}, {1, -1}, {1, 0}, {1, 1}}; // 8 directions
	int cnt = 0;
	for (int i = 0; i < boardSize; i++){
		for (int j = 0; j < boardSize; j++){
			if (mapStat[i][j] == playerID) {
				cnt++;
			}
		}
	}

	if (cnt == 0) {  // init
		for (int i = 0; i < boardSize; i++){
			for (int j = 0; j < boardSize; j++){
				if (mapStat[i][j] == 0) {
					bool isLegal = false;
					for (int dir = 2; dir <= 8; dir += 2) {  // 2 4 6 8
						int x = j + dir_move[dir][0];
						int y = i + dir_move[dir][1];
						if ((x < 0) || (x == boardSize) || (y < 0) || (y == boardSize)) {  // border
							isLegal = true;
							break;
						}
						if ((x >= 0) && (x < boardSize) && (y >= 0) && (y < boardSize) && (mapStat[y][x] == -1)) {  // adj to -1
							isLegal = true;
							break;
						}
					}
					if (isLegal) {
						legal_steps.push_back({i, j});
					}
				}
			}
		}
		return legal_steps;
	}
	for (int i = 0; i < boardSize; i++){
		for (int j = 0; j < boardSize; j++){
			if (mapStat[i][j] == playerID && sheepStat[i][j] > 1){ // if this player has more than 1 sheep
				for (int dir = 1; dir <= 9; dir++){ 
					if (dir == 5) continue;
					int y = i + dir_move[dir][1];
					int x = j + dir_move[dir][0];
					if ((x >= 0) && (x < boardSize) && (y >= 0) && (y < boardSize) && (mapStat[y][x] == 0)){ // walk through the direction until meet the wall or other player's sheep
						for (int m = 1; m < sheepStat[i][j]; m++){ // split the sheep
							legal_steps.push_back({i, j, m, dir});
						}
					}
				}
			}
		}
	}
	return legal_steps;
}

bool isTerminal(std::vector<std::vector<int>> &mapStat, std::vector<std::vector<int>> &sheepStat) {
	for (int playerID = 1; playerID <= 4; playerID++) {
		if (legalSteps(playerID, mapStat, sheepStat).size() != 0) {
			return false;
		}
	}
	return true;
}

int getValue_dfs(int playerID, std::vector<std::vector<int>> &mapStat, std::vector<std::vector<bool>> &visited, int y, int x) {
	if ((y < 0) || (y >= boardSize) || (x < 0) || (x >= boardSize) || visited[y][x] || (mapStat[y][x] != playerID)) {
        return 0;
	}
    
    visited[y][x] = true;
    int area = 1;
    
    area += getValue_dfs(playerID, mapStat, visited, y - 1, x);  // up
    area += getValue_dfs(playerID, mapStat, visited, y + 1, x);  // down
    area += getValue_dfs(playerID, mapStat, visited, y, x - 1);  // left
    area += getValue_dfs(playerID, mapStat, visited, y, x + 1);  // right
    
    return area;
}
    

double getValue(int playerID, std::vector<std::vector<int>> &mapStat) {
    std::vector<std::vector<bool>> visited;
	visited.resize(boardSize);
	for (int i = 0; i < boardSize; i++) {
		for (int j = 0; j < boardSize; j++) {
			visited[i].push_back(false);
		}
	}
    std::vector<int> areas;
    for (int y = 0; y < boardSize; y++) {
        for (int x = 0; x < boardSize; x++) {
            if (!visited[y][x] && (mapStat[y][x] == playerID)) {
                areas.push_back(getValue_dfs(playerID, mapStat, visited, y, x));
			}
		}
	}

    double value = 0.0;
    for (auto area: areas) {
        value += pow(area, 1.25);
	}
    value = round(value);
    
    return value;
}

bool applyStep(int playerID, std::vector<std::vector<int>> &mapStat, std::vector<std::vector<int>> &sheepStat, std::vector<int> step) {
    if (step.size() == 2) {  // initPos
        int y = step[0];
		int x = step[1];
        if ((mapStat[y][x] != 0) || (sheepStat[y][x] != 0)) {
            std::cout << "applyStep: error1\n";
            return false;
		}
        mapStat[y][x] = playerID;
        sheepStat[y][x] = sheepNum;
        return true;
	}

    int y = step[0];
	int x = step[1];
	int m = step[2];
	int dir = step[3];

    std::vector<std::vector<int>> dir_move = {{}, {-1, -1}, {-1, 0}, {-1, 1}, {0, -1}, {}, {0, 1}, {1, -1}, {1, 0}, {1, 1}}; // 8 directions

    if ((m >= sheepStat[y][x]) || (m <= 0)) {
        std::cout << "applyStep: error2\n";
        return false;
	}
    if (mapStat[y + dir_move[dir][1]][x + dir_move[dir][0]] != 0) {
        std::cout << "applyStep: error3\n";
        return false;
	}

    sheepStat[y][x] -= m;
    while ((y + dir_move[dir][1] >= 0) && (y + dir_move[dir][1] < boardSize) && (x + dir_move[dir][0] >= 0) && (x + dir_move[dir][0] < boardSize) && (mapStat[y + dir_move[dir][1]][x + dir_move[dir][0]] == 0)) {
        y += dir_move[dir][1];
        x += dir_move[dir][0];
	}

    mapStat[y][x] = playerID;
    sheepStat[y][x] = m;

    return true;
}

class Node {
public:
	Node(int playerID_): playerID(playerID_) {}
	Node(int playerID_, std::vector<int> chosen_step_, Node* parent_): playerID(playerID_), chosen_step(chosen_step_), parent(parent_) {}
	~Node() = default;

	int num_visits = 0;
	double value_sum = 0.0;
	double policy = 0.0;
	std::vector<int> chosen_step;
	Node* parent = NULL;
	std::vector<Node*> children;
	int playerID;
};

class MCTS {
public:
	MCTS(int playerID_, int mapStat_[15][15], int sheepStat_[15][15]): playerID(playerID_) {
		mapStat.resize(boardSize);
		sheepStat.resize(boardSize);
		for (int i = 0; i < boardSize; i++) {
			for (int j = 0; j < boardSize; j++) {
				mapStat[i].push_back(mapStat_[i][j]);
				sheepStat[i].push_back(sheepStat_[i][j]);
			}
		}
		init();
	}
	~MCTS() = default;

	int playerID;
	std::vector<std::vector<int>> mapStat;
	std::vector<std::vector<int>> sheepStat;

	std::vector<std::thread> threads;
	std::vector<Node*> roots;

	void init() {
		for (int threadID = 0; threadID < num_threads; threadID++) {
			roots.push_back(new Node(playerID - 1));
			threads.emplace_back(std::move(std::thread(&MCTS::run, this, threadID)));
		}
		for (auto& thread: threads) {
			thread.join();
		}
	}

	void run(int threadID) {
		auto start = std::chrono::steady_clock::now();
		int i;
		for (i = 0; i < num_simulations; i++) {
			simulation(roots[threadID]);
			auto end = std::chrono::steady_clock::now();
			if (std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() >= time_threshold) {
				break;
			}
		}
		// std::cout << "sim: " << i << '\n';
	}

	void simulation(Node* root) {
		Node* leaf_node = root;
		std::vector<std::vector<int>> leaf_mapStat(mapStat);
		std::vector<std::vector<int>> leaf_sheepStat(sheepStat);

		select(root, leaf_node, leaf_mapStat, leaf_sheepStat);
	}

	void select(Node* root, Node* leaf_node, std::vector<std::vector<int>> &leaf_mapStat, std::vector<std::vector<int>> &leaf_sheepStat) {
		while (leaf_node->children.size() != 0) {
			leaf_node->num_visits++;

			double best_score = -std::numeric_limits<double>::infinity();
			Node* select_node = NULL;
			for (auto child: leaf_node->children) {
				double score = 0;
				if (child->num_visits == 0) {
					score = std::numeric_limits<double>::infinity();
				}
				else {
					double q = child->value_sum / child->num_visits;
					double u = C_PUCT * sqrt(log(root->num_visits) / child->num_visits);
					score = q + u;
				}

				if (score > best_score) {
					best_score = score;
					select_node = child;
				}
			}
			if (select_node == NULL) {
				std::cout << "select error\n";
				return;
			}
			leaf_node = select_node;
			if (!applyStep(leaf_node->playerID, leaf_mapStat, leaf_sheepStat, leaf_node->chosen_step)) {
				return;
			}
		}
		leaf_node->num_visits++;

		if (isTerminal(leaf_mapStat, leaf_sheepStat)) {
			update(root, leaf_node, leaf_mapStat);
			return;
		}
		// expand
		std::vector<std::vector<int>> legal_steps = legalSteps(leaf_node->playerID % 4 + 1, leaf_mapStat, leaf_sheepStat);
		for (auto& step: legal_steps) {
			leaf_node->children.push_back(new Node(leaf_node->playerID % 4 + 1, step, leaf_node));
		}

		evaluate(root, leaf_node, leaf_mapStat, leaf_sheepStat);
        return;
	}

	void evaluate(Node* root, Node* leaf_node, std::vector<std::vector<int>> &leaf_mapStat, std::vector<std::vector<int>> &leaf_sheepStat) {
		// rollout
		if (leaf_node->children.size() > 0) {
			std::uniform_int_distribution<> dis(0, leaf_node->children.size() - 1);
    		int r_idx = dis(gen);
			leaf_node = leaf_node->children[r_idx];
			leaf_node->num_visits++;

			if (!applyStep(leaf_node->playerID, leaf_mapStat, leaf_sheepStat, leaf_node->chosen_step)) {
				return;
			}
		}

		int cur_player = leaf_node->playerID;
		while (!isTerminal(leaf_mapStat, leaf_sheepStat)) {
			cur_player = cur_player % 4 + 1;
			std::vector<std::vector<int>> legal_steps = legalSteps(cur_player, leaf_mapStat, leaf_sheepStat);
			if (legal_steps.size() > 0) {
				std::uniform_int_distribution<> dis(0, legal_steps.size() - 1);
    			int r_idx = dis(gen);
				if (!applyStep(cur_player, leaf_mapStat, leaf_sheepStat, legal_steps[r_idx])) {
					return;
				}
			}
		}

		update(root, leaf_node, leaf_mapStat);
		return;
	}

	void update(Node* root, Node* leaf_node, std::vector<std::vector<int>> &leaf_mapStat) {
		while (leaf_node->parent != NULL) {
			leaf_node->policy = leaf_node->num_visits / root->num_visits;
			leaf_node->value_sum += getValue(leaf_node->playerID, leaf_mapStat);
			leaf_node = leaf_node->parent;
		}
		return;
	}

	std::vector<int> getStep() {
		std::unordered_map<std::vector<int>, double, VectorHash> all_steps;
		for (auto& root: roots) {
			for (auto& child: root->children) {
				if (child->num_visits > 0) {
					all_steps[child->chosen_step] += child->value_sum / child->num_visits;
				}
			}
		}

		auto bestStep = std::max_element(all_steps.begin(), all_steps.end(), [](const auto& lhs, const auto& rhs) {
                                             return lhs.second < rhs.second;
                                         });
        return bestStep->first;
	}
};

/*
    選擇起始位置
    選擇範圍僅限場地邊緣(至少一個方向為牆)
    
    return: init_pos
    init_pos=<x,y>,代表你要選擇的起始位置
    
*/
std::vector<int> InitPos(int mapStat[15][15], int playerID)
{
	std::vector<int> init_pos;
	init_pos.resize(2);

	int sheepStat[15][15] = {0};
	MCTS mcts(playerID, mapStat, sheepStat);

	init_pos = mcts.getStep();
    
    return init_pos;
}

/*
	產出指令
    
    input: 
	playerID: 你在此局遊戲中的角色(1~4)
    mapStat : 棋盤狀態, 為 15*15矩陣, 
					0=可移動區域, -1=障礙, 1~4為玩家1~4佔領區域
    sheepStat : 羊群分布狀態, 範圍在0~16, 為 15*15矩陣

    return Step
    Step : <x,y,m,dir> 
            x, y 表示要進行動作的座標 
            m = 要切割成第二群的羊群數量
            dir = 移動方向(1~9),對應方向如下圖所示
            1 2 3
			4 X 6
			7 8 9
*/
std::vector<int> GetStep(int playerID,int mapStat[15][15], int sheepStat[15][15])
{

	std::vector<int> step;
	step.resize(4);

	MCTS mcts(playerID, mapStat, sheepStat);
	step = mcts.getStep();
    
    return step;
}

int main()
{
	int id_package;
	int playerID;
    int mapStat[15][15];
    int sheepStat[15][15];

	// player initial
	GetMap(id_package,playerID,mapStat);
	std::vector<int> init_pos = InitPos(mapStat, playerID);
	SendInitPos(id_package,init_pos);

	while (true)
	{
		if (GetBoard(id_package, mapStat, sheepStat))
			break;

		std::vector<int> step = GetStep(playerID,mapStat,sheepStat);
		SendStep(id_package, step);
	}
}
