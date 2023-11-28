import numpy as np
import pygame
import random as r
import gymnasium as gym
from gymnasium import spaces
import math as m
import csv
import pandas as pd
import time

 ### AVOIDANCE

def rotate_point(point, axis, angle_degrees):
    # Convert angle from degrees to radians
    angle_radians = m.radians(angle_degrees)
    
    # Unpack the point and axis coordinates
    x, y = point
    axis_x, axis_y = axis

    # Translate the point so that the axis is at the origin
    translated_x = x - axis_x
    translated_y = y - axis_y

    # Perform the rotation using trigonometric functions
    rotated_x = translated_x * m.cos(angle_radians) - translated_y * m.sin(angle_radians)
    rotated_y = translated_x * m.sin(angle_radians) + translated_y * m.cos(angle_radians)

    # Translate the point back to its original position
    rotated_x += axis_x
    rotated_y += axis_y

    return (rotated_x, rotated_y)

def getRange(point1, point2):
    dX = abs(point1.x-point2.x)
    dY = abs(point1.y-point2.y)
    range = m.sqrt(dX**2 +  dY**2)
    return range

def getBearing(point1, point2, heading):
    dX = (point2.x-point1.x)
    dY = -1*(point2.y-point1.y)
    #print(dX, dY)
    if dY ==0 and dX>0:
        trueBearing = 90
    elif dY ==0 and dX<0:
        trueBearing = 270
    else:
        trueBearing = m.degrees(m.atan(dX/dY))
        if dX >0 and dY>0:#TR
            trueBearing = trueBearing
        elif dX >0 and dY<0:#BR
            trueBearing = 180+trueBearing
            #print("BR:", 180+ trueBearing)
        elif dX <0 and dY<0:#BL
            trueBearing = 180+trueBearing
        elif dX <0 and dY>0:#TL
            trueBearing = 360+trueBearing

    
    relBearing = trueBearing-heading
    if relBearing <-180:
        relBearing = 180-(abs(relBearing)-180)
    if relBearing <0:
        relBearing = 360+relBearing
    #print(relBearing, heading, trueBearing)
    if relBearing < 0 or relBearing > 360:
        print(point1, point2, heading)
        print(dX, dY)
        print(trueBearing)
        print(heading)
        print(relBearing)
        #the problem might be heading not being between 0 and 360
    return relBearing

def getBearing180(point1, point2, heading):
    dX = (point2.x-point1.x)
    dY = -1*(point2.y-point1.y)
    #print(dX, dY)
    if dY ==0 and dX>0:
        trueBearing = 90
    elif dY ==0 and dX<0:
        trueBearing = 270
    else:
        trueBearing = m.degrees(m.atan(dX/dY))
        if dX >0 and dY>0:#TR
            trueBearing = trueBearing
        elif dX >0 and dY<0:#BR
            trueBearing = 180+trueBearing
            #print("BR:", 180+ trueBearing)
        elif dX <0 and dY<0:#BL
            trueBearing = 180+trueBearing
        elif dX <0 and dY>0:#TL
            trueBearing = 360+trueBearing

    
    relBearing = trueBearing-heading
    if relBearing <-180:
        relBearing = 180-(abs(relBearing)-180)
    if relBearing >360:
        relBearing = -relBearing - 360
    #print(relBearing, heading, trueBearing)
    return abs(relBearing)

