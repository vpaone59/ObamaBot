import discord
from discord.ext import commands
import time
import cv2


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

    @commands.command(aliases=['catcap', 'catpic', 'catsnap', 'cat'])
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def cat_cap(self, ctx):
        """
        takes a quick picture from the webcam and saves the file
        then sends it to the discord channel
        """
        frame_counter = 0
        cam = cv2.VideoCapture(-1)

        cv2.namedWindow("Cat Cap")
        ret, frame = cam.read()

        if not ret:
            print("failed to grab frame")
        cv2.imshow("Cat Cap", frame)

        img_name = "gifs/catcam/cat_cap_{}.jpg".format(frame_counter)
        cv2.imwrite(img_name, frame)
        # print("{} written!".format(img_name))

        cam.release()
        cv2.destroyAllWindows()

        await ctx.send(file=discord.File('gifs/catcam/cat_cap_0.jpg'))

    @commands.command(aliases=['catrec', 'catvid'])
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def cat_rec(self, ctx):
        """
        records a 5 second video through webcam and saves the file
        then sends the file to the discord channel
        """
        rec = cv2.VideoCapture(0)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_output = cv2.VideoWriter(
            'gifs/catcam/cat_rec.mp4', fourcc, 20.0, (640, 480))

        start_time = time.time()
        while (time.time() - start_time) < 5.0:
            ret, frame = rec.read()
            if ret:
                video_output.write(frame)
            else:
                break

        rec.release()
        video_output.release()

        await ctx.send(file=discord.File('gifs/catcam/cat_rec.mp4'))


async def setup(client):
    await client.add_cog(Camcap(client))
