# Auto Caption Bot with Advanced Variables
# Deployable on Koyeb/Heroku/Railway

import os
import re
import asyncio
from datetime import datetime
import pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode

# Configuration
app_id = int(os.environ.get("APP_ID", "20919625"))
api_hash = os.environ.get("API_HASH", "40168846bf06f4ff443f0f7a4182bf8d")
bot_token = os.environ.get("BOT_TOKEN", "7212259744:AAFEHoo3NBmE02csGSSRyooQEOl7IazPrSI")
default_caption = os.environ.get("DEFAULT_CAPTION", """
🎬 {title} | {artist}
📅 {year} | 🗣️ {language} | 🎞️ {quality}
📺 S{season}E{episode} | ⏱️ {duration}
📊 {resolution} | 📦 {filesize}
✨ {wish}!
""")

# Initialize Pyrogram Client
app = Client(
    "AutoCaptionBotV2",
    api_id=app_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# Helper Functions
def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def get_time_based_wish():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 21:
        return "Good Evening"
    else:
        return "Good Night"

def parse_filename(filename):
    """Extract metadata from filename"""
    if not filename:
        return {}
    
    patterns = {
        'language': r'\[([A-Za-z]{2,3})\]|\(([A-Za-z]{2,3})\)',
        'year': r'(19|20)\d{2}',
        'quality': r'(480p|720p|1080p|2160p|4K|8K|HD|FHD|UHD)',
        'season': r'S(\d{1,2})|Season\s(\d{1,2})',
        'episode': r'E(\d{1,2})|Episode\s(\d{1,2})',
        'title': r'^(.+?)(?=[\[\(]|S\d|E\d|\d{4}|480p|720p|1080p)',
        'artist': r'-\s(.+?)(?=[\[\(]|S\d|E\d|\d{4}|480p|720p|1080p)'
    }
    
    metadata = {
        'filename': filename,
        'ext': filename.split('.')[-1].lower() if '.' in filename else '',
        'language': '',
        'year': '',
        'quality': '',
        'season': '',
        'episode': '',
        'title': '',
        'artist': ''
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            groups = [g for g in match.groups() if g]
            if groups:
                metadata[key] = groups[0]
    
    return metadata

# Bot Handlers
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    await message.reply_text(
        "👋 Hello! I'm an Advanced Auto Caption Bot\n\n"
        "Add me to your channel as admin with edit rights\n"
        "Use /setcaption to configure your template",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Updates Channel", url="t.me/VJ_Botz")],
            [InlineKeyboardButton("➕ Add to Channel", url=f"http://t.me/{client.me.username}?startchannel=true")]
        ])
    )

@app.on_message(filters.command("setcaption") & filters.private)
async def set_caption(client, message):
    # Implement caption template setting logic
    # Store in database for each user/channel
    await message.reply_text("Send me your new caption template with variables")

@app.on_message(filters.channel)
async def auto_caption(client, message):
    if not message.caption and not any([
        message.photo, message.video, 
        message.document, message.audio
    ]):
        return
    
    # Get file details
    file = (message.document or message.video or 
            message.audio or message.photo[-1] if message.photo else None)
    
    # Extract metadata
    file_name = getattr(file, "file_name", "")
    file_meta = parse_filename(file_name)
    
    # Prepare variables
    variables = {
        'filename': file_meta['filename'],
        'filesize': sizeof_fmt(getattr(file, "file_size", 0)),
        'caption': message.caption or '',
        'language': file_meta['language'],
        'year': file_meta['year'],
        'quality': file_meta['quality'],
        'season': file_meta['season'],
        'episode': file_meta['episode'],
        'ext': file_meta['ext'],
        'mime_type': getattr(file, "mime_type", ""),
        'title': file_meta.get('title', '') or getattr(file, "title", ""),
        'artist': file_meta.get('artist', '') or getattr(file, "performer", ""),
        'wish': get_time_based_wish(),
        'duration': str(datetime.timedelta(seconds=getattr(file, "duration", 0))),
        'height': str(getattr(file, "height", 0)),
        'width': str(getattr(file, "width", 0)),
        'resolution': f"{getattr(file, 'width', 0)}x{getattr(file, 'height', 0)}"
    }
    
    # Format caption
    try:
        new_caption = default_caption.format(**variables)
    except KeyError as e:
        new_caption = f"Error in template: {e}"
    
    # Edit message
    try:
        await message.edit_caption(new_caption)
    except Exception as e:
        print(f"Error editing caption: {e}")

# Start the Bot
print("⚡ Advanced Auto Caption Bot Started!")
print("📢 Updates: @Moviehub9089")
app.run()
