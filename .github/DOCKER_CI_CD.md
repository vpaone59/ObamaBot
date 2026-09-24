# Docker Hub CI/CD Setup

This document describes how the automatic Docker Hub builds are configured via GitHub Actions.

## What It Does

When you push to the `main` branch, GitHub automatically:
1. Builds a Docker image using the Dockerfile
2. Pushes it to Docker Hub with two tags:
   - `<your-username>/obamabot:latest` (always points to the newest build)
   - `<your-username>/obamabot:<commit-sha>` (specific commit version for rollbacks)
3. Uses Docker BuildKit caching to speed up subsequent builds

## Setup Required

### 1. Create GitHub Secrets

In your GitHub repo:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add these two:

#### Secret 1: `DOCKERHUB_USERNAME`
- **Value**: Your Docker Hub username (e.g., `vpaone59`)

#### Secret 2: `DOCKERHUB_TOKEN`
- **Value**: A Docker Hub Personal Access Token

### 2. Generate Docker Hub Personal Access Token

1. Log in to [Docker Hub](https://hub.docker.com)
2. Click your profile icon → **Account Settings** → **Security**
3. Click **New Access Token**
4. Give it a name: `GitHub Actions ObamaBot` (or similar)
5. Set permissions: **Read & Write** (sufficient for pushing images)
6. Click **Generate** and **copy the token**
7. Paste it as the `DOCKERHUB_TOKEN` secret in GitHub

**⚠️ Important**: Store this token securely. Don't share it or commit it to Git. GitHub encrypts it automatically.

## Workflow File

The workflow is defined in [`.github/workflows/docker-build.yml`](.github/workflows/docker-build.yml).

**Trigger**: Any push to the `main` branch

**Key environment variables** (defined in the workflow):
```yaml
tags: |
  ${{ secrets.DOCKERHUB_USERNAME }}/obamabot:latest
  ${{ secrets.DOCKERHUB_USERNAME }}/obamabot:${{ github.sha }}
```

## Verifying It Works

1. Make a commit and push to `main`:
   ```bash
   git add .
   git commit -m "test docker build"
   git push origin main
   ```

2. Go to your GitHub repo → **Actions** tab
3. You should see the workflow running (yellow indicator)
4. Wait for it to complete (green checkmark)
5. Check [Docker Hub](https://hub.docker.com/repositories) for the new image:
   - Go to your repo: `vpaone59/obamabot`
   - Verify tags under **Tags** tab (should see `latest` and a commit SHA)

## Using the Image

On your Unraid server:

```bash
# Pull the latest image
docker pull vpaone59/obamabot:latest

# Or pull a specific commit version (for rollbacks)
docker pull vpaone59/obamabot:abc1234def5678

# Update docker-compose.yml to use the new image
# Then redeploy:
docker-compose down
docker-compose up -d
```

## Troubleshooting

### Workflow fails with "Unable to push"
- Verify `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` are set correctly in GitHub Secrets
- Ensure the token hasn't expired (Docker Hub tokens don't expire by default, but re-create if unsure)

### Image not updating on Docker Hub
- Check GitHub Actions logs (repo → Actions → click the failed run)
- Verify you pushed to `main` (not another branch)

### How to skip a build
Add `[skip ci]` to your commit message:
```bash
git commit -m "docs: update readme [skip ci]"
```

## Notes

- Builds use multi-stage Docker BuildKit caching for efficiency
- Layer caching is stored on Docker Hub, so subsequent builds are much faster
- Images are built fresh every time (no stale layers unless explicitly cached)
- The Dockerfile uses Python 3.13 slim image with uv for dependency management
