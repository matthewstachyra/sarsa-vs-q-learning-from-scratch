import random
import numpy as np

class Agent:
    def __init__(self, env):
        self.env = env
        self.s = env.get_start()
        self.x = self.s[0]
        self.y = self.s[1]
        self.a = [[1,0], [0,1], [-1,0], [0,-1]]
    
    def get_actions(self):
        return self.a
    
    def reset_agent(self):
        self.s = self.env.get_start()
    
    def get_start(self):
        self.s = self.env.get_start()
        return self.s
    
    def get_valid_actions(self, x, y):
        # valid is defined here as those actions where you
        # don't go out of bounds
        alist = []
        for a in self.a:
            nx = x - a[0]
            ny = y + a[1]
            # ensure that the new x and new y are not out 
            # of the array bounds
            if not self.env.stepped_out_of_bounds(nx, ny):
                alist.append(a)
        return alist
        