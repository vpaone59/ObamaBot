"""
Fish Game Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

A guessing game where users identify fish from images or guess real vs. fake fish names.
"""

import json
import os
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from utils.logging_config import create_new_logger

logger = create_new_logger(__name__)


# Load fish data
with open("./dynamic/fish_data.json", "r", encoding="utf-8") as file:
    fish_data = json.load(file)

GAME_TYPES = ["image", "name"]
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


@dataclass
class FishGame:
    """Represents the state of a single fish game instance."""

    game_type: str
    correct_answer: str
    correct_fish_name: str
    options: List[str]
    answered_users: set = field(default_factory=set)
    game_stats: dict = field(
        default_factory=lambda: {
            "correct_answers": [],
            "wrong_answers": [],
            "total_participants": 0,
        }
    )


class FishGameView(discord.ui.View):
    """
    View for handling fish game interactions.
    """

    def __init__(self, cog: "Fish", game: FishGame):
        super().__init__(timeout=60.0)
        self.cog = cog
        self.game = game

        if len(self.children) >= 2:
            self.children[0].label = game.options[0]
            self.children[1].label = game.options[1]

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Allow all users to interact, but only once per game."""
        if interaction.user.id in self.game.answered_users:
            await interaction.response.send_message(
                "You've already played in this fish game!", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        """Disables buttons and sends a final summary embed on timeout."""
        for item in self.children:
            item.disabled = True

        logger.info(
            f"Fish game timed out. Correct answer was {self.game.correct_fish_name}"
        )

    @discord.ui.button(label="Option 1", style=discord.ButtonStyle.primary, emoji="🐟")
    async def option_one(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await self.cog._handle_game_answer(interaction, button, self.game)

    @discord.ui.button(label="Option 2", style=discord.ButtonStyle.primary, emoji="🐠")
    async def option_two(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await self.cog._handle_game_answer(interaction, button, self.game)


class Fish(commands.Cog):
    """Fish identification and name guessing games."""

    def __init__(self, bot):
        self.bot = bot
        self.session: Optional[aiohttp.ClientSession] = None
        # expose module-level env values on the cog instance as well
        self.ollama_api_url = OLLAMA_API_URL
        self.ollama_model = OLLAMA_MODEL

    async def cog_load(self):
        """Initialize aiohttp session when cog loads."""
        # If env vars aren't set, do not raise here; setup() will skip loading the cog.
        if not (self.ollama_api_url and self.ollama_model):
            logger.warning(
                "OLLAMA env vars not set; Fish cog loaded without AI features."
            )
            # still create a session for fallback name generation if desired
            self.session = aiohttp.ClientSession()
            logger.info("%s ready (limited)", self.__cog_name__)
            return

        self.session = aiohttp.ClientSession()
        logger.info("%s ready", self.__cog_name__)

    async def cog_unload(self):
        """Close aiohttp session when cog unloads."""
        if self.session:
            await self.session.close()

    @commands.hybrid_group(
        name="fishgame",
        aliases=["fish", "fg"],
        description="Start a fish-related guessing game.",
    )
    @app_commands.describe(
        game_type="Choose a specific game, or leave blank for random."
    )
    async def fishgame(self, ctx: commands.Context, game_type: Optional[str] = None):
        """Starts a fish-related guessing game. Can be image or name based."""
        if game_type:
            choice = game_type.lower()
            if choice not in GAME_TYPES:
                await ctx.send(
                    f"Invalid game type. Choose one of: {', '.join(GAME_TYPES)}.",
                    ephemeral=True,
                )
                return
            game_choice = choice
        else:
            game_choice = random.choice(GAME_TYPES)

        if game_choice == "image":
            await self._start_image_game(ctx)
        elif game_choice == "name":
            await self._start_name_game(ctx)

    async def _start_image_game(self, ctx: commands.Context):
        """Starts the fish identification game (from an image)."""
        logger.info("Fish image game started by user %s", ctx.author)
        try:
            selected_fish = random.choice(fish_data["fish"])
            correct_name = selected_fish["name"]
            image_url = selected_fish["image_url"]
            wrong_answer = await self._generate_fake_fish_name_ai()

            options = [correct_name, wrong_answer]
            random.shuffle(options)

            game = FishGame(
                game_type="image",
                correct_answer=correct_name,
                correct_fish_name=correct_name,
                options=options,
            )

            embed = discord.Embed(
                title="🐟 Fish Identification Game",
                description="What type of fish is this?",
                color=0x1E90FF,
            )
            embed.set_image(url=image_url)
            embed.add_field(
                name="Options", value="\n".join(f"- {o}" for o in options), inline=False
            )
            embed.set_footer(text="You have 60 seconds to answer.")

            view = FishGameView(self, game)
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            logger.error("Error starting image fish game: %s", e, exc_info=True)
            await ctx.send("Sorry, I couldn't start the fish game. Please try again.")

    async def _start_name_game(self, ctx: commands.Context):
        """Starts the real vs. fake fish name guessing game."""
        logger.info("Fish name game started by user %s", ctx.author)
        try:
            real_fish_name = random.choice(fish_data["fish"])["name"]
            fake_fish_name = await self._generate_fake_fish_name_ai()

            options = [real_fish_name, fake_fish_name]
            random.shuffle(options)

            game = FishGame(
                game_type="name",
                correct_answer=real_fish_name,
                correct_fish_name=real_fish_name,
                options=options,
            )

            embed = discord.Embed(
                title="📝 Fish Name Game",
                description="Which of these is a **REAL** fish name?",
                color=0xFF6B35,
            )
            embed.add_field(
                name="Options", value="\n".join(f"- {o}" for o in options), inline=False
            )
            embed.set_footer(text="You have 60 seconds to answer.")

            view = FishGameView(self, game)
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            logger.error("Error starting name fish game: %s", e, exc_info=True)
            await ctx.send(
                "Sorry, I couldn't start the fish name game. Please try again."
            )

    async def _handle_game_answer(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
        game: FishGame,
    ):
        """Handles a user's answer, sends a response, and saves stats."""
        user_id = interaction.user.id
        game.answered_users.add(user_id)
        is_correct = button.label == game.correct_answer

        if is_correct:
            game.game_stats["correct_answers"].append(user_id)
            response = f"🎉 Correct! It was a **{game.correct_fish_name}**!"
        else:
            game.game_stats["wrong_answers"].append(user_id)
            response = f"❌ Wrong! The correct answer is **{game.correct_fish_name}**."

        game.game_stats["total_participants"] += 1
        await self._save_user_stats(
            user_id, interaction.user.display_name, is_correct, game.game_type
        )
        await interaction.response.send_message(response, ephemeral=True)

        logger.info(
            "User %s (%s) answered %s for %s game - fish: %s",
            interaction.user.display_name,
            user_id,
            "correctly" if is_correct else "incorrectly",
            game.game_type,
            game.correct_fish_name,
        )

    async def _save_user_stats(
        self,
        user_id: int,
        username: str,
        is_correct: bool,
        game_type: str,
    ):
        """Save user and global statistics to a JSON file."""
        try:
            with open("./dynamic/fish_stats.json", "r+", encoding="utf-8") as file:
                stats = json.load(file)
        except FileNotFoundError:
            stats = {
                "users": {},
                "global": {
                    "total_games": 0,
                    "total_correct": 0,
                    "total_wrong": 0,
                    "image_games": 0,
                    "name_games": 0,
                    "image_correct": 0,
                    "name_correct": 0,
                },
            }

        user_id_str = str(user_id)
        user_stats = stats["users"].setdefault(
            user_id_str,
            {
                "username": username,
                "games_played": 0,
                "correct_answers": 0,
                "wrong_answers": 0,
                "image_games": 0,
                "name_games": 0,
                "image_correct": 0,
                "name_correct": 0,
                "last_played": None,
            },
        )

        user_stats.update(
            {
                "username": username,
                "games_played": user_stats["games_played"] + 1,
                "last_played": datetime.now().isoformat(),
            }
        )

        game_type_key = f"{game_type}_games"
        game_correct_key = f"{game_type}_correct"

        user_stats[game_type_key] = user_stats.get(game_type_key, 0) + 1
        stats["global"][game_type_key] = stats["global"].get(game_type_key, 0) + 1

        if is_correct:
            user_stats["correct_answers"] += 1
            user_stats[game_correct_key] = user_stats.get(game_correct_key, 0) + 1
            stats["global"]["total_correct"] += 1
            stats["global"][game_correct_key] = (
                stats["global"].get(game_correct_key, 0) + 1
            )
        else:
            user_stats["wrong_answers"] += 1
            stats["global"]["total_wrong"] += 1

        stats["global"]["total_games"] += 1

        with open("./dynamic/fish_stats.json", "w", encoding="utf-8") as file:
            json.dump(stats, file, indent=2)

    @app_commands.command(
        name="fishstats", description="View your fish game statistics."
    )
    async def fish_stats_slash(
        self, interaction: discord.Interaction, user: Optional[discord.User] = None
    ):
        """Slash command to view fish game statistics."""
        target_user = user or interaction.user
        await self._show_fish_stats(
            target_user, lambda **kwargs: interaction.response.send_message(**kwargs)
        )

    @commands.command(name="fishstats", help="View your fish game statistics.")
    async def fish_stats_prefix(
        self, ctx: commands.Context, user: Optional[discord.User] = None
    ):
        """Prefix command to view fish game statistics."""
        target_user = user or ctx.author
        await self._show_fish_stats(target_user, ctx.send)

    async def _show_fish_stats(self, user: discord.User, send_func):
        """Displays a user's fish game statistics in an embed."""
        try:
            with open("./dynamic/fish_stats.json", "r", encoding="utf-8") as file:
                stats = json.load(file)
        except FileNotFoundError:
            await send_func("No fish game statistics found yet. Play a game first!")
            return

        user_id_str = str(user.id)
        if user_id_str not in stats.get("users", {}):
            await send_func(f"{user.display_name} hasn't played any fish games yet.")
            return

        user_stats = stats["users"][user_id_str]
        embed = self._create_stats_embed(user, user_stats, stats["global"])
        await send_func(embed=embed)

    def _create_stats_embed(
        self, user: discord.User, user_stats: dict, global_stats: dict
    ) -> discord.Embed:
        """Helper function to build the stats embed."""
        total_games = user_stats.get("games_played", 0)
        correct = user_stats.get("correct_answers", 0)
        accuracy = (correct / total_games * 100) if total_games > 0 else 0

        embed = discord.Embed(
            title=f"🐟 {user.display_name}'s Fish Game Stats", color=0x1E90FF
        )
        embed.add_field(
            name="📊 Overall Stats",
            value=f"🎮 Total: {total_games}\n✅ Correct: {correct}\n❌ Wrong: {user_stats.get('wrong_answers', 0)}\n🎯 Accuracy: {accuracy:.1f}%",
            inline=True,
        )

        for game_type in ["image", "name"]:
            played = user_stats.get(f"{game_type}_games", 0)
            correct = user_stats.get(f"{game_type}_correct", 0)
            accuracy = (correct / played * 100) if played > 0 else 0
            title = (
                f"🖼️ {game_type.title()} Games"
                if game_type == "image"
                else f"📝 {game_type.title()} Games"
            )
            embed.add_field(
                name=title,
                value=f"🎮 Played: {played}\n✅ Correct: {correct}\n🎯 Accuracy: {accuracy:.1f}%",
                inline=True,
            )

        if user_stats.get("last_played"):
            last_played = datetime.fromisoformat(user_stats["last_played"])
            embed.set_footer(
                text=f"Last played: {last_played.strftime('%Y-%m-%d %H:%M')}"
            )

        return embed

    async def _generate_fake_fish_name_ai(self) -> str:
        """Generate a believable but fictional fish name using Ollama AI."""
        if not self.session:
            self.session = aiohttp.ClientSession()

        # If Ollama env not configured, use fallback immediately
        if not (self.ollama_api_url and self.ollama_model):
            return self._generate_fake_fish_name_fallback()

        real_fish_sample = random.sample(
            [fish["name"] for fish in fish_data["fish"]], min(5, len(fish_data["fish"]))
        )
        prompt = f"Generate one plausible-sounding but completely fictional fish name. Examples of real fish are: {', '.join(real_fish_sample)}. Your response should only be the name itself and nothing else."

        try:
            async with self.session.post(
                f"{self.ollama_api_url}/api/generate",
                json={"model": self.ollama_model, "prompt": prompt, "stream": False},
                timeout=10,
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    fake_name = result.get("response", "").strip().replace('"', "")
                    if fake_name:
                        return fake_name
        except Exception as e:
            logger.error(f"AI fish name generation failed: {e}")

        return self._generate_fake_fish_name_fallback()

    def _generate_fake_fish_name_fallback(self) -> str:
        """Fallback for generating a fake fish name."""
        prefixes = ["Golden", "Azure", "Crimson", "Glimmerfin", "Shadowscale"]
        suffixes = ["Darter", "Grouper", "Snapper", "Whiskerfish", "Tide-runner"]
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"


async def setup(bot):
    """Adds the cog to the bot only if required env vars are present"""
    if not (OLLAMA_API_URL and OLLAMA_MODEL):
        logger.error(
            "Required environment variables for Fish cog not found: OLLAMA_API_URL and/or OLLAMA_MODEL. Skipping Fish cog load."
        )
        return

    await bot.add_cog(Fish(bot))
