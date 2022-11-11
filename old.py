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
        
    def reset(self):
        # reset the agent and the stored episode
        # this is used after each run
        # therefore we do not reset the stored Q values or returns because these continue to be used
        # in the update steps
        self.agent.reset_agent()
        self.episode = {}
    
    def initialize(self):
        # what form should Q have here?
        # it should hold both the state and action
        # the state is x and y as (x, y)
        # the action is the change to x and y as [dx, dy]
        # so key for Q is [x, y, dx, dy]
        d = {}
        hvelocities = vvelocities = [0,1,2,3,4]
        for x in range(len(self.env.get_cliff())):
            for y in range(len(self.env.get_cliff()[x])):
                for a in self.agent.get_actions():
                    dx = a[0]
                    dy = a[1]
                    s = [x, y, dx, dy]
                    scopy = s.copy()
                    sprime = tuple(scopy)
                    d[sprime] = 0
        return d
        
    def generate_episode(self):
        # generating an episode means a generating
        # a sequence of state-action pairs that eventually
        # gets us to the goal state. we can think of this as
        # equivalent to a proposed solution to the 
        # MDP - "take these actions in these states,
        # with the goal of maximizing total discounted
        # reward"
        self.agent.reset_agent() # resets position of agent to start
        s = self.agent.get_start() # gets the start position of the agent
        x, y = s[0], s[1]
        a = self.get_next_action(x, y) # get starting action using policy
        s.extend(a)
        x = s[0]
        y = s[1]
        dx = s[2]
        dy = s[3]
        
        t = 0
        r = 0
        tr = r
        oob = 0
        
        while(not self.env.finished(x, y)):
            
            # start within initial action that was pre appended
            scopy = list(s).copy()
            x = scopy[0] - scopy[2]  # new x
            y = scopy[1] + scopy[3]  # new y

            # check out of bounds / update reward
            if self.env.stepped_out_of_bounds(x, y) or self.env.stepped_off_cliff(x, y):
                s = self.env.get_start() # [x, y, hv, vv]
                x, y = s[0], s[1]
                r = -100 # overwrite reward because out of bounds
                oob += 1
            else:
                r = self.env.get_reward(x, y)
                
            # update episode with old values (i.e., the reward is for t+1 and the state is that at t)
            self.episode[t] = ((scopy[0], scopy[1], scopy[2], scopy[3]), r)
 
            # then, get next action
            self.agent.update_agent(x, y)
            a = self.get_next_action(x, y)        # get next [dx, dy]

            # save to new state
            s = tuple([x, y, a[0], a[1]])
            
            # update time
            t += 1
            
            # track total reward for episode
            tr += r
            
        
        # append last episode (finish state), with reward 0
        self.episode[t] = ((x, y, a[0], a[1]), 0)
