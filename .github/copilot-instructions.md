# ObamaBot - AI Coding Agent Instructions

## Project Overview

ObamaBot is a Discord.py bot with a modular Cog-based architecture. It's a general-purpose entertainment bot with features ranging from games to API integrations (Google Maps, Genius lyrics, Reddit, Giphy, etc.).

**Key Tech Stack:** Python 3.11+, discord.py 2.6.4, SQLite, Docker

## Architecture & Key Patterns

### Cog System (Discord.py Modular Architecture)

All bot features live in `cogs/` as individual Cog classes. Each cog file:
- Extends `commands.Cog`
- Has a `setup(bot)` async function that calls `await bot.add_cog(CogClass(bot))`
- Implements event listeners and command groups

**Example structure:**
```python
from logging_config import create_new_logger

logger = create_new_logger(__name__)

class Friends(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("%s ready", self.__cog_name__)

async def setup(bot):
    await bot.add_cog(Friends(bot))
```

**Important:** Each cog's `setup()` function must call `bot.add_cog()` exactly once. Multiple calls or missing calls cause "already loaded" errors.

### Logging Pattern

All modules use the centralized logger:
```python
from logging_config import create_new_logger
logger = create_new_logger(__name__)
```

Logs output to `./logs/bot.log` in JSON format with EST timezone. No print statements—always use `logger.*()`.

### Import Conventions (CRITICAL)

**After creating `cogs/__init__.py`**, use relative imports in cog files:
```python
from ..logging_config import create_new_logger  # From root level
```

Do NOT use `from .logging_config` (that tries to import from cogs directory).

Root-level scripts like `main.py` and `db_helper.py` use absolute imports:
```python
from logging_config import create_new_logger
```

### Environment Variables & Configuration

Required vars in `.env` (copy from `SAMPLE.env`):
- `DISCORD_TOKEN`: Bot token from Discord Developer Portal
- `PREFIX`: Command prefix (e.g., `!`)

Optional vars (check cog docstrings for specifics):
- `OLLAMA_API_URL`, `OLLAMA_MODEL`: For Fish game cog
- `GOOGLE_MAPS_API_KEY`: For location-based features
- `GENIUS_ACCESS_TOKEN`: For lyrics features
- `REDDIT_*`: For Reddit integration
- `GIPHY_API_KEY`: For GIF generation
- `HOST_LOG_PATH`, `HOST_DB_PATH`: Docker volume mappings

### Database Pattern

SQLite database at `./database/bot.db`. Use `db_helper.py`:
```python
from db_helper import get_database_connection, initialize_database

conn = get_database_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM table_name")
```

Initialize via: `initialize_database()` (called in startup if needed).

### Data Files

Dynamic data stored in `./dynamic/`:
- `fish_data.json`: Fish game species and images
- `fish_stats.json`: Game statistics
- `smite_gods.json`: Smite character data

Load with: `with open("./dynamic/fish_data.json", "r") as file: data = json.load(file)`

## Critical Developer Workflows

### Local Development
```bash
cp SAMPLE.env .env
# Edit .env with your DISCORD_TOKEN and PREFIX
pip install -r requirements.txt
python main.py
```
View logs: `./logs/bot.log`

### Docker Workflow
Edit `docker-compose.yml` to map `HOST_LOG_PATH` and `HOST_DB_PATH` to your machine, then:
```bash
docker compose up --build -d
```

### Loading/Unloading Cogs at Runtime
Use admin commands:
- `!load cog_name` - Load a specific cog
- `!unload cog_name` - Unload a specific cog
- `!reload cog_name` - Reload a specific cog

### Adding a New Cog
1. Create `cogs/my_feature.py` with a Cog class
2. Implement `setup(bot)` that calls `await bot.add_cog(MyFeature(bot))`
3. Restart bot or use `!load my_feature` command
4. Cogs are auto-discovered by `load_all_cogs()` in `main.py`

## Common Gotchas & Patterns

### Handling Optional API Keys
If a cog requires optional environment variables, skip loading it gracefully:
```python
async def setup(bot):
    if not all([API_KEY_1, API_KEY_2]):
        logger.error("Required API keys not set. Cog not loaded.")
        return
    await bot.add_cog(MyCog(bot))
```

### Message Filtering
In `on_message` listeners, always check:
- `if message.author == bot.user or message.author.bot: return` (in main.py)
- `if string.startswith(PREFIX): return` (to skip command prefixes in listeners)

### Async/Await Discipline
All Discord interactions are async. Use `await` for:
- `ctx.send()`, `ctx.reply()`
- `bot.load_extension()`, `bot.add_cog()`
- API calls (requests, aiohttp)

## File Organization Reference

- `main.py`: Bot initialization, cog loader, global event handlers
- `logging_config.py`: JSON logging setup with EST timezone
- `db_helper.py`: SQLite connection and initialization helpers
- `cogs/`: Modular feature Cogs (auto-loaded)
- `dynamic/`: JSON data files (fish data, stats, etc.)
- `database/`: SQLite database file
- `logs/`: Bot logs (created on first run)
- `docker-compose.yml`: Docker volume and environment mappings
- `.env`: Environment variables (must match SAMPLE.env structure)

## Deprecated Code

Deprecated cogs are marked with `⚠️ DEPRECATED` in docstrings and moved to `cogs/deprecated/`. New features should never reference them.

---

**Last Updated:** February 2026
**Python Version:** 3.11+
