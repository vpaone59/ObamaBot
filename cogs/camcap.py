import discord
from discord.ext import commands

import random
import cv2
from cv2 import *
import numpy as np
import matplotlib.pyplot as plt

class Camcap(commands.Cog):
    """
    counter Cog for ObamaBot
    keeps a running tally of certain things.
    """

    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} ready')

    @commands.command(aliases=['catcap','catpic','catsnap', 'cat'])
    async def cat_cap(self, ctx):
        frame_counter = 0
        cam = cv2.VideoCapture(0)
        
        cv2.namedWindow("Cat Cap")
        ret, frame = cam.read()
        
        if not ret:
            print("failed to grab frame")
        cv2.imshow("Cat Cap", frame)
        
        img_name = "gifs/cat_cap_{}.jpg".format(frame_counter)
        cv2.imwrite(img_name, frame)
        
        # print("{} written!".format(img_name))

        cam.release()
        cv2.destroyAllWindows()

        await ctx.send(file=discord.File('gifs/cat_cap_0.jpg'))

async def setup(client):
    await client.add_cog(Camcap(client))