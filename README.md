# MangaKakalot Telegram Bot

A Telegram bot for searching, browsing and downloading manga from MangaKakalot.

## Features

- Search manga by title
- Browse popular manga
- View manga details including description, status and genres
- Download chapters in multiple formats:
  - PDF
  - EPUB 
  - CBZ
- Paginated navigation for both search results and chapters

## Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
- `API_ID`: Telegram API ID
- `API_HASH`: Telegram API hash  
- `BOT_TOKEN`: Telegram bot token

3. Run the bot:
```bash
python bot.py
```

## Usage

Commands:
- `/search [query]` - Search for manga
- `/popular` - Browse popular manga

After selecting a manga, you can:
- View details and available chapters
- Download chapters in your preferred format

## File Structure

- `bot.py`: Main bot implementation
- `scraper.py`: Manga scraping functionality
- `config.py`: Configuration
- `utils/`: Utility functions
  - `callbacks.py`: Callback handling
  - `file_downloaders.py`: File download and conversion
  - `keyboards.py`: Inline keyboard builders
  - `progress.py`: Upload progress tracking

## Requirements

- Python 3.8+
- pyrogram
- aiohttp
- ebooklib
- Pillow