#         print(f"Finished in {t} steps with {tr} reward accumulated and went out of bounds {oob} times.")
    
    def get_next_action(self, x, y):
        if(np.random.binomial(1, self.e)): # 1 if exploring, 0 if exploiting
            # use random index to return an action from possible valid actions at this state
            return self.agent.get_valid_actions(x, y)[random.randint(0, len(self.agent.get_valid_actions(x, y))-1)]
        return self.get_greedy_action(self.agent.get_state()) # state returned has form (x, y)
    
    def get_greedy_action(self, state):
        # state here has form (x, y)
        
        # generate all sa pairs
        # this means creating 4 sa tuples for the 4 actions
        sas = []
        for a in self.agent.get_actions():
            sa = list(state)
            sa.extend(a)              # a has form [dx, dy]
            sas.append(tuple(sa))     # sas has form [(x, y, dx, dy), ...]
        
        
        # it is possible there are no valid actions
        valid_actions = self.agent.get_valid_actions(state[0], state[1])
            
        # if all q values are 0, then we don't have action values for the (s,a), so return random
        if sum([self.Q[sa] for sa in sas])==0: 
            return valid_actions[random.randint(0, len(valid_actions)-1)]
        # else, check least negative / largest q value and return that action
        ma = [0,0]
        mq = -11111111
        for sa in sas:
            if self.Q[sa] > mq:
                mq = self.Q[sa]
                ma = sa[-2:]
        return ma
    
    def optimal_policy(self):
        self.agent.reset_agent() # resets position of agent to start
        s = self.agent.get_start() # gets the start position of the agent
        x = s[0]
        y = s[1]
        a = self.get_next_action(x, y) # get starting action using policy
        s.extend(a)
        dx = s[2]
        dy = s[3]
        
        t = 0
        r = 0
        tr = r
        oob = 0
        
        while(not self.env.finished(x, y)):
            print(t)
            
            # start within initial action that was pre appended
            scopy = list(s).copy()
            x = scopy[0] - scopy[2]  # new x
            y = scopy[1] + scopy[3]  # new y

            # check out of bounds / update reward
            if self.env.stepped_out_of_bounds(x, y) or self.env.stepped_off_cliff(x, y):
                s = self.env.get_start() # [x, y, hv, vv]
                x, y, dx, dy = s[0], s[1], 0, 0
                r = -100 # overwrite reward because out of bounds
                oob += 1
            else:
                r = self.env.get_reward(x, y)
                
            # update episode with old values (i.e., the reward is for t+1 and the state is that at t)
            self.episode[t] = ((scopy[0], scopy[1], scopy[2], scopy[3]), r)
 
            # then, get next action
            self.agent.update_agent(x, y)
            a = self.get_greedy_action([x, y])        # get next [dx, dy]

            # save to new state
            s = tuple([x, y, a[0], a[1]])
            
            # update time
            t += 1
            
            # track total reward for episode
            tr += r
            
        
        # append last episode (finish state), with reward 0
        self.episode[t] = ((x, y, a[0], a[1]), 0)
        return self.episode
    
    def __call__(self):
        episodes_in_run = []
        for r in range(self.runs): # 50
            print(r+1)
            cr_by_episode = []
            self.Q = self.initialize() 
            for e in range(self.episodes): # 500
                self.reset()

                # # generated episodes will become better
                # # with each run
                # self.generate_episode()

                # reset cumulative reward sum
                tr = 0

                for t in range(len(self.episode)):
                    # each value in episode for some time step key is ((x, y, dx, dy), r)
                    # Q[sa] = Q[sa] + l[R + Q[sa_next]]
                    sa = self.episode[t][0] # current state and action in episode
                    s = sa[:-2]   # splice means "everything except last 2"

                    # get next state
                    if t+1 < len(self.episode):

                        # get reward for taking 'a' in 's'
                        r = self.episode[t][1]

                        # approach 1 - generate action for s'
                        # ----------
                        # get state from episode
                        s_prime = self.episode[t+1][0][:-2]
                        # on policy, so grab the next action according to an epsilon greedy approach
                        if(np.random.binomial(1, self.e)): # 1 if exploring, 0 if exploiting
                            a = self.agent.get_valid_actions(s_prime[0], s_prime[1])[random.randint(0, len(self.agent.get_valid_actions(s_prime[0], s_prime[1]))-1)]
                        else:
                            a = self.get_greedy_action(s_prime) # state returned has form (x, y)
                        # using next action, build the state 
                        s_prime = list(s_prime)
                        s_prime.extend(a)
                        sa_prime = tuple(s_prime)

                        # approach 2 - use the action that comes with the episode
                        # ----------
                        # using the next state and action in the episode
                        # sa_prime = tuple(self.episode[t+1][0])

                        # get target for this step
                        target = r + (self.d * self.Q[sa_prime])

                        # make update
                        self.Q[sa] = self.Q[sa] + self.l*(target - self.Q[sa])
                        tr += r
                cr_by_episode.append(tr)
            episodes_in_run.append(cr_by_episode)
        return episodes_in_run
























    def generate_episode(self):
        # generating an episode means a generating
        # a sequence of state-action pairs that eventually
        # gets us to the goal state. we can think of this as
        # equivalent to a proposed solution to the 
        # MDP - "take these actions in these states,
        # with the goal of maximizing total discounted
        # reward"
        self.agent.reset_agent() # resets position of agent to start
        s = self.agent.get_start() # gets the start position of the agent
        x, y = s[0], s[1]
        a = self.get_next_action(x, y) # get starting action using policy
        s.extend(a)
        x = s[0]
        y = s[1]
        dx = s[2]
        dy = s[3]
        
        t = 0
        r = 0
        tr = r
        oob = 0
        
        while(not self.env.finished(x, y)):
            
            # start within initial action that was pre appended
            # 
            scopy = list(s).copy()
            x = scopy[0] - scopy[2]  # new x
            y = scopy[1] + scopy[3]  # new y

            # check out of bounds / update reward
            if self.env.stepped_out_of_bounds(x, y) or self.env.stepped_off_cliff(x, y):
                s = self.env.get_start() # [x, y]
                x, y = s[0], s[1]
                r = -100 # overwrite reward because out of bounds
                oob += 1
            else:
                r = self.env.get_reward(x, y)
                
            # update episode with old values (i.e., the reward is for t+1 and the state is that at t)
            self.episode[t] = ((scopy[0], scopy[1], scopy[2], scopy[3]), r)
 
            # then, get next action
            self.agent.update_agent(x, y)
            a = self.get_next_action(x, y)        # get next [dx, dy]

            # save to new state
            s = tuple([x, y, a[0], a[1]])
            
            # update time
            t += 1
            
            # track total reward for episode
            tr += r
            
        
        # append last episode (finish state), with reward 0
        self.episode[t] = ((x, y, a[0], a[1]), 0)
