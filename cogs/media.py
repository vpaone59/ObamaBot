"""
Media Cog for ObamaBot by Vincent Paone https://github.com/vpaone59
"""

import os
import discord
import random
from PIL import Image, ImageDraw
from discord.ext import commands
import colorgram

ball_phrases = ['Did someone say...ball?',
                'Status: Balling.', ':rotating_light: Baller alert :rotating_light:']

obama_pics = os.listdir(os.getcwd() + '/gifs/obama')
obama_dir = 'gifs/obama/'


class Media(commands.Cog):
    """
    Media cogs/commands for Obama Bot
    These commands will send media to the Guild the command was run in
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f'{self} ready')

    @commands.Cog.listener("on_message")
    async def obama_msg(self, message):
        # listens for an on_message hit and then runs the following
        if message.author == self.bot.user or message.author.bot:
            return

    @commands.command(aliases=['wed'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wednesday(self, ctx):
        """
        Reply with media
        """
        await ctx.send(file=discord.File('gifs/memes/wednesday.jpg'))

    @commands.command(aliases=['c'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cry(self, ctx):
        """
        Reply with media
        """
        await ctx.send(file=discord.File('gifs/obama/obama-cry.gif'))

    @commands.command(aliases=['md'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def micdrop(self, ctx):
        """
        Reply with media
        """
        await ctx.send(file=discord.File('gifs/obama/obama-micdrop.gif'))

    @commands.command(aliases=['mb'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def micbomb(self, ctx):
        """
        Reply with media
        """
        await ctx.send(file=discord.File('gifs/obama/obama-micbomb.gif'))

    @commands.command(aliases=['gm'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def goodmorning(self, ctx):
        """
        Reply with media
        """
        await ctx.send(f'Goodmorning my fellow Americans!', file=discord.File('gifs/obama/obama-smile.jpg'))

    @commands.command(aliases=['gn'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def goodnight(self, ctx):
        """
        Reply with media
        """
        await ctx.send(f'Goodnight and God Bless!', file=discord.File('gifs/obama/obama-sleep.jpeg'))

    @commands.command(aliases=['balls'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ball(self, ctx):
        """
        Reply with media
        """
        await ctx.channel.send(random.choice(ball_phrases), file=discord.File('gifs/obama/obama-basketball.jpg'))

    @commands.command(aliases=['monkey', 'm'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def monkey_falling(self, ctx):
        """
        Reply with media
        """
        await ctx.send(file=discord.File('gifs/memes/monkey-fall.gif'))

    @commands.command(aliases=['poggers'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pog(self, ctx):
        """
        Reply with media
        """
        await ctx.channel.send("<:obamapog:1040355321102749819>")

    @commands.command(aliases=['thanks'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def thanks_obama(self, ctx):
        """
        Reply with media
        """
        await ctx.channel.send(f'You\'re welcome! <:obamacare:844291609663111208>\n', file=discord.File('gifs/obama/obama-smile.jpg'))

    @commands.command(aliases=['obunga'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def obamna(self, ctx):
        """
        Reply with media
        """
        await ctx.channel.send("<:obamacare:844291609663111208>")

    @commands.command(aliases=['coord'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def coordinate(self, ctx):
        """
        Reply with media
        """
        await ctx.channel.send(":BatChest: :point_up:")

    @commands.command(aliases=['o'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def obama(self, ctx):
        """
        Reply with media
        """
        await ctx.channel.send(file=discord.File('gifs/obama/obama-wave.jpg'))

    @commands.command(aliases=['idk'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def i_dont_know(self, ctx):
        """
        Reply with media
        """
        await ctx.channel.send("<:obamathink:842635667779616798>")

    @commands.command(aliases=['who', 'whoasked'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def who_asked(self, ctx):
        """
        Reply with media
        """
        await ctx.channel.send(file=discord.File('gifs/obama/biden-looking.jpg'))

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lip_bite(self, ctx):
        """
        Reply with media
        """
        await ctx.channel.send(file=discord.File('gifs/obama/obama-lip_bite.jpg'))

    @commands.command(aliases=['smoile'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wink(self, ctx):
        """
        Reply with media
        """
        await ctx.channel.send(file=discord.File('gifs/obama/obama-wink.gif'))

    @commands.command(aliases=['pixel'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pixel_image(self, ctx, pixel_count=16):
        """
        Pick a random file, select RGB pixels, redraw the file using only those pixels
        """
        rgb_colors = []
        non_gif_files = [f for f in obama_pics if not f.endswith(
            '.gif') or f == 'pixel_obama.png']
        file = random.choice(non_gif_files)

        try:
            # extract 24 RGB colors from the image
            # this might fail if there is something wrong with the file (wrong file type, etc)
            colors = colorgram.extract(
                os.path.join(obama_dir, file), pixel_count)
            print(colors)
        except Exception as e:
            print(e)

        for color in colors:
            r = color.rgb.r
            g = color.rgb.g
            b = color.rgb.b
            new_color = (r, g, b)
            rgb_colors.append(new_color)
            print(color.proportion)  # get % of each pixel in the image

        # Determine the number of squares to be displayed per row and column
        num_squares = len(rgb_colors)
        num_per_row = int(num_squares ** 0.5)
        # Calculate the number of rows the image will have, based on whether or not its a square
        num_rows = num_per_row if num_per_row ** 2 == num_squares else num_per_row + 1

        # Determine the size of each square
        square_size = 50
        total_width = num_per_row * square_size
        total_height = num_rows * square_size

        # Create the image and draw each square
        image = Image.new('RGB', (total_width, total_height))
        draw = ImageDraw.Draw(image)

        # Draw the image, 1 color block at a time
        for i, color in enumerate(rgb_colors):
            row = i // num_per_row
            col = i % num_per_row
            x = col * square_size
            y = row * square_size
            draw.rectangle(
                [(x, y), (x+square_size, y+square_size)], fill=color)

        # Save the image to a file
        image.save('gifs/obama/pixel_obama.png')

        # adjust the number of pixels printed out
        # if user input 50 and image could only do 36, it will say 36 pixels
        pixel_count = num_squares
        await ctx.send(f'```{file}, in {pixel_count} pixels!```', file=discord.File('gifs/obama/pixel_obama.png'))


async def setup(bot):
    await bot.add_cog(Media(bot))
