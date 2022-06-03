from time import sleep
from matplotlib.style import available
import numpy as np

class Player:
    def __init__(self, gui):
        self.gui = gui
        self.points = gui.game.get_points()
        self.hand = gui.game.current_blocks
        self.field = gui.game.field
        self.target_block = 0
        self.target_coord = (-1, -1)

    def play(self):
        self.set_to_first_available_space()
        self.select_block(self.target_block)
        self.place_block()
        row_num, col_num = 0, 0
        self.target_block = 0
    
    def set_to_first_available_space(self):
        for i in range(0, len(self.hand)):
            self.target_block = i
            self.select_block(self.target_block)
            row_num = 0
            match_found = False
            for row in self.field:
                col_num = 0
                for col in row:
                    fuckingFitsMaybe = self.gui.game.fits(row_num, col_num, self.gui.game.selected_block.coord_array)
                    if fuckingFitsMaybe:
                        self.target_coord = (row_num, col_num)
                        match_found = True
                        break
                    col_num+=1
                else:
                    row_num+=1
                    continue
                break
            if match_found:
                break

    def update_hand(self, hand):
        print("Updating hand")
        self.hand = hand

    def select_block(self, i):
        target_block = self.hand[i]
        target_block.select_block(None)
    
    def place_block(self):
        print(f"Placing block {self.target_block} at {self.target_coord}")
        class Event:
            def __init__(self, coords):
                self.x = coords[0] * 50
                self.y = coords[1] * 50
        
        event = Event(self.target_coord)
        self.gui.canvas_click(event)
        self.target_coord = (0, 0)