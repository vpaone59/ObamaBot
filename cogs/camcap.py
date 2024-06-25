"""
Camcap Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This Cog is custom made for a specific server and will not work in normal servers.
"""

import time
import random
import discord
from discord.ext import commands
import cv2
import os
from logging_config import create_new_logger

logger = create_new_logger()
# number of cameras active and an index to identify each
active_cam_nums = [1, 2, 3]


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
        Runs when the cog is loaded
        """
        print(f"{self} ready")

    @commands.command(aliases=["catcap", "catpic", "catsnap", "cat"])
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def cat_cap(self, ctx, cam_num=-1):
        """
        takes a quick picture from the webcam and saves the file
        then sends it to the discord channel
        """
        bot_warn = await ctx.send("```loading image...pls do not spam command :D```")

        frame_counter = 0
        if cam_num > 3 or cam_num == 0 or cam_num < -1:
            await ctx.send(
                "INDEX ERROR: Cameras available #s 1 2 3. Use -1 or leave empty for random."
            )
            return
        elif cam_num == -1:
            cam_num = random.choice(active_cam_nums)
            cam = cv2.VideoCapture(cam_num - 1)
        else:
            cam = cv2.VideoCapture(cam_num - 1)

        cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
        img_name = f"gifs/catcam/catcap/cat_cap_{frame_counter}.jpg"
        while os.path.exists(img_name):
            frame_counter += 1
            img_name = f"gifs/catcam/catcap/cat_cap_{frame_counter}.jpg"
        cv2.imwrite(img_name, frame)
        cam.release()

        # Check to see if the cat is in the image taken and assign the return status to a variable
        cat_status = check_for_cat(img_name)
        # delete the warning message
        await bot_warn.delete()

        if cat_status == "CAT DETECTED":
            await ctx.send(
                f"```{cat_status} Image from Camera #{cam_num}```",
                file=discord.File(f"gifs/catcam/catcap/cat_cap_{frame_counter}.jpg"),
            )
        elif cat_status == "NO CAT DETECTED":
            os.remove(img_name)
            cat_dir = "gifs/catcam/FRITA/"
            cat_files = os.listdir(cat_dir)
            random_cat_pic = random.choice(cat_files)
            random_cat_path = os.path.join(cat_dir, random_cat_pic)
            try:
                await ctx.send(
                    f"```{cat_status} :( enjoy a complimentary random cat pic```",
                    file=discord.File(random_cat_path),
                )
            except Exception as e:
                print(e)
                await ctx.send(f"```ERROR {e}```")

    @commands.command(aliases=["catrec", "catvid"])
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def cat_rec(self, ctx):
        """
        records a 5 second video through webcam and saves the file
        then sends the file to the discord channel
        """
        rec = cv2.VideoCapture(1)

        fourcc = cv2.VideoWriter_fourcc("X", "V", "I", "D")
        video_output = cv2.VideoWriter(
            "gifs/catcam/catcap/cat_rec.avi", fourcc, 1.0, (640, 480)
        )

        start_time = time.time()
        while (time.time() - start_time) < 3.0:
            ret, frame = rec.read()
            if ret:
                video_output.write(frame)
            else:
                break

        rec.release()
        video_output.release()

        await ctx.send(file=discord.File("gifs/catcam/catcap/cat_rec.avi"))


def check_for_cat(image):
    """
    Check for black pixels in the center of the image
    """

    try:
        img = cv2.imread(image)
        height, width, _ = img.shape
        center_x = width // 2
        center_y = height // 2
        b, g, r = img[center_y, center_x]

        if r == 0 and g == 0 and b == 0:
            return "CAT DETECTED"
        else:
            return "NO CAT DETECTED"

    except Exception as e:
        return f"ERROR {e}"


async def setup(bot):
    await bot.add_cog(Camcap(bot))
