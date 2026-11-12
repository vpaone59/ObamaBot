# ObamaBot - AI Coding Agent Instructions

> **Note:** This is the single source of instructions for every AI agent working on this repo. [CLAUDE.md](../CLAUDE.md) only points here so nothing is duplicated.

## Branches

- **Never commit or push to `main` from local.** All work goes on a branch that gets merged to `main` through a pull request
- Pull the latest `main` and branch from it before starting work
- Name branches by the type of work: `feature/...`, `bugfix/...`, `docs/...`, `refactor/...`, `maintenance/...`
- If a branch depends on another unmerged branch, branch from that one and say which should be merged first
- Pull requests are opened and merged by the repo owner

## Commits and Authorship

- **No co-authors.** Never add `Co-Authored-By` trailers, "Generated with" lines, or any other AI attribution to commits, pull requests, or GitHub issues. All work should read as if the repo owner wrote it
- Keep commits simple. A one line subject is usually enough, only add a body when the reason for the change isn't obvious
- All commits follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that don't affect code meaning (formatting, missing semicolons, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Code change that improves performance
- **test**: Adding tests or updating test logic
- **ci**: Changes to CI/CD configuration
- **chore**: Changes to build process, dependencies, or tooling

### Examples

```
feat(friends): add frank feature for Danny DeVito GIFs
fix(logging): replace logger.error with logger.exception per standard
docs(README): update uv installation instructions
refactor(general): improve exception handling in hello command
ci: add GitHub Actions workflow for Docker Hub CI/CD
```

### Scope (Optional)

Use the affected cog name or module:
- `friends`, `game`, `fish_game`, `general`, etc.
- `logging`, `db`, `utils` for infrastructure
- Leave blank for project-wide changes

### Body (Optional)

Use imperative mood ("add" not "adds"), and explain:
- WHY the change was made
- WHAT problem it solves
- Any breaking changes (prefix with `BREAKING CHANGE:`)

Example:
```
fix(prompt_loader): replace bare Exception with specific error types

Previously caught all exceptions generically, making debugging harder.
Now catches httpx.RequestError and discord.AppCommandError specifically,
improving logging and error handling precision.
```

### Footer (Optional)

Reference issues:
```
Closes #42
Fixes #123, #456
Related-to: #789
```

## Engineering Standards

Hold this project to the same bar as a well run Django project, written in strong, idiomatic Python.

- Take the clear solution. Avoid complex workarounds when a straightforward fix exists
- Explicit is better than implicit. Prefer readable code over clever code
- Keep commands thin. Business logic and database access belong in helpers in `utils/`
- Don't repeat yourself. Reuse an existing helper before writing a new one
- Secure by default: check permissions on every admin command, and never log or commit secrets
- Configuration comes from environment variables. Document new ones in `.env-example`
- Schema changes go in `database/init_create.sql` and must be safe to run on an existing database
- Fix the cause of a bug, not the symptom

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

### Logging

- All modules use centralized logger: `from utils.logging_config import create_new_logger`
- Logs output to `./logs/bot.log` in JSON format with EST timezone
- Always use `logger.*()` methods, never `print()`
- Use lazy formatting: `logger.info("User %s logged in", username)` not `logger.info(f"User {username} logged in")`
- Use `logger.exception()` for exception context, never `logger.error(..., exc_info=True)`
- Never log a URL or exception text that contains an API key or token
- Choose appropriate level:
  - `debug`: Detailed info for development/debugging
  - `info`: General informational messages (command usage, startup)
  - `warning`: Something went wrong but bot continues
  - `error`: Error occurred; operation may have failed
  - `exception`: Exception caught; use in except blocks

### Exception Handling

- Never use bare `except Exception:` — catch specific exception types
- Discord operations: catch `discord.DiscordException` or specific subclasses
- HTTP operations: catch `httpx.RequestError`, `httpx.HTTPStatusError`
- Let unexpected exceptions propagate for logging/debugging

