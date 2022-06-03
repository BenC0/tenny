import enum
from turtle import pos
from matplotlib.style import available
import numpy as np

class Player:
    def __init__(self, gui):
        self.gui = gui
        self.points = gui.game.get_points()
        self.hand = gui.game.current_blocks
        self.field = gui.game.field
        self.reset_target()

    class Event:
        def __init__(self, coords):
            self.x = coords[0] * 50
            self.y = coords[1] * 50

    def play(self):
        if self.final_preview_shown:
            self.set_target_to_first_available_space()
            self.select_block(self.target_block)
            self.place_block()
            print(f"Moves played: {self.gui.moves_played}, Score: {self.gui.game.get_points()}")
            self.reset_target()
        
        if self.all_possible_spaces == None:
            self.find_all_possible_spaces()
        
        if self.previews == None:
            self.update_previews()
        
        if self.previews != None:
            self.update_current_preview()

        if self.preview_shown >= 1:
            self.update_current_preview()
        else:
            self.show_possible_preview()
    
    def update_current_preview(self):
        try:
            self.preview_shown = 0
            self.current_preview = next(self.previews)
        except StopIteration:
            self.previews = None
            self.final_preview_shown = True
    
    def update_previews(self):
        self.previews = iter(self.all_possible_spaces)
    
    def show_possible_preview(self):
        if self.current_preview != None:
            self.select_block(self.current_preview[0])
            self.gui.render_preview(self.Event((self.current_preview[1], self.current_preview[2])))
            self.preview_shown += 1

    def find_all_possible_spaces(self):
        self.all_possible_spaces = []
        count = 0
        for i in range(0, len(self.hand)):
            self.target_block = i
            self.select_block(self.target_block)
            for row_num, row in enumerate(self.field):
                for col_num, col in enumerate(row):
                    count += 1
                    fuckingFitsMaybe = self.gui.game.fits(row_num, col_num, self.gui.game.selected_block.coord_array)
                    if fuckingFitsMaybe:
                        self.all_possible_spaces.append((i, row_num, col_num))
        
        print(f"Spaces evaluated: {count}, Possible spaces found: {len(self.all_possible_spaces)}")

    def reset_target(self):
        self.target_block = 0
        self.target_coord = (-1, -1)
        self.previews = None
        self.preview_shown = 0
        self.current_preview = None
        self.all_possible_spaces = None
        self.final_preview_shown = False

    
    def set_target_to_first_available_space(self):
        possible_spaces = self.all_possible_spaces
        first_available = possible_spaces[0]
        self.target_block = first_available[0]
        self.target_coord = (first_available[1], first_available[2])

    def update_hand(self, hand):
        print("Updating hand")
        self.hand = hand

    def select_block(self, i):
        target_block = self.hand[i]
        target_block.select_block(None)
    
    def place_block(self):
        print(f"Placing block {self.target_block} at {self.target_coord}")
        
        event = self.Event(self.target_coord)
        self.gui.canvas_click(event)
        self.target_coord = (0, 0)