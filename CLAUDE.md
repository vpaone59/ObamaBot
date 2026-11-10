# Claude AI Agent Instructions

This file contains shared instructions referenced by copilot-instructions.md to avoid duplication. All AI agents should follow these guidelines.

Architecture and workflows: @.github/copilot-instructions.md

Project skills live in `.claude/skills/`.

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

## Authorship

Never add `Co-Authored-By` trailers, "Generated with" lines, or any other AI attribution to commits, pull requests, or GitHub issues. All work should read as if the repo owner wrote it.

## Commit Message Style: Conventional Commits

Keep commits simple. A one line subject is usually enough, only add a body when the reason for the change isn't obvious.

All commits must follow [Conventional Commits](https://www.conventionalcommits.org/) format:

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

## Code Quality Standards

### Logging

- Always use `logger.*()` methods, never `print()`
- Use lazy formatting: `logger.info("User %s logged in", username)` not `logger.info(f"User {username} logged in")`
- Use `logger.exception()` for exception context, never `logger.error(..., exc_info=True)`
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

- Cogs use **absolute imports** from project root:
  ```python
  from utils.logging_config import create_new_logger
  ```
- Modules in `utils/` package use **relative imports**:
  ```python
  from .logging_config import create_new_logger
  ```

### Type Hints

- Add type hints to all public methods for IDE support and type checking
- Use `from typing import Optional, List` for complex types
- Annotate parameters and return types:
  ```python
  async def hello(self, ctx: commands.Context) -> None:
      """Reply with a greeting."""
      await ctx.send(f"Hello {ctx.author.mention}!")
  ```

## Review Checklist

Before committing:
- [ ] Run `uv run ruff check cogs/ --fix` — no remaining issues
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
