from Environment import *
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import PPO, A2C
from stable_baselines3.common.evaluation import evaluate_policy
import os
env = CustomEnv()
model_path = os.path.join("Models", "v3Model_A2C")
model = A2C.load(model_path)

for i in range(100):
    obs, info = env.reset()  # Reset the environment
    done = False
    print("run:", i)
    while not done:
        action, _ = model.predict(obs)
        obs, reward, done, unknown, info = env.step(action)
        env.render()  # Render the environment if needed

env.close()  # Close the environment when done