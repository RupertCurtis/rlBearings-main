from Environment3 import *
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import PPO, A2C
from stable_baselines3.common.evaluation import evaluate_policy
import os
import time

results = []
# from env2 import CustomEnv
env = CustomEnv()
pygame.init()
check_env(env)
start = time.time()
model = A2C("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000000)
#print(results)
end = time.time()-start
print(end)
save_path = os.path.join("Models", "test_A2C")
model.save(save_path)
model = A2C.load(save_path, env)
print("testing model")
result = evaluate_policy(model, env, n_eval_episodes=1, render=True)
print(result)