class CustomEnv(gym.Env):

    def __init__(self):
        print("INIT")
        self.render_mode="human"
        self.width = 1000
        self.height = 1000

        #logging
        with open("liveLogs/log.csv", mode='w', newline='') as csv_file:
            # Create a CSV writer object
            csv_writer = csv.writer(csv_file)
            headers = ["episode", "result", "length", "reward"]
            # Write the headers to the CSV file
            csv_writer.writerow(headers)
        

        #DEFINE THE SPACE
        # one pixel  = 100m
        self.pixelDistance = 100
         # one timejump = 10seconds
         # ownship can vary 1degree per timejump
        self.numberObstacles = 1

        self.window = None
        self.clock = 0
        self.dt=10 #ten seconds per jump
        self.speed = 10 #metres per second
        self.count = 0
        self.episodes = 0

        # We have 4 actions, corresponding to "right", "up", "left", "down"
        #self.action_space = spaces.MultiDiscrete([3,3])
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Discrete(361)
         # new observation
        self.observation_space = spaces.MultiDiscrete([(361) for i in range(1+self.numberObstacles)])
        print(self.observation_space.sample())

    def _get_obs(self):
        obs = []
        obs.append(int(getBearing(self.player_pos, self.finish_pos, self.heading)))
        for obstacle in self.obstacles:
            obs.append(int(getBearing(self.player_pos, obstacle, self.heading)))
        return np.array(obs)
    
    def reset(self, seed=None, options=None):
        #print("RESET")
        # Choose the agent's location
        self.player_pos = pygame.Vector2(self.width / 2, self.height / 2)
        self.heading = r.randrange(0,360)
        # choose the finish location
        bearing = r.randrange(0,360)
        range = r.randrange(700, 900)
        self.episodes+=1

         # create finish 
        print("Bearing:", bearing)
        if bearing<=180:
            x = self.player_pos.x + (range*m.sin(m.radians(bearing)))
            xObstacle = self.player_pos.x + (range*m.sin(m.radians(bearing)))/2
        else:
            x = self.player_pos.x - (range*m.sin(m.radians(bearing)))
            xObstacle = self.player_pos.x - (range*m.sin(m.radians(bearing)))/2
        if bearing<=90 or bearing>=270:
            y = self.player_pos.y + (range*m.cos(m.radians(bearing)))
            yObstacle = self.player_pos.y + (range*m.cos(m.radians(bearing)))/2
        else:
            y = self.player_pos.y - (range*m.cos(m.radians(bearing)))
            yObstacle = self.player_pos.y - (range*m.cos(m.radians(bearing)))/2
        self.finish_pos = pygame.Vector2(x, y)

         # create obstacles
        self.obstacles = []
        self.obstacleBearing = {}
        for i in range(self.numberObstacles):
            print(i)
            self.obstacles.append(pygame.Vector2(xObstacle, yObstacle))
            print(self.obstacles)
            print("done")
            self.obstacleBearing[str(i)] = getBearing(self.player_pos, pygame.Vector2(x, y), self.heading)

        self.startRange = getRange(self.player_pos, self.finish_pos)
        # reset the display
        self.running = True
        self.clock = 0
        # get starting observation
        observation = self._get_obs()
        info = {}
        self.count+=1
        #print(self.count)
        return observation, info
    
    def step(self, action):
        #self.speed += (action[0] -1)
        #self.heading += (action[1] -1)
        #print(self.targetRange)
        print(action)
        success = False
        oldBearing = getBearing180(self.player_pos, self.finish_pos, self.heading)
        self.heading+=action-1
        if self.heading > 360:
            self.heading = self.heading-360
        elif self.heading <0:
            self.heading = self.heading + 360
        prevRange = getRange(self.player_pos, self.finish_pos)
        #print(self.heading, self.speed)
        self.player_pos.y -= self.speed*m.cos(m.radians(self.heading)) * self.dt/self.pixelDistance
        self.player_pos.x += self.speed*m.sin(m.radians(self.heading)) * self.dt/self.pixelDistance

        
        newRange = getRange(self.player_pos, self.finish_pos)
        newBearing = getBearing180(self.player_pos, self.finish_pos, self.heading)
        observation = self._get_obs()
        #print("Obs: ", observation)

         ### creat obstacle aversion component ###
        obstacleReward = 0
        for obstacle, i in self.obstacles:
            oldBearingContact = self.obstacleBearing[str(i)]
            range = getRange(self.player_pos, obstacle)
            bearing = getBearing180(self.player_pos, obstacle, self.heading)
            if range < 100:
                print("obstacle:", oldBearingContact, bearing)
                obstacleReward+=bearing-oldBearingContact
            self.obstacleBearing[str(obstacle)] = bearing
            if range<=25:
                collision = True
                break
            else:
                collision = False
        
        #have we reached the target
        if newRange <= 40:
            terminated = True
            success = True
            Result = "Complete"
            print("Complete")
            reward=1000
        #check out of bounds
        elif self.player_pos.x > self.width or self.player_pos.x < 0 or self.player_pos.y > self.height or self.player_pos.y < 0:
            terminated = True
            reward = -100
            Result = "Edge"
            print("border")
        #check contact collision
        elif collision:
            terminated = True
            Result = "collision"
            reward = -100
        #check time
        elif self.clock >200000:
            print("TIMEOUT", self.clock)
            terminated = True
            reward = -100
            Result = "Timeout"
        else:
            terminated=False
            #still in progress
            reward = 5*(prevRange-newRange)+(oldBearing-newBearing) + obstacleReward
            print("finish:", oldBearing, newBearing)
            print("Reward:", reward, 5*(prevRange-newRange), oldBearing-newBearing , obstacleReward)
             # add component for avoiding contacts, detract points if current heading puts contact in path
        
        self.reward+=reward
        if terminated:
            data = [self.episodes, Result, self.clock, self.reward]
            with open("liveLogs/log.csv", 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(data)


        self.clock = self.clock+self.dt
        info = {"status": success, "time": self.clock, "targetRange": self.startRange }
        #print(self.clock, observation, reward, self.player_pos)
        self.render()
        
        return observation, reward, terminated, False, info
    def close(self):
        pygame.display.quit()
        pygame.quit()

    def render(self):
        self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.width, self.height))
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.width, self.height))
        canvas.fill("white")
        sub = ((self.player_pos.x+10, self.player_pos.y+10),(self.player_pos.x, self.player_pos.y-20),(self.player_pos.x-10, self.player_pos.y+10))
        sub = [rotate_point(point, (self.player_pos.x, self.player_pos.y),self.heading) for point in sub]
        #print(sub)
        pygame.draw.polygon(canvas, "blue", sub)
        pygame.draw.circle(canvas, "red", self.finish_pos, 10)
        pygame.draw.circle(canvas, "red", self.finish_pos, 40, width=1)
        for obstacle in self.obstacles:
            pygame.draw.circle(canvas, "yellow", obstacle, 5)
            pygame.draw.circle(canvas, "yellow", obstacle, 25, width = 1)

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            
            pygame.display.flip()