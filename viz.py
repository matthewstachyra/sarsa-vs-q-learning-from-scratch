import random
import numpy as np

class GridWorldViz:
    def __init__(self, RL_learner):
        self.RL = RL_learner
        self.dimension = self.RL.env.cliff.shape
        self.dirmap = { (1, 0) : "[^]", 
                        (0, 1) : "[>]", 
                        (-1, 0) : "[v]", 
                        (0, -1) : "[<]" }
         
    def draw_policy(self):
        '''Print out cliff world with the optimal actions (left, right, up, down)
        overlaid on each state in the gridworld.
        '''
        # for each state, gets the action that produces the max value
        # actions are mapped as follows
        # dx  dy        
        # ------
        # [1, 0]  is > (right)
        # [0, 1]  is v (down)
        # [-1, 0] is < (left)
        # [0, -1] is ^ (up)
        #
        # the character for the direction is placed within "[" and "]" 
        
        maxx = self.dimension[0]
        maxy = self.dimension[1]
        for x in range(maxx):
            row = []
            for y in range(maxy):
                # get the greedy action
                ga = self.RL.get_greedy_action(x, y)
                if self.RL.env.cliff[x][y] != '0':
                    row.append(self.dirmap[tuple(ga)])
                # do not append a direction if it is the cliff
                else:
                    row.append("[ ]")
            print(''.join(row))
    
    def draw_episode(self, episode):
        # built dict with movement boxes
        # key is position, value is the movement box
        d = { sa[0][:-2] : self.dirmap[sa[0][-2:]] for sa in episode.values() }
        maxx = self.dimension[0]
        maxy = self.dimension[1]
        for x in range(maxx):
            row = []
            for y in range(maxy):
                if (x,y) in d.keys():
                    row.append(d[(x,y)])
                else:
                    row.append("[ ]")
            print(''.join(row))