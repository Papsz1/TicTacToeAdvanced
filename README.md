# TicTacToeAdvanced

A simple game played between a player and a bot made to test and try out the minimax algorithm.
It implements a simple minimax algorithm and an optimised one with heuristics, such as alfa-beta cutting, dynamic depth and oher, more specific ones,
the details of which can be found in the code.

Needs python 3.7 and up because of the usage of dataclass.

The game is played as follows:
1. The player needs to pick a surrounding tile that he wants to step into (the player can move diagonally, horizontally or vertically) 
2. The player also needs to block a tile, this tile can be any tile on the map, as long as it's a free tile. 

The win condition is when your opponent can no longer step anywhere. 

Colours:
Green - You, the player

Red - The bot

Grey - blocked tile

White - free tile
