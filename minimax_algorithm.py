import tkinter
from matplotlib.pyplot import grid
import numpy as np
import copy
from tkinter import *
from tkinter import ttk
from PIL import Image
import sys
from tkinter import messagebox
from dataclasses import dataclass, replace


# As the map becomes bigger, we need to set a dynamic depth, so at the start of the game we might only check the first 2 levels
# but as the game progresses (and the tree of possible choices decreases) we will go deeper
dynamic_depth = 0


@dataclass
class StepBlock:
    step_x: int
    step_y: int
    block_x: int
    block_y: int


def occupiable_spaces(game_array, contestant_pos):
    list_occupiable = []
    x = contestant_pos[0]
    y = contestant_pos[1]
    array_length = len(game_array)

    # we check the spaces next to the contestant, and put the places he can step into
    for i in range(-1, 2):
        for j in range(-1, 2):
            x_temp = x + i
            y_temp = y + j
            if (
                x_temp >= 0
                and x_temp < array_length
                and y_temp < array_length
                and y_temp >= 0
            ):
                if game_array[x_temp][y_temp] == 0:
                    list_occupiable.append((x_temp, y_temp))
    return list_occupiable


def occupiable_spaces_degree(game_array, contestant_pos):
    degree_free_pos = []
    x = contestant_pos[0]
    y = contestant_pos[1]
    array_length = len(game_array)

    # We iterate through every possible position the contestant can step into, and we give each one a degree based on how many possible positions
    # we could further step into from there

    for i in range(-1, 2):
        for j in range(-1, 2):
            x_temp = x + i
            y_temp = y + j
            if (
                x_temp >= 0
                and x_temp < array_length
                and y_temp < array_length
                and y_temp >= 0
            ):
                if game_array[x_temp][y_temp] == 0:
                    temp_list = occupiable_spaces(game_array, (x_temp, y_temp))
                    degree_free_pos.append(len(temp_list) - 1)
    return degree_free_pos


def positions(game_array):
    # We iterate through the whole table searching for the bot and player's position
    array_length = len(game_array)
    for j in range(0, array_length):
        for i in range(0, array_length):
            if game_array[i][j] == 2:
                player_pos = (i, j)
            else:
                if game_array[i][j] == 3:
                    bot_pos = (i, j)
    return player_pos, bot_pos


def blockable_pos(game_array):
    # we iterate through the whole table searching for the tiles that the contestant can block
    array_length = len(game_array)
    list_blockable = []
    for i in range(0, array_length):
        for j in range(0, array_length):
            if game_array[i][j] == 0:
                list_blockable.append((i, j))
    return list_blockable


def minimax(game_array, level, nr):
    player_pos, bot_pos = positions(game_array)
    step_and_block = StepBlock(0, 0, 0, 0)

    if level == "maxi":
        contestant_steppable = occupiable_spaces(game_array, bot_pos)
        val = -10
        for i in contestant_steppable:

            game_array[bot_pos[0]][
                bot_pos[1]
            ] = 0  # the contestant's original position becomes zero and we select the next one
            game_array[i[0]][i[1]] = 3
            contestant_blockable = blockable_pos(game_array)

            for j in contestant_blockable:
                game_array[j[0]][j[1]] = 1
                result = minimax(game_array, "mini", nr + 1)
                game_array[j[0]][j[1]] = 0
                if val < result:
                    val = result
                    # if we are at the last level, we save the winning position the bot should step into
                    if nr == 0 and val >= 1:
                        game_array[j[0]][j[1]] = 0
                        game_array[i[0]][i[1]] = 0
                        game_array[bot_pos[0]][bot_pos[1]] = 3
                        return (i[0], i[1]), (j[0], j[1])

            game_array[i[0]][i[1]] = 0  # we reset the positions to their initial values
            game_array[bot_pos[0]][bot_pos[1]] = 3

        if nr == 0:
            return (i[0], i[1]), (j[0], j[1])
        return val
    else:
        if level == "mini":
            val = 10
            contestant_steppable = occupiable_spaces(game_array, player_pos)
            for i in contestant_steppable:
                game_array[player_pos[0]][player_pos[1]] = 0
                game_array[i[0]][i[1]] = 2
                contestant_blockable = blockable_pos(game_array)
                for j in contestant_blockable:
                    game_array[j[0]][j[1]] = 1
                    result = minimax(game_array, "maxi", nr + 1)
                    game_array[j[0]][j[1]] = 0
                    val = min(val, result)
                    if val < -1:
                        game_array[j[0]][j[1]] = 0
                        game_array[i[0]][i[1]] = 0
                        game_array[player_pos[0]][player_pos[1]] = 2
                        break

                game_array[i[0]][i[1]] = 0
                game_array[player_pos[0]][player_pos[1]] = 2
        return val


