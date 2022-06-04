import enum, copy
from turtle import pos
from xmlrpc.client import Boolean
from matplotlib.style import available
import numpy as np
from scipy import ndimage

class Player:
    def __init__(self, gui):
        self.gui = gui
        self.points = gui.game.get_points()
        self.hand = gui.game.current_blocks
        self.field = gui.game.field
        # self.brrrrr = True
        self.brrrrr = False
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
            # self.set_target_to_most_lines_cleared()
            self.set_target_to_most_lines_and_least_gaps()
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
        for line in range(0, 10):
            columns_filled = 0
            for column in range(0, 10):
                if preview[line][column] == 1:
                    columns_filled += 1
                else:
                    break
            if columns_filled == 10:
                print("Line is full")
                lines_filled += 1
        return lines_filled
    
    def check_columns(self, preview):
        columns_filled = 0
        for column in range(0, 10):
            lines_filled = 0
            for line in range(0, 10):
                if preview[line][column] == 1:
                    lines_filled += 1
                else:
                    break
            if lines_filled == 10:
                print("Column is full")
                columns_filled += 1
        return columns_filled

    def add_shape(self, input_field, shape, xy, val = 1):
        field = copy.deepcopy(input_field)
        for x, y in shape:
            field[y + xy[1]][x + xy[0]] = val
        return field

    def invert_preview(self, preview):
        inverted = []
        for row in preview:
            inverted_row = []
            for val in row:
                inverted_row.append(~val)
            inverted += inverted_row

        return inverted

    def handle_labels(self, val, pos):
        # if val[0] == 0:
        #     return 1
        return val[0]

    def get_preview_gappiness(self, preview):
        gaps = 0
        inverted = self.invert_preview(preview)
        lbl, nlbl = ndimage.label(inverted)
        labels = np.arange(1, nlbl + 1)
        m = ndimage.median(inverted, labels=lbl)
        comp = ndimage.labeled_comprehension(inverted, lbl, labels, self.handle_labels, int, -1, True)
        gaps = sum(comp)
        return (gaps, m)

    def preview_placement(self, shape, offset, field):
        return self.add_shape(field, shape, offset)

    def set_target_to_most_lines_and_least_gaps(self):
        possible_spaces = self.all_possible_spaces
        scored_spaces = []
        for key, space in enumerate(possible_spaces):
            offset, shape, = (space[1], space[2]), space[3]
            field = copy.deepcopy(self.gui.game.field)
            preview = self.preview_placement(shape, offset, field)
            space_surrounds = self.check_shape_surrounds(shape, offset, self.gui.game.field)
            gappiness = self.get_preview_gappiness(preview)[0]
            comp = self.get_preview_gappiness(preview)
            lines = self.check_lines(preview)
            columns = self.check_columns(preview)
            immediate_gaps = ~len(space_surrounds[0])
            borders = len(space_surrounds[1])
            detail_str = f"\n - gappiness: {gappiness},"
            detail_str += f"\n - lines + columns: {lines + columns},"
            detail_str += f"\n - borders: {borders},"
            detail_str += f"\n - immediate_gaps: {immediate_gaps}"
            detail_str += f"\n - combined_gappiness: {gappiness + immediate_gaps},"
            detail_str += f"\n - combined_line_completion: {lines + columns},"
            detail_str += f"\n - final_result: {(gappiness + immediate_gaps) - (lines + columns) + borders},"
            detail_str += f"\n - comp: {comp}"
            scored_spaces.append([key, (gappiness) + (lines + columns) + gappiness, preview, detail_str])

        should_we_sort = sum([x[1] for x in scored_spaces])
        if should_we_sort > 0:
            scored_spaces.sort(key=lambda x: x[1], reverse=True)
        most_lines = scored_spaces[0]
        most_lines_space = possible_spaces[most_lines[0]]
        print(f"most_lines: {most_lines}")
        print(f"most_lines_space: {most_lines_space}")
        print(f"most_lines details: {most_lines[3]}")
        self.print_field(most_lines[2])
        self.set_target(most_lines_space)

    def set_target_to_most_lines_cleared(self):
        possible_spaces = self.all_possible_spaces
        scored_spaces = []
        for key, space in enumerate(possible_spaces):
            offset, shape, = (space[1], space[2]), space[3]
            field = copy.deepcopy(self.gui.game.field)
            preview = self.preview_placement(shape, offset, field)
            lines = self.check_lines(preview)
            columns = self.check_columns(preview)
            scored_spaces.append([key, lines + columns, preview])

        should_we_sort = sum([x[1] for x in scored_spaces])
        if should_we_sort > 0:
            scored_spaces.sort(key=lambda x: x[1], reverse=True)
        most_lines = scored_spaces[0]
        most_lines_space = possible_spaces[most_lines[0]]
        print(f"most_lines: {most_lines}")
        print(f"most_lines_space: {most_lines_space}")
        self.print_field(most_lines[2])
        self.set_target(most_lines_space)
        
    def print_field(self, field):
        print("Placement found, logging preview rows")
        for row in field:
            print(row)
        print("All preview rows logged")

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
        evaluated_spaces = []
        count = 0
        for i in range(0, len(self.hand)):
            self.target_block = i
            self.select_block(self.target_block)
            for r in range(0, 10):
                for c in range(0, 10):
                    if (r, c, self.gui.game.selected_block.coord_array) not in evaluated_spaces:
                        count += 1
                        evaluated_spaces.append((r, c, self.gui.game.selected_block.coord_array))
                        fuckingFitsMaybe = self.gui.game.fits(r, c, self.gui.game.selected_block.coord_array)
                        if fuckingFitsMaybe:
                            self.all_possible_spaces.append((i, r, c, self.gui.game.selected_block.coord_array))
        self.all_possible_spaces = self.remove_duplicate_spaces()
        print(f"Spaces evaluated: {count}, Possible spaces found: {len(self.all_possible_spaces)}")

    def remove_duplicate_spaces(self):
        stripped_spaces, deduped = [], []
        for space in self.all_possible_spaces:
            de_indexed = (space[1], space[2], space[3])
            if de_indexed in stripped_spaces:
                stripped_spaces.append(de_indexed)
            else:
                deduped.append(space)
        return deduped

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
        print(f"Setting Target: {target}")
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