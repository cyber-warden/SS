import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from moviepy.editor import VideoFileClip
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

# Replace these with your own values
API_ID = "YOUR_API_ID"
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Initialize the Pyrogram client
app = Client("screenshot_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Spinner animation for status updates
spinner = ["🔄", "🌀", "🌪️", "🌊", "✨", "⚡", "💫", "🌟"]

# Function to analyze video metadata
def analyze_video(file_path: str):
    parser = createParser(file_path)
    metadata = extractMetadata(parser)
    if not metadata:
        return None
    return {
        "name": os.path.basename(file_path),
        "size": f"{os.path.getsize(file_path) / (1024 * 1024):.2f} MB",
        "duration": metadata.get("duration").seconds,
        "format": metadata.get("format")
    }

# Function to generate screenshots
def generate_screenshots(file_path: str, num_screenshots: int, duration: int):
    clip = VideoFileClip(file_path)
    timestamps = [i * (duration / num_screenshots) for i in range(num_screenshots)]
    screenshots = []
    for i, timestamp in enumerate(timestamps):
        screenshot_path = f"screenshot_{i+1}.jpg"
        clip.save_frame(screenshot_path, t=timestamp)
        screenshots.append(screenshot_path)
    clip.close()
    return screenshots

# Function to update status with animation
async def update_status(message: Message, text: str, delay: float = 0.5):
    for frame in spinner:
        await message.edit_text(f"{frame} {text}")
        time.sleep(delay)

# Start command
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text("🎥 **Welcome to the Screenshot Generator Bot!**\n\n"
                             "Send me a video, and I'll analyze it and generate screenshots for you! 🚀")

# Handle video files
@app.on_message(filters.video)
async def handle_video(client: Client, message: Message):
    # Download the video
    status_msg = await message.reply_text("📥 **Downloading video...**")
    video_path = await message.download()
    await update_status(status_msg, "📥 **Downloading video...**")

    # Analyze video metadata
    await update_status(status_msg, "🔍 **Analyzing video...**")
    video_info = analyze_video(video_path)
    if not video_info:
        await status_msg.edit_text("❌ **Failed to analyze the video. Please try again.**")
        return

    # Send video info
    info_text = (
        f"📄 **Video Name:** `{video_info['name']}`\n"
        f"📦 **Size:** `{video_info['size']}`\n"
        f"⏱️ **Duration:** `{video_info['duration']} seconds`\n"
        f"📁 **Format:** `{video_info['format']}`\n\n"
        "🛠️ **How many screenshots do you want?** (Enter a number)"
    )
    await status_msg.edit_text(info_text)

    # Wait for user input
    num_screenshots = await client.listen(message.chat.id, filters.text, timeout=30)
    try:
        num_screenshots = int(num_screenshots.text)
        if num_screenshots <= 0:
            raise ValueError
    except (ValueError, AttributeError):
        await status_msg.edit_text("❌ **Invalid input. Please enter a positive number.**")
        return

    # Generate screenshots
    await update_status(status_msg, "🖼️ **Generating screenshots...**")
    screenshots = generate_screenshots(video_path, num_screenshots, video_info["duration"])

    # Send screenshots
    await update_status(status_msg, "📤 **Uploading screenshots...**")
    media_group = []
    for screenshot in screenshots:
        media_group.append({"type": "photo", "media": screenshot})
    await client.send_media_group(message.chat.id, media_group)
    await status_msg.edit_text("✅ **Screenshots generated successfully!**")

    # Clean up
    for screenshot in screenshots:
        os.remove(screenshot)
    os.remove(video_path)

# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    app.run()
