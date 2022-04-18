from matplotlib.pyplot import grid
import numpy as np
import copy
from tkinter import *
from tkinter import messagebox
import minimax_algorithm
from dataclasses import dataclass, replace

@dataclass
class Contestant:
    x: int
    y: int

def game_over(game_array, contestant_pos):
    x = contestant_pos.x
    y = contestant_pos.y
    array_length = len(game_array)
    ok = False

    #we check whether there is a free position in the vicinity of our player
    for i in range (-1, 2):
        for j in range (-1,2):
            x_temp = x + i
            y_temp = y + j
            if (x_temp>=0 and x_temp < array_length and y_temp < array_length and y_temp >= 0):
                if (game_array[x_temp][y_temp]==0):
                    ok = True

    #if the human player is the one who loses, we return 1, if it's the bot, we return -1, and if it's not game over, we return 0  
    if (ok == False):
        if (game_array[contestant_pos.x][contestant_pos.y] == 2):
            return 1
        else:
            return -1
    else:
        return 0

def gameplay_initialiser(tile_nr_aux):
    print(turn.get())
    tile_set(tile_nr_aux)
    map_initialiser()

def tile_set(tile_nr_aux):
    global tile_nr, master
    tile_nr = tile_nr_aux
    for widget in master.winfo_children():
        widget.destroy()
    master.columnconfigure(tile_nr, weight=1)
    master.rowconfigure(tile_nr, weight=1)

def map_initialiser():
    global tile_list, tile_nr, master, game_array, player, bot, turn
    tile_list = [[0 for i in range(tile_nr)] for j in range(tile_nr)]
    
    for i in range (0,tile_nr):
        for j in range (0,tile_nr):
            tile_list[i][j] = (Button(master, text = "",bg='white', activebackground='white', width = 120//tile_nr, height = 45//tile_nr, command=lambda i=i, j=j:game_running(i,j)))

    tile_list[0][tile_nr//2].config(bg='red', activebackground='red')
    tile_list[tile_nr-1][tile_nr//2].config(bg='green', activebackground='green')

    print(len(tile_list))

    for i in range (0,tile_nr):
        for j in range (0,tile_nr):
            tile_list[i][j].grid(row=i, column=j)

    game_array = np.zeros((tile_nr,tile_nr))
    game_array[tile_nr-1][tile_nr//2] = 2
    game_array[0][tile_nr//2] = 3
    player = replace(player, x = tile_nr-1, y = tile_nr//2)
    bot = replace(bot, x=0, y=tile_nr//2)
    if (turn.get()==2): #We call game_running so the bot can make its first step
        game_running(0,0)

def player_position(game_array):
    array_length = len(game_array)

    for i in range(0, array_length):
        for j in range (0, array_length):
                if game_array[i][j] == 2:
                    player_pos = (i,j)

    return player_pos

def check_winner(contestant_pos):
    ok = game_over(game_array, contestant_pos)

    if (ok == 1):
        print("THE BOT HAS WON")
        messagebox.showinfo("Game Over", "The Bot has won")
        quit()
    else:
        if (ok == -1):
            print("THE PLAYER HAS WON")
            messagebox.showinfo("Game Over", "You have won")
            quit()
    return 0

def game_running(i,j):
    global turn, player, bot
    contestant_pos = player_position(game_array)

    if (turn.get() == 0):
        if (game_array[i][j]==0 and abs(i - contestant_pos[0]) <= 1 and abs(j - contestant_pos[1]) <= 1 ):
            graphic_player_move(i,j)
            turn.set(1)
    else:
        if (turn.get() == 1):
            if (game_array[i][j]==0):
                graphic_player_block(i,j)
                turn.set(2)
            
        if (check_winner(bot) != 0):
            return

        if (turn.get() == 2):
            graphic_bot_move(tile_nr)            
            if (check_winner(player) != 0):
                return
            turn.set(0)

def graphic_bot_move(tile_nr):
    global player, bot
    game_array_copy = copy.deepcopy(game_array)
    print("bot",game_array)
    if (tile_nr>3):
        print("Heuristical minimax")
        optimal_pos = minimax_algorithm.minimax_heuristic(game_array_copy, "maxi", 0, -100, 100)  
    else:
        print("Plain minimax")
        optimal_pos = minimax_algorithm.minimax(game_array_copy, "maxi", 0)

    game_array[bot.x][bot.y] = 0
    tile_list[bot.x][bot.y].config(bg='white', activebackground='white')
    print("optimal_pos: ", optimal_pos)
    new_bot_pos = optimal_pos[0]
    blocking_pos = optimal_pos[1]
    minimax_algorithm.dynamic_depth = minimax_algorithm.dynamic_depth + 1
    
    game_array[new_bot_pos[0]][new_bot_pos[1]] = 3
    game_array[blocking_pos[0]][blocking_pos[1]] = 1
    bot = replace(bot, x = new_bot_pos[0], y = new_bot_pos[1])

    tile_list[bot.x][bot.y].config(bg="red", activebackground='red')
    tile_list[blocking_pos[0]][blocking_pos[1]].config(bg='grey', activebackground='grey')

    return 1
    
def graphic_player_move(i,j):

    tile_list[player.x][player.y].config(bg='white', activebackground='white')
    game_array[player.x][player.y] = 0
    player.x = i
    player.y = j
    game_array[i][j] = 2
    tile_list[i][j].config(bg='green', activebackground='green')
    print("JMozdulat1",game_array)

def graphic_player_block(i,j):
    game_array[i][j] = 1
    tile_list[i][j].config(bg='grey', activebackground='grey')


def interface_menu():
    global turn
    master.geometry("1100x1000")
    master.title("Tic Tac Toe Advanced")
    button_mode3 = Button(master, text = "3x3",width = 20, height = 10, command=lambda:gameplay_initialiser(3))
    button_mode5 = Button(master, text = "5x5",width = 20, height = 10, command=lambda:gameplay_initialiser(5))
    who_starts = Checkbutton(master, text = "The bot should start", variable=turn, onvalue=2, offvalue=0, indicatoron=True)
    tutorial_text = Label(master, text = "\nThe game is played as follows:\n\n 1. The player needs to pick a surrounding tile that he wants to step into \n(the player can move diagonally, horizontally or vertically) \n\n2. The player also needs to block a tile, this tile can be any tile on the map, as long as it's a free tile. \n\nThe win condition is when your opponent can no longer step anywhere. \n\nColours:\nGreen - You, the player\nRed - The bot\nGrey - blocked tile\nWhite - free tile")
    button_mode3.pack()
    button_mode5.pack()
    who_starts.pack()
    tutorial_text.pack()
    master.mainloop()


tile_nr=0
master = Tk()
turn = IntVar()
game_array = 0
player = Contestant(0,0)
bot = Contestant(0,0)

interface_menu()