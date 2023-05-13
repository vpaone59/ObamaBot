"""
Camcap Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This Cog is custom made for a specific server and will not work in normal servers.
"""

import time
import random
import discord
from discord.ext import commands
import cv2


class Camcap(commands.Cog):
    """
    camera capture commands that uses webcams to take pictures,
    record videos, etc
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f'{self} ready')

    @commands.command(aliases=['catcap', 'catpic', 'catsnap', 'cat'])
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def cat_cap(self, ctx, cam_num=-1):
        """
        takes a quick picture from the webcam and saves the file
        then sends it to the discord channel
        """
        bot_warn = await ctx.send("```loading image...pls do not spam command :D```")
        # camera 2 is being reserved for an outside camera
        camera_number = [1, 3]
        frame_counter = 0
        if cam_num > 3 or cam_num == 0 or cam_num < -1 or cam_num == 2:
            await ctx.send(f'INDEX ERROR: Cameras available #s 1 or 3. Use -1 or leave empty for random.')
            return
        elif cam_num == -1:
            cam_num = random.choice(camera_number)
            cam = cv2.VideoCapture(cam_num-1)
        else:
            cam = cv2.VideoCapture(cam_num-1)

        cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
        img_name = f"gifs/catcam/cat_cap_{frame_counter}.jpg"
        cv2.imwrite(img_name, frame)

        cam.release()
        await bot_warn.delete()
        await ctx.send(f'```Image from Camera #{cam_num}```', file=discord.File('gifs/catcam/cat_cap_0.jpg'))

    @commands.command(aliases=['catrec', 'catvid'])
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def cat_rec(self, ctx):
        """
        records a 5 second video through webcam and saves the file
        then sends the file to the discord channel 
        """
        rec = cv2.VideoCapture(1)

        fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
        video_output = cv2.VideoWriter(
            'gifs/catcam/cat_rec.avi', fourcc, 1.0, (640, 480))

        start_time = time.time()
        while (time.time() - start_time) < 3.0:
            ret, frame = rec.read()
            if ret:
                video_output.write(frame)
            else:
                break

        rec.release()
        video_output.release()

        await ctx.send(file=discord.File('gifs/catcam/cat_rec.avi'))


async def setup(bot):
    await bot.add_cog(Camcap(bot))