def minimax_heuristic(game_array, level, nr, alfa, beta):
    global dynamic_depth
    try:
        player_pos, bot_pos = positions(game_array)
    except:
        if level == "maxi":
            return -100
        else:
            return 100

    step_and_block = StepBlock(0, 0, 0, 0)
    bot_steppable = occupiable_spaces(game_array, bot_pos)
    player_steppable = occupiable_spaces(game_array, player_pos)

    # Heuristic: Winning routes get priority
    if len(bot_steppable) == 0:
        return -100
    if len(player_steppable) == 0:
        return 100

    bot_blocks = occupiable_spaces_degree(game_array, bot_pos)
    player_blocks = occupiable_spaces_degree(game_array, player_pos)
    # Heuristic: we look at the degree of every position the contestants can step into (as in, the number of possible positions, the positions we step into offer)
    if nr >= 2 + dynamic_depth // 2:
        return sum(bot_blocks) - sum(player_blocks)

    if level == "maxi":
        val = -100
        for i in bot_steppable:
            game_array[bot_pos[0]][bot_pos[1]] = 0
            game_array[i[0]][i[1]] = 3
            # Heuristic: we give the blockable tiles next to the player priority (as in the bot will usually block these tiles first)
            contestant_blockable = copy.deepcopy(player_steppable)
            contestant_blockable = blockable_pos(game_array)
            contestant_blockable = list(set(contestant_blockable))
            for j in contestant_blockable:
                game_array[j[0]][j[1]] = 1
                result = minimax_heuristic(game_array, "mini", nr + 1, alfa, beta)
                game_array[j[0]][j[1]] = 0
                if val < result:
                    val = result
                    if nr == 0 and alfa >= 1000:
                        game_array[j[0]][j[1]] = 0
                        game_array[i[0]][i[1]] = 0
                        game_array[bot_pos[0]][bot_pos[1]] = 3
                        return (i[0], i[1]), (j[0], j[1])
                    step_and_block = replace(
                        step_and_block,
                        step_x=i[0],
                        step_y=i[1],
                        block_x=j[0],
                        block_y=j[1],
                    )
                # Heuristic: Alfa-beta cutting
                alfa = max(alfa, val)
                if val >= beta:
                    break

            game_array[i[0]][i[1]] = 0
            game_array[bot_pos[0]][bot_pos[1]] = 3
        if nr == 0 and val >= 1:
            return (step_and_block.step_x, step_and_block.step_y), (
                step_and_block.block_x,
                step_and_block.block_y,
            )
        else:
            if nr == 0:
                return (i[0], i[1]), (j[0], j[1])
        return val
    else:
        val = 100
        if level == "mini":
            for i in player_steppable:
                game_array[player_pos[0]][player_pos[1]] = 0
                game_array[i[0]][i[1]] = 2
                contestant_blockable = blockable_pos(game_array)
                for j in contestant_blockable:
                    game_array[j[0]][j[1]] = 1
                    result = minimax_heuristic(game_array, "maxi", nr + 1, alfa, beta)
                    game_array[j[0]][j[1]] = 0
                    val = min(val, result)
                    # Heuristic: Alfa-beta cutting
                    beta = min(beta, val)
                    if alfa >= val:
                        break
                game_array[i[0]][i[1]] = 0
                game_array[player_pos[0]][player_pos[1]] = 2
        return val
