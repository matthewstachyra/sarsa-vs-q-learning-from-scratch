import random
import numpy as np

class Environment:
    def __init__(self, f):
        self.file = f
        self.lines = self.convert_file()
        self.cliff = self.build_cliff()
        self.rmap = { "0" : -100, "1" : -1, "f" : -1, "s" : -1 }
    
    def convert_file(self):
        lines = []
        with open(self.file) as f:
            lines = f.readlines()
        return lines
    
    def build_cliff(self):
        cliff = []
        for i in range(len(self.lines)):
            level = []
            for j in range(len(self.lines[i])):
                if self.lines[i][j] != '\n':
                    level.extend(self.lines[i][j])
            cliff.append(level)
        return np.asarray(cliff)

    def get_cliff(self):
        return self.cliff
    
    def print_env(self):
        for l in self.lines:
            print(l, end="")
    
    def get_start(self):
        # returns the starting position
        # here, there is only one possibility
        ixs = np.argwhere(self.cliff=='s').tolist()
        i = np.random.choice(len(ixs), 1)
        s = ixs[i[0]]
        self.start = s
        return self.start

    def stepped_off_cliff(self, x, y):
        # checks whether the agent is stepping off the 
        # cliff with the current action
        return self.cliff[x][y] == '0'

    def stepped_out_of_bounds(self, x, y):
        if x<0 or y<0 or x>=len(self.cliff) or y>=len(self.cliff[0]):
            return True
        return False 
    
    def finished(self, x, y):
        return self.cliff[x][y] == 'f'
    
    def get_reward(self, x, y):
        mpos = self.cliff[x][y]
        return self.rmap[mpos]
        