#         print(f"Finished in {t} steps with {tr} reward accumulated and went out of bounds {oob} times.")






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
        d = {}
        for x in range(len(self.env.get_cliff())):
            for y in range(len(self.env.get_cliff()[x])):
                for a in self.agent.get_actions():
                    dx = a[0]
                    dy = a[1]
                    s = [x, y, dx, dy]
                    scopy = s.copy()
                    sprime = tuple(scopy)
                    d[sprime] = 0
        return d
    
    def get_next_action(self, x, y):
        if(np.random.binomial(1, self.e)): # 1 if exploring, 0 if exploiting
            # use random index to return an action from possible valid actions at this state
            return self.agent.get_valid_actions(x, y)[random.randint(0, len(self.agent.get_valid_actions(x, y))-1)]
        a = self.get_greedy_action(x, y) # state returned has form (x, y)
        return a[0], a[1] # dx, dy
    
    def get_greedy_action(self, x, y):
        # Q[(s,a)] has a scalar value, reward
        # (1) subset dict for those keys that in sas
        # (2) max(subset_dict, key=subset_dict.get)

        # print(f"greedy")

        sas = [tuple([x, y, a[0], a[1]]) for a in self.agent.get_actions()] # get keys
        # print(f"sas {sas}")
        subset_dict = {k:v for k, v in self.Q.items() if k in sas} # subset dict to keys
        idxs = max(subset_dict, key=subset_dict.get) # return key for max value
        return idxs[-2:]
    
        # # it is possible there are no valid actions
        # valid_actions = self.agent.get_valid_actions(x, y)
            
        # # if all q values are 0, then we don't have action values for the (s,a), so return random
        # if sum([self.Q[sa] for sa in sas])==0: 
        #     print(f"  random greedy")
        #     return valid_actions[random.randint(0, len(valid_actions)-1)]
        # # else, check least negative / largest q value and return that action
        # ma = [0,0]
        # mq = -11111111
        # for sa in sas:
        #     if self.Q[sa] > mq:
        #         mq = self.Q[sa]
        #         ma = sa[-2:]
        # print(f"  non-random greedy {ma}")
        # return ma
    
    # def optimal_policy(self):
    #     self.agent.reset_agent() # resets position of agent to start
    #     s = self.agent.get_start() # gets the start position of the agent
    #     x, y = s[0], s[1]
    #     a = self.get_next_action(x, y) # get starting action using policy
    #     s.extend(a)
    #     x = s[0]
    #     y = s[1]
    #     dx = s[2]
    #     dy = s[3]
        
    #     t = 0
    #     r = 0
    #     tr = r
    #     oob = 0
                
    #     while(not self.env.finished(x, y)):
    #         # (1) get reward for this state and action
    #         scopy = list(s).copy()
    #         x = scopy[0] - scopy[2]  # new x
    #         y = scopy[1] + scopy[3]  # new y
    #         if self.env.stepped_out_of_bounds(x, y) or self.env.stepped_off_cliff(x, y):
    #             s = self.env.get_start()
    #             x, y = s[0], s[1]
    #             r = -100 # overwrite reward because out of bounds
    #             oob += 1
    #         else:
    #             r = self.env.get_reward(x, y)

    #         # update episode with old values (i.e., the reward is for t+1 and the state is that at t)
    #         self.episode[t] = ((scopy[0], scopy[1], scopy[2], scopy[3]), r)
            
    #         # (2) then, get next action
    #         self.agent.update_agent(x, y)
    #         a = self.get_next_action(x, y)        # get next [dx, dy]

    #         # (3) get next state
    #         s_prime = tuple([x, y, a[0], a[1]])
    #         s = s_prime

            
    #         t += 1
    #         tr += r
            
        
        # append last episode (finish state), with reward 0
        self.episode[t] = ((x, y, a[0], a[1]), 0)
        return self.episode
    
    def update_state(self, old_x, old_y, old_dx, old_dy):
        r = -1 # set default reward

        # update state
        new_x = old_x - old_dx # subtract because going up means reducing index
        new_y = old_y + old_dy
 
        # check we go out of bounds
        #   update state and reward if out of bounds
        if self.env.stepped_out_of_bounds(new_x, new_y) or self.env.stepped_off_cliff(new_x, new_y):
            print(f"went out of bounds with {x, y}")
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
        # print(f"q updated from {oldq} to {self.Q[old_sa]}")
    
    def print_episode(self):
        for k, v in self.episode.items():
            print(f"{k} timestep : {v}")
        for _, v in self.Q.items():
            if v!= 0:
                print(v)

    
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
                a = self.get_next_action(x, y) 
                dx, dy = a[0], a[1]

                while(not self.env.finished(x, y)):
                    # print(t)
                    old_x, old_y, old_dx, old_dy = x, y, dx, dy
                    x, y, r = self.update_state(old_x, old_y, old_dx, old_dy)
                    
                    # print(f"  {t}  state {old_x, old_y} updated to {x, y}; reward {r}")

                    # self.agent.update_agent(x, y)
                    dx, dy = self.get_next_action(x, y)
                    # print(f"dx {dx} dy {dy}")
                    # print(f"params to update_q{old_x, old_y, old_dx, old_dy, x, y, dx, dy}")
                    self.update_q(old_x, old_y, old_dx, old_dy, x, y, dx, dy, r) 
                    self.episode[t] = ((old_x, old_y, old_dx, old_dy, self.Q[(old_x, old_y, old_dx, old_dy)]), r)
                    t += 1
                    tr += r
                # print(f"episode {e} total reward {tr}")
                cr_by_episode.append([tr])
                self.episode[t] = ((x, y, dx, dy, self.Q[(x, y, dx, dy)]), r)
                
                print(f"episode {e} had {t} timesteps")
            episodes_in_run.append(cr_by_episode) # outer dimension should be 10, with inner dimension 500
        return episodes_in_run
