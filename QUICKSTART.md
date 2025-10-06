# Quick Start Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Get Bot Token

1. Open Telegram and find [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions
3. Copy the bot token (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### Step 2: Get Your Telegram ID

1. Open [@userinfobot](https://t.me/userinfobot)
2. Send any message
3. Copy your ID number (looks like: `123456789`)

### Step 3: Clone and Configure

```bash
# Clone repository
git clone https://github.com/DigneZzZ/remnabot.git
cd remnabot

# Create .env file
cp .env.example .env

# Edit .env with your favorite editor
nano .env  # or notepad .env on Windows
```

Fill in these required values in `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_step_1
ADMIN_IDS=your_telegram_id_from_step_2
REMNAWAVE_API_URL=http://your-remnawave-host:8000
REMNAWAVE_USERNAME=admin
REMNAWAVE_PASSWORD=your_password
```

### Step 4: Run

#### Option A: Docker (Recommended)

```bash
docker-compose up -d
```

#### Option B: Local Python

**Windows:**
```powershell
.\dev.ps1
```

**Linux/Mac:**
```bash
chmod +x dev.sh
./dev.sh
```

### Step 5: Test

1. Open Telegram
2. Find your bot by username
3. Send `/start`
4. You should see the main menu! 🎉

## 📋 What's Next?

- Read [README.md](README.md) for full documentation
- Read [DEVELOPMENT.md](DEVELOPMENT.md) if you want to contribute
- Check [STRUCTURE.md](STRUCTURE.md) to understand the code

## 🆘 Troubleshooting

### Bot doesn't respond?

- Check logs: `docker-compose logs -f` (Docker) or look in console (local)
- Verify your Telegram ID is in `ADMIN_IDS`
- Verify bot token is correct

### API connection error?

- Check `REMNAWAVE_API_URL` is correct
- Verify Remnawave is running
- Check username/password

### Other issues?

Check [DEVELOPMENT.md](DEVELOPMENT.md) Common Issues section.

## 📊 Example Configuration

### Single Admin Setup

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789
REMNAWAVE_API_URL=http://localhost:8000
REMNAWAVE_USERNAME=admin
REMNAWAVE_PASSWORD=secret123
PIN_CODE=1234
LOG_LEVEL=INFO
DEBUG=False
REDIS_ENABLED=False
```

### Multiple Admins Setup

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789,987654321,555444333
REMNAWAVE_API_URL=http://remnawave.example.com:8000
REMNAWAVE_USERNAME=admin
REMNAWAVE_PASSWORD=secret123
PIN_CODE=5678
LOG_LEVEL=INFO
DEBUG=False
REDIS_ENABLED=True
REDIS_URL=redis://localhost:6379/0
```

### Development Setup

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789
REMNAWAVE_API_URL=http://localhost:8000
REMNAWAVE_USERNAME=admin
REMNAWAVE_PASSWORD=admin
PIN_CODE=0000
LOG_LEVEL=DEBUG
DEBUG=True
REDIS_ENABLED=False
```

## 🎯 Features Overview

Once started, you can:

- ✅ View system statistics
- ✅ Manage users (create, edit, delete, extend)
- ✅ Manage hosts
- ✅ Manage nodes with traffic statistics
- ✅ View HWID device statistics
- ✅ Manage squads
- ✅ Perform mass operations

All through simple Telegram menus!
