import enum, copy
from turtle import pos
from matplotlib.style import available
import numpy as np

class Player:
    def __init__(self, gui):
        self.gui = gui
        self.points = gui.game.get_points()
        self.hand = gui.game.current_blocks
        self.field = gui.game.field
        self.brrrrr = True
        # self.brrrrr = False
        self.reset_target()

    class Event:
        def __init__(self, coords):
            self.x = coords[0] * 50
            self.y = coords[1] * 50

    def play(self):
        if self.final_preview_shown or (self.brrrrr and self.all_possible_spaces != None):
            # self.set_target_to_first_available_space()
            # self.set_target_to_least_gaps()
            # self.set_target_to_most_borders()
            self.set_target_to_most_lines_cleared()
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
    
    def check_lines(self, preview):
        lines_filled = 0
        for row in range(0, 10):
            row_count = 0
            for column in range(0, 10):
                row_count += preview[row][column]
            if row_count == 10:
                lines_filled += 1
        return lines_filled     
    
    def check_columns(self, preview):
        columns_filled = 0
        for column in range(0, 10):
            col_count = 0
            for row in range(0, 10):
                col_count += preview[row][column]
            if col_count == 10:
                columns_filled += 1
        return columns_filled        

    def add_shape(self, input_field, shape, xy, val = 1):
        field = copy.deepcopy(input_field)
        for x, y in shape:
            field[x + xy[0]][y + xy[1]] = val
        return field

    def preview_placement(self, shape, offset, field):
        return self.add_shape(field, shape, offset)

    def set_target_to_most_lines_cleared(self):
        field = copy.deepcopy(self.gui.game.field)
        possible_spaces = self.all_possible_spaces
        scored_spaces = []
        for key, space in enumerate(possible_spaces):
            offset, shape, = (space[1], space[2]), space[3]
            preview = self.preview_placement(shape, offset, field)
            lines = self.check_lines(preview)
            columns = self.check_columns(preview)
            scored_spaces.append([key, lines + columns])

        scored_spaces.sort(key=lambda x: x[1], reverse=True)
        most_lines = scored_spaces[0]
        most_lines_space = possible_spaces[most_lines[0]]
        print(f"most_lines: {most_lines}")
        print(f"most_lines_space: {most_lines_space}")
        self.set_target(most_lines_space)

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
                        self.all_possible_spaces.append((i, row_num, col_num, self.gui.game.selected_block.coord_array))
        
        print(f"Spaces evaluated: {count}, Possible spaces found: {len(self.all_possible_spaces)}")

    def reset_target(self):
        self.target_block = 0
        self.target_coord = (-1, -1)
        self.previews = None
        self.preview_shown = 0
        self.current_preview = None
        self.all_possible_spaces = None
        self.final_preview_shown = False
        self.evaluating = False

    def is_first(self, x):
        return x == 0

    def is_last(self, x):
        return x == 9

    def get_true_coords(self, coord, offset):
        return (coord[0] + offset[0], coord[1] + offset[1])

    def coord_is_full(self, field, coord):
        if coord == None:
            return True
        else:
            return field[coord[0]][coord[1]] == 1

    def get_coord_neighbours(self, x, y):
        neighbours = []
        top_neighbour = None
        left_neighbour = None
        right_neighbour = None
        bottom_neighbour = None
        top_left_neighbour = None
        top_right_neighbour = None
        bottom_left_neighbour = None
        bottom_right_neighbour = None

        if self.is_first(x) == False:
            left_neighbour = (x - 1, y)

        if self.is_last(x) == False:
            right_neighbour = (x + 1, y)

        if self.is_first(y) == False:
            top_neighbour = (x, y - 1)

        if self.is_last(y) == False:
            bottom_neighbour = (x, y + 1)

        if self.is_first(x) == False and self.is_first(y) == False:
            top_left_neighbour = (x - 1, y - 1)

        if self.is_first(x) == False and self.is_last(y) == False:
            top_right_neighbour = (x - 1, y + 1)

        if self.is_last(x) == False and self.is_first(y) == False:
            bottom_left_neighbour = (x + 1, y - 1)

        if self.is_last(x) == False and self.is_last(y) == False:
            bottom_right_neighbour = (x + 1, y + 1)
        
        neighbours.append(left_neighbour)
        neighbours.append(right_neighbour)
        neighbours.append(top_neighbour)
        neighbours.append(bottom_neighbour)
        neighbours.append(top_left_neighbour)
        neighbours.append(top_right_neighbour)
        neighbours.append(bottom_left_neighbour)
        neighbours.append(bottom_right_neighbour)
        return neighbours

    def get_shape_neighbours(self, coords):
        all_neighbours = []
        for x, y in coords:
            neighbours = self.get_coord_neighbours(x, y)
            all_neighbours = all_neighbours + [neighbour for neighbour in neighbours if neighbour not in coords]
        return all_neighbours

    def check_shape_surrounds(self, shape, offset, field):
        true_shape = [self.get_true_coords(coord, offset) for coord in shape]
        neighbours = self.get_shape_neighbours(true_shape)
        neighbour_gaps = [coord for coord in neighbours if self.coord_is_full(field, coord) == False]
        neighbour_borders = [coord for coord in neighbours if self.coord_is_full(field, coord)]
        return (neighbour_gaps, neighbour_borders)

    def set_target_to_most_borders(self):
        possible_spaces = self.all_possible_spaces
        scored_spaces = []
        for key, space in enumerate(possible_spaces):
            offset, shape, = (space[1], space[2]), space[3]
            space_surrounds = self.check_shape_surrounds(shape, offset, self.gui.game.field)
            scored_spaces.append([key, len(space_surrounds[1])])

        scored_spaces.sort(key=lambda x: x[1], reverse=True)
        most_borders = scored_spaces[0]
        most_borders_space = possible_spaces[most_borders[0]]
        self.set_target(most_borders_space)

    def set_target_to_least_gaps(self):
        possible_spaces = self.all_possible_spaces
        scored_spaces = []
        for key, space in enumerate(possible_spaces):
            offset, shape, = (space[1], space[2]), space[3]
            space_surrounds = self.check_shape_surrounds(shape, offset, self.gui.game.field)
            scored_spaces.append([key, len(space_surrounds[0])])

        scored_spaces.sort(key=lambda x: x[1])
        least_gaps = scored_spaces[0]
        least_gaps_space = possible_spaces[least_gaps[0]]
        self.set_target(least_gaps_space)
    
    def set_target_to_first_available_space(self):
        possible_spaces = self.all_possible_spaces
        first_available = possible_spaces[0]
        self.set_target(first_available)
    
    def set_target(self, target):
        self.target_block = target[0]
        self.target_coord = (target[1], target[2])

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