# Gripper (Robotiq 2F85) code
import os
import pybullet
import pybullet_data
import numpy as np
import threading
import copy
import cv2
from moviepy.editor import ImageSequenceClip

# imports for LMPs
import shapely
import ast
import astunparse
from time import sleep
from shapely.geometry import *
from shapely.affinity import *
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

from robots.gym import PickPlaceEnv
from robots.globals import *
from robots.config import setup_LMP, lmp_tabletop_coords, cfg_tabletop

import gradio as gr


def test_func(input):
  return "hello world"

application = gr.Interface(fn=test_func, inputs="text", outputs="text")


application.launch()
num_blocks = 5
num_bowls = 3 
high_resolution = False 
high_frame_rate = False 

# setup env and LMP
env = PickPlaceEnv(render=True, high_res=high_resolution, high_frame_rate=high_frame_rate)
block_list = np.random.choice(ALL_BLOCKS, size=num_blocks, replace=False).tolist()
bowl_list = np.random.choice(ALL_BOWLS, size=num_bowls, replace=False).tolist()
obj_list = block_list + bowl_list
_ = env.reset(obj_list)
lmp_tabletop_ui = setup_LMP(env, cfg_tabletop)


# display env
print('di initial environment...')
cv2.imwrite('test_image.png',cv2.cvtColor(env.get_camera_image(), cv2.COLOR_BGR2RGB))
print('image saved to test_image.png')


print('available objects:')
print(obj_list)



user_input = 'stack the block on the other block' 

env.cache_video = []

print('Running policy and recording video...')
lmp_tabletop_ui(user_input, f'objects = {env.object_list}')

print(len(env.cache_video))
if env.cache_video:
  rendered_clip = ImageSequenceClip(env.cache_video, fps=35 if high_frame_rate else 25)
  rendered_clip.write_videofile('test_video.mp4')