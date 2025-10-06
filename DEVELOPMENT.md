# Development Guide

## Prerequisites

- Python 3.11 or higher
- pip
- Git
- Docker and Docker Compose (for containerized development)
- Access to Remnawave API instance

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/DigneZzZ/remnabot.git
cd remnabot
```

### 2. Create Environment File

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and fill in your values:

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_from_@BotFather
ADMIN_IDS=your_telegram_id,another_admin_id
REMNAWAVE_API_URL=http://your-remnawave-host:8000
REMNAWAVE_USERNAME=admin
REMNAWAVE_PASSWORD=your_password
PIN_CODE=1234

# Optional
LOG_LEVEL=DEBUG
DEBUG=True
REDIS_ENABLED=False
```

### 3. Get Your Telegram ID

Use [@userinfobot](https://t.me/userinfobot) to get your Telegram user ID.

### 4. Get Bot Token

1. Open [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Follow instructions
4. Copy the token

## Development Options

### Option 1: Local Development (Recommended for development)

#### Windows PowerShell

```powershell
# Run the development script
.\dev.ps1
```

Or manually:

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements-dev.txt

# Set debug mode
$env:DEBUG = "True"
$env:LOG_LEVEL = "DEBUG"

# Run bot
python -m src.main
```

#### Linux/Mac

```bash
# Run the development script
chmod +x dev.sh
./dev.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Set debug mode
export DEBUG=True
export LOG_LEVEL=DEBUG

# Run bot
python -m src.main
```

### Option 2: Docker Development

```bash
# Build and run with docker-compose
docker-compose -f docker-compose.dev.yml up --build

# Run in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f remnabot-dev

# Stop
docker-compose -f docker-compose.dev.yml down
```

## Project Structure

See [STRUCTURE.md](STRUCTURE.md) for detailed project structure.

## Making Changes

### Adding a New Handler

1. Create a new file in `src/handlers/`:

```python
# src/handlers/my_feature.py
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from src.core.logger import log
from src.middleware.auth import admin_only
from src.utils.keyboards import keyboards

@admin_only
async def my_feature_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = "🎯 <b>My Feature</b>\n\nFeature content here"
    
    await query.edit_message_text(
        text,
        reply_markup=keyboards.back_to_main(),
        parse_mode=ParseMode.HTML
    )

def register_my_feature_handlers(application):
    application.add_handler(
        CallbackQueryHandler(my_feature_callback, pattern="^my_feature$")
    )
    log.info("My feature handlers registered")
```

2. Register in `src/main.py`:

```python
from src.handlers.my_feature import register_my_feature_handlers

# In main():
register_my_feature_handlers(application)
```

3. Add keyboard button in `src/utils/keyboards.py`:

```python
def main_menu(self) -> InlineKeyboardMarkup:
    keyboard = [
        # ... existing buttons ...
        [
            InlineKeyboardButton("🎯 My Feature", callback_data="my_feature"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
```

### Adding API Methods

Add methods to `src/services/api.py`:

```python
async def my_new_api_call(self, param: str) -> Dict[str, Any]:
    """Description of what this does"""
    log.info(f"Calling my API with {param}")
    return await self._make_request("GET", f"/api/my-endpoint/{param}")
```

### Adding Formatters

Add formatters to `src/utils/formatters.py`:

```python
@staticmethod
def format_my_data(data: Dict[str, Any]) -> str:
    """Format my data for display"""
    value = data.get('value', 'N/A')
    
    text = f"""
🎯 <b>My Data</b>

<b>Value:</b> {value}
    """
    
    return text.strip()
```

## Testing

### Manual Testing

1. Start the bot in debug mode
2. Send `/start` to your bot
3. Navigate through menus
4. Check logs for any errors

### Logs

Logs are written to:
- Console (with colors in debug mode)
- `logs/remnabot_YYYY-MM-DD.log` (all logs)
- `logs/errors_YYYY-MM-DD.log` (errors only)

### Debug Mode

In debug mode you get:
- Verbose logging
- Request/response bodies in logs
- Stack traces for errors
- More detailed timestamps

## Common Issues

### Issue: "Не удается разрешить импорт"

**Solution**: Make sure you're running from the project root and the virtual environment is activated.

### Issue: Bot doesn't respond

**Solution**: Check:
1. Bot token is correct
2. Your Telegram ID is in ADMIN_IDS
3. Remnawave API is accessible
4. Check logs for errors

### Issue: API authentication fails

**Solution**: Check:
1. REMNAWAVE_API_URL is correct
2. Username and password are correct
3. API is running and accessible

### Issue: Redis connection fails

**Solution**: 
- Set `REDIS_ENABLED=False` if you don't need caching
- Or start Redis: `docker run -d -p 6379:6379 redis:7-alpine`

## Code Style

- Use type hints
- Follow PEP 8
- Use async/await for I/O operations
- Add docstrings to functions
- Use the logger instead of print()
- Handle exceptions gracefully

### Example:

```python
async def my_function(param: str) -> Dict[str, Any]:
    """
    Description of what this function does
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
    try:
        log.info(f"Doing something with {param}")
        result = await some_async_operation(param)
        return result
    except Exception as e:
        log.error(f"Error in my_function: {e}")
        raise
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: add my feature"

# Push to remote
git push origin feature/my-feature

# Create pull request on GitHub
```

### Commit Message Format

- `feat:` - new feature
- `fix:` - bug fix
- `docs:` - documentation changes
- `style:` - formatting changes
- `refactor:` - code refactoring
- `test:` - adding tests
- `chore:` - maintenance tasks

## Resources

- [python-telegram-bot documentation](https://docs.python-telegram-bot.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Remnawave API Documentation](your-api-docs-url)
- [httpx documentation](https://www.python-httpx.org/)
- [loguru documentation](https://loguru.readthedocs.io/)

## Need Help?

- Check the logs first
- Read error messages carefully
- Use debug mode for more information
- Check GitHub issues
- Ask in project discussions
