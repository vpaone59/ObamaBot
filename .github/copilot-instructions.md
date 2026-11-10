# ObamaBot - AI Coding Agent Instructions

> **Note:** This file references [CLAUDE.md](../CLAUDE.md) for shared guidelines on commit styling, logging, exception handling, and code quality. See that file for details.

## Commits and Authorship

- All commits follow [Conventional Commits](https://www.conventionalcommits.org/), e.g. `fix(roles): require admin to delete roles`. See [CLAUDE.md](../CLAUDE.md#commit-message-style-conventional-commits)
- Keep commit messages simple. A one line subject is usually enough
- **No co-authors.** Never add `Co-Authored-By` trailers, "Generated with" lines, or any other AI attribution to commits, pull requests, or GitHub issues

## Engineering Standards

Hold this project to the same bar as a well run Django project, written in strong, idiomatic Python. Take the clear solution and avoid complex workarounds when a straightforward fix exists. See [CLAUDE.md](../CLAUDE.md#engineering-standards).

## Project Overview

ObamaBot is a Discord.py bot with a modular Cog-based architecture. It's a general-purpose entertainment bot with features ranging from games to API integrations (Google Maps, Genius lyrics, Reddit, Giphy, etc.).

**Key Tech Stack:** Python 3.11+, discord.py 2.6.4, PostgreSQL, Docker

## Architecture & Key Patterns

### Cog System (Discord.py Modular Architecture)

All bot features live in `cogs/` as individual Cog classes. Each cog file:
- Extends `commands.Cog`
- Has a `setup(bot)` async function that calls `await bot.add_cog(CogClass(bot))`
- Implements event listeners and command groups

**Example structure:**
```python
from utils.logging_config import create_new_logger

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

See [claude.md](../CLAUDE.md#logging) for logging guidelines. Key points:
- All modules use centralized logger: `from utils.logging_config import create_new_logger`
- Logs output to `./logs/bot.log` in JSON format with EST timezone
- Use **lazy formatting**: `logger.info("User %s logged in", user)` not `logger.info(f"User {user} logged in")`
- Use `logger.exception()` in except blocks, never `logger.error(..., exc_info=True)`

### Import Conventions

Cog files use absolute imports rooted at the project directory (the project root is on `sys.path`, cogs are not a package):
```python
from utils.logging_config import create_new_logger
```

Root-level scripts like `main.py` use the same absolute import style:
```python
from utils.logging_config import create_new_logger
```

Modules inside `utils/` (e.g. `db_helper.py`) use relative imports since `utils` is a package:
```python
from .logging_config import create_new_logger
```



### Environment Variables & Configuration

Required vars in `.env` (copy from `.env-example`):
- `DISCORD_TOKEN`: Bot token from Discord Developer Portal
- `PREFIX`: Command prefix (e.g., `!`)
- `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`: PostgreSQL connection

Optional vars (check cog docstrings for specifics):
- `OLLAMA_API_URL`, `OLLAMA_MODEL`: For Fish game cog
- `GOOGLE_MAPS_API_KEY`: For location-based features
- `GENIUS_ACCESS_TOKEN`: For lyrics features
- `REDDIT_*`: For Reddit integration
- `GIPHY_API_KEY`: For GIF generation
- `HOST_LOG_PATH`: Docker volume mapping for logs
- `COMPOSE_PROFILES`: Set to `local-db` to run PostgreSQL in Docker with the bot

### Database Pattern

PostgreSQL through a connection pool in `utils/db_helper.py`:
```python
from utils.db_helper import get_database_connection, return_database_connection

conn = get_database_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM table_name")
cursor.close()
return_database_connection(conn)
```

The schema is in `database/init_create.sql` and runs at startup through `initialize_database()`.

### Data Files

Dynamic data stored in `./dynamic/`:
- `fish_data.json`: Fish game species and images
- `fish_stats.json`: Game statistics
- `smite_gods.json`: Smite character data

Load with: `with open("./dynamic/fish_data.json", "r") as file: data = json.load(file)`

## Critical Developer Workflows

### Local Development
```bash
cp .env-example .env
# Edit .env with your DISCORD_TOKEN, PREFIX and DATABASE_* values
uv sync
uv run python main.py
```
View logs: `./logs/bot.log`

### Docker Workflow
Set `HOST_LOG_PATH` and `DATABASE_PASSWORD` in `.env`, then:
```bash
docker compose up --build -d
```

### Loading/Unloading Cogs at Runtime
Use admin commands:
- `!cog load cog_name` - Load a specific cog
- `!cog unload cog_name` - Unload a specific cog
- `!cog reload cog_name` - Reload a specific cog (or `!cog reload` for all)

### Adding a New Cog
1. Create `cogs/my_feature.py` with a Cog class
2. Implement `setup(bot)` that calls `await bot.add_cog(MyFeature(bot))`
3. Restart bot or use `!cog load my_feature` command
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

### Message Filtering & Exception Handling

In `on_message` listeners, always check:
- `if message.author == bot.user or message.author.bot: return` (in main.py)
- `if string.startswith(PREFIX): return` (to skip command prefixes in listeners)

For exception handling, see [claude.md](../CLAUDE.md#exception-handling):
- Never use bare `except Exception:`
- Catch specific exception types (discord.DiscordException, httpx.RequestError, etc.)
- Use `logger.exception()` not `logger.error(..., exc_info=True)`

### Async/Await Discipline

See [claude.md](../CLAUDE.md#asyncawait) for async best practices. Key points:
- All Discord interactions are async — use `await` for:
  - Message sends: `await ctx.send()`, `await interaction.response.send_message()`
  - Cog operations: `await bot.add_cog()`, `await bot.load_extension()`
  - Blocking I/O: wrap in `asyncio.to_thread()` or `loop.run_in_executor()`
- Never block the event loop with `time.sleep()` — use `await asyncio.sleep()`

## Code Quality Standards

See [claude.md](../CLAUDE.md#code-quality-standards) for detailed standards on:
- **Type Hints**: Add to all public methods for IDE support
- **Imports**: Absolute imports in cogs, relative imports in utils package
- **Review Checklist**: Pre-commit quality verification

## File Organization Reference

- `main.py`: Bot initialization, cog loader, global event handlers
- `utils/logging_config.py`: JSON logging setup with EST timezone
- `utils/db_helper.py`: PostgreSQL connection pool and initialization helpers
- `cogs/`: Modular feature Cogs (auto-loaded)
- `dynamic/`: JSON data files (fish data, stats, etc.)
- `database/`: PostgreSQL schema
- `logs/`: Bot logs (created on first run)
- `docker-compose.yml`: Bot and optional PostgreSQL services
- `.env`: Environment variables (must match `.env-example` structure)
- `CLAUDE.md`, `.claude/skills/`: Claude Code instructions and project skills

## Deprecated Code

Deprecated cogs are marked with `⚠️ DEPRECATED` in docstrings and moved to `cogs/deprecated/`. New features should never reference them.

---

**Last Updated:** November 2026
**Python Version:** 3.11+
