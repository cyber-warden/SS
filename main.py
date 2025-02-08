import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image
import time

# Bot credentials
API_ID = "23883349"
API_HASH = "9ae2939989ed439ab91419d66b61a4a4"
BOT_TOKEN = "7763711532:AAGh6rz7TPCXb_dca2j26sbv77j6wN9plCM"

# Initialize the bot
app = Client("screenshot_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to extract metadata
def extract_metadata(video_path: str) -> dict:
    with VideoFileClip(video_path) as video:
        return {
            "file_name": os.path.basename(video_path),
            "size": f"{os.path.getsize(video_path) / (1024 * 1024):.2f} MB",
            "duration": f"{video.duration:.2f} seconds",
            "format": video.fps,
        }

# Function to generate screenshots
async def generate_screenshots(video_path: str, num_screenshots: int, message: Message):
    with VideoFileClip(video_path) as video:
        duration = video.duration
        interval = duration / num_screenshots
        timestamps = [i * interval for i in range(num_screenshots)]

        # Create a folder to store screenshots
        output_folder = f"screenshots_{message.chat.id}"
        os.makedirs(output_folder, exist_ok=True)

        # Progress bar animation
        progress_bar_length = 10
        progress_message = await message.reply("Generating screenshots...\n[⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜]")

        for i, timestamp in enumerate(timestamps):
            # Update progress bar
            progress = int((i + 1) / num_screenshots * progress_bar_length)
            progress_bar = "🟩" * progress + "⬜" * (progress_bar_length - progress)
            await progress_message.edit_text(f"Generating screenshots...\n[{progress_bar}]")

            # Save screenshot
            frame = video.get_frame(timestamp)
            image = Image.fromarray(frame)
            image.save(f"{output_folder}/screenshot_{i + 1}.png")

        await progress_message.edit_text("✅ Screenshots generated successfully!")

        # Send screenshots to the user
        for i in range(num_screenshots):
            await message.reply_photo(f"{output_folder}/screenshot_{i + 1}.png")

        # Clean up
        for file in os.listdir(output_folder):
            os.remove(f"{output_folder}/{file}")
        os.rmdir(output_folder)

# Command to start the bot
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(
        "🎥 **Welcome to the Video Screenshot Bot!**\n\n"
        "Send me a video, and I'll analyze it and generate screenshots for you!"
    )

# Handle video messages
@app.on_message(filters.video)
async def handle_video(client, message: Message):
    # Download the video
    video_path = await message.download()

    # Extract metadata
    metadata = extract_metadata(video_path)
    metadata_text = (
        "📄 **Video Metadata:**\n"
        f"📂 **File Name:** `{metadata['file_name']}`\n"
        f"📏 **Size:** `{metadata['size']}`\n"
        f"⏱️ **Duration:** `{metadata['duration']}`\n"
        f"🎞️ **Format:** `{metadata['format']} fps`\n\n"
        "How many screenshots would you like to generate?"
    )

    # Ask for the number of screenshots
    await message.reply_text(
        metadata_text,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("3", callback_data="3")],
                [InlineKeyboardButton("5", callback_data="5")],
                [InlineKeyboardButton("10", callback_data="10")],
            ]
        ),
    )

    # Clean up
    os.remove(video_path)

# Handle callback queries for screenshot count
@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    num_screenshots = int(callback_query.data)
    await callback_query.answer(f"Generating {num_screenshots} screenshots...")

    # Download the video again (since it was deleted earlier)
    video_message = callback_query.message.reply_to_message
    video_path = await video_message.download()

    # Generate screenshots
    await generate_screenshots(video_path, num_screenshots, video_message)

    # Clean up
    os.remove(video_path)

# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    app.run()