### Async/Await

- All Discord interactions are async — use `await` for:
  - Message sends: `await ctx.send()`, `await interaction.response.send_message()`
  - Cog operations: `await bot.add_cog()`, `await bot.load_extension()`
  - Blocking I/O: wrap in `asyncio.to_thread()` or `loop.run_in_executor()`
- Never block the event loop with `time.sleep()` — use `await asyncio.sleep()`

### Imports

Cog files use absolute imports rooted at the project directory (the project root is on `sys.path`, cogs are not a package):
```python
from utils.logging_config import create_new_logger
```

Root-level scripts like `main.py` use the same absolute import style.

Modules inside `utils/` (e.g. `db_helper.py`) use relative imports since `utils` is a package:
```python
from .logging_config import create_new_logger
```

### Type Hints

- Add type hints to all public methods for IDE support and type checking
- Use built in generics and `|` for unions: `list[str]`, `dict[str, int]`, `str | None`
- Annotate parameters and return types:
  ```python
  async def hello(self, ctx: commands.Context) -> None:
      """Reply with a greeting."""
      await ctx.send(f"Hello {ctx.author.mention}!")
  ```

### Permissions

- Prefix admin commands use `@commands.has_permissions(administrator=True)`
- Slash admin commands use `@app_commands.checks.has_permissions(administrator=True)`. `commands.has_permissions` does nothing on slash commands

### Environment Variables & Configuration

Required vars in `.env` (copy from `.env-example`):
- `DISCORD_TOKEN`: Bot token from Discord Developer Portal
- `PREFIX`: Command prefix (e.g., `!`)
- `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`: PostgreSQL connection

Optional vars (check cog docstrings and `.env-example` for specifics):
- `OLLAMA_API_URL`, `OLLAMA_MODEL`: For the AI chat cog
- `GOOGLE_MAPS_API_KEY`: For location-based features
- `GENIUS_API_KEY`: For lyrics features
- `REDDIT_*`: For Reddit integration
- `GIPHY_KEY`, `KLIPY_KEY`: For GIF searches
- `HOST_LOG_PATH`: Docker volume mapping for logs
- `COMPOSE_PROFILES`: Set to `local-db` to run PostgreSQL in Docker with the bot

### Database Pattern

PostgreSQL through a connection pool in `utils/db_helper.py`. Use the connection as a context manager so the transaction commits or rolls back, and always return it to the pool:
```python
from utils.db_helper import get_database_connection, return_database_connection

conn = get_database_connection()
try:
    with conn, conn.cursor() as cursor:
        cursor.execute("SELECT * FROM table_name")
        rows = cursor.fetchall()
finally:
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

### Message Filtering

In `on_message` listeners, always check:
- `if message.author == bot.user or message.author.bot: return` (in main.py)
- `if string.startswith(PREFIX): return` (to skip command prefixes in listeners)

## Review Checklist

Before committing:
- [ ] Working on a branch, not `main`
- [ ] Run `uv run ruff check cogs/ --fix` — no new issues
- [ ] Run `uv run ruff format cogs/` — code is formatted consistently
- [ ] Commit message follows Conventional Commits format
- [ ] No co-authors or AI attribution anywhere in the commit, PR, or issue
- [ ] Admin commands have a permission check (`app_commands.checks` for slash commands)
- [ ] No API keys or tokens in log messages
- [ ] No bare `except Exception:` clauses
- [ ] No `logger.error(..., exc_info=True)` — use `logger.exception()` instead
- [ ] Type hints added to new/modified methods
- [ ] Logging uses lazy formatting
- [ ] All async operations use `await`

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
- `CLAUDE.md`, `.claude/skills/`: Claude Code entry point and project skills

## Deprecated Code

Deprecated cogs are marked with `⚠️ DEPRECATED` in docstrings and moved to `cogs/deprecated/`. New features should never reference them.

---

**Last Updated:** November 2026
**Python Version:** 3.11+
