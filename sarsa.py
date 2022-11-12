import random
import numpy as np


class SARSA:
    def __init__(self, epsilon, discount_rate, learning_rate, agent, environment, episodes, runs):
        self.e = epsilon
        self.d = discount_rate
        self.l = learning_rate
        self.env = environment
        self.agent = agent
        self.runs = runs
        self.episodes = episodes
        self.episode = {}              # e[t] = (s, r), where s or state is (x, y) and r is reward
        self.Q = self.initialize()     # Q[s] = q, where s includes both state and action information
                                       #           as a tuple (x, y, change_to_x, change_to_y)
    
    def initialize(self):
        # by default sets all Q values to 0
        d = {}
        for x in range(len(self.env.get_cliff())):
            for y in range(len(self.env.get_cliff()[x])):
                for a in self.agent.get_actions():
                    dx, dy = a[0], a[1]
                    s = [x, y, dx, dy]
                    d[tuple(s)] = 0
        return d


    def get_next_action(self, x, y):
        if(np.random.binomial(1, self.e)): # 1 if exploring, 0 if exploiting
            # valid here means not out of the bounds of the array
            #   but we still need to check whether it is "off the cliff"Agent
            #   incurring the -100 reward/penalty
            valid_actions = self.agent.get_valid_actions(x, y)
            exploring =  valid_actions[random.randint(0, len(valid_actions))-1]
            return exploring[0], exploring[1], "exploring"
        a = self.get_greedy_action(x, y) # state returned has form (x, y)
        return a[0], a[1], "greedy" # dx, dy
    

    def get_greedy_action(self, x, y):
        sas = [tuple([x, y, a[0], a[1]]) for a in self.agent.get_valid_actions(x, y)] 
        subset_dict = {k:v for k, v in self.Q.items() if k in sas} # subset dict to keys
        idxs = max(subset_dict, key=subset_dict.get) # return key for max value
        return idxs[-2:] # return (dx, dy) from (x, y, dx, dy)
    
    
    def update_state(self, old_x, old_y, old_dx, old_dy):
        r = -1 # set default reward
        # update state
        new_x = old_x - old_dx # subtract because going up means reducing index
        new_y = old_y + old_dy
        # check whether (x,y) is out of array bounds or "off the cliff"
        if self.env.stepped_out_of_bounds(new_x, new_y) or self.env.stepped_off_cliff(new_x, new_y):
            s = self.env.get_start()
            new_x, new_y = s[0], s[1]
            r = -100
        return new_x, new_y, r


    def update_q(self, old_x, old_y, old_dx, old_dy, new_x, new_y, new_dx, new_dy, r):
        # s, s'
        old_sa = tuple([old_x, old_y, old_dx, old_dy])
        new_sa = tuple([new_x, new_y, new_dx, new_dy])
        # set target
        target = r + (self.d * self.Q[new_sa])
        # make on policy update
        #   it is on policy because the key (state, action pair) where we update the q function
        #   is the same as the one that generated the action
        oldq = self.Q[old_sa]
        self.Q[old_sa] = oldq + self.l*(target - oldq)

    
    def run(self, r=1, e=1):
        i = r
        episodes_in_run = []
        while i != 0: 
            cr_by_episode = [] # appended to 500 times
            j = e
            while j != 0:
                self.episode = {}
                t = 0
                tr = 0
                s = self.agent.get_start() 
                x, y = s[0], s[1]
                dx, dy, _ = self.get_next_action(x, y) 
                while(not self.env.finished(x, y)):
                    old_x, old_y, old_dx, old_dy = x, y, dx, dy
                    x, y, r = self.update_state(old_x, old_y, old_dx, old_dy)
                    dx, dy, _ = self.get_next_action(x, y)
                    self.update_q(old_x, old_y, old_dx, old_dy, x, y, dx, dy, r) 
                    self.episode[t] = ((old_x, old_y, old_dx, old_dy), r)
                    t += 1
                    tr += r
                cr_by_episode.append([tr])
                self.episode[t] = ((x, y, dx, dy), r)
                j -= 1
            episodes_in_run.append(cr_by_episode)
            i -= 1
        return self.episode, episodes_in_run # return the last episode created
    

    def change_env(self, env):
        # changed environemnt to use experimentally
        self.env = env


    def DEBUG_PRINT(self, timestep, old_x, old_y, old_dx, old_dy, x, y, dx, dy, atype):
        # [0] print time step
        print(timestep)

        # [1] details about state-action update
        print(f"{old_x, old_y} and {old_dx, old_dy} -> {x, y} and {dx, dy}")

        # [2] details about action
        #   whether greedy or exploratory
        #   what q key-value pairs it was selected from
        sa_pairs = [(old_x, old_y, _dx, _dy) 
                    for _dx, _dy 
                    in self.agent.get_valid_actions(old_x, old_y)]
        qvalues = [(sa, self.Q[sa]) for sa in sa_pairs]
        print(f"{dx, dy} action selected was {atype} from {qvalues}")

        # new line to indicate new episode
        print()
    

    def __call__(self):
        episodes_in_run = []
        for r in range(self.runs): # 50
            self.Q = self.initialize() 
            cr_by_episode = []

            # Main loop
            #   Each episode ends when the agent's position (x, y)
            #   is at the finish state.
            #   
            #   Episode starts with (x, y, dx, dy) - an initial position
            #   an an initial action. The q value for this state-action
            #   pair is based on the q value of the very next state and
            #   the reward we get in this state.
            for e in range(self.episodes): # 500
                self.episode = {}
                t = 0
                r = 0
                tr = r

                # state
                s = self.agent.get_start() 
                x, y = s[0], s[1]

                # action
                dx, dy, atype = self.get_next_action(x, y) 

                while(not self.env.finished(x, y)):
                    old_x, old_y, old_dx, old_dy = x, y, dx, dy
                    x, y, r = self.update_state(old_x, old_y, old_dx, old_dy)
                    dx, dy, atype = self.get_next_action(x, y)
                    self.update_q(old_x, old_y, old_dx, old_dy, x, y, dx, dy, r) 
                    self.episode[t] = ((old_x, old_y, old_dx, old_dy), r)
                    # self.DEBUG_PRINT(t, old_x, old_y, old_dx, old_dy, x, y, dx, dy, atype)
                    t += 1
                    tr += r
                cr_by_episode.append([tr])
                self.episode[t] = ((x, y, dx, dy), r)
            episodes_in_run.append(cr_by_episode) # outer dimension should be 10, with inner dimension 500
        return episodes_in_run
