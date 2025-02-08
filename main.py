import os
import asyncio
import ffmpeg
from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image
from math import floor

# Bot credentials
API_ID = "23883349"
API_HASH = "9ae2939989ed439ab91419d66b61a4a4"
BOT_TOKEN = "7763711532:AAGh6rz7TPCXb_dca2j26sbv77j6wN9plCM"

# Initialize Pyrogram bot
bot = Client("screenshot_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dictionary to store user state (for screenshot count input)
user_state = {}

# Progress animation
def get_progress_bar(percentage):
    filled = floor(percentage * 5)
    return "[" + "🟩" * filled + "⬜" * (5 - filled) + "]"

@bot.on_message(filters.video)
async def video_handler(client, message: Message):
    video = message.video
    file_name = video.file_name or "Unknown"
    file_size = round(video.file_size / (1024 * 1024), 2)  # Convert to MB
    duration = video.duration  # In seconds
    mime_type = video.mime_type or "Unknown"

    if not duration:
        await message.reply("⚠️ Unable to analyze video duration. Please try another video.")
        return

    # Send video details
    reply_text = f"📹 **Video Details:**\n" \
                 f"📝 **Name:** `{file_name}`\n" \
                 f"💾 **Size:** `{file_size} MB`\n" \
                 f"⏳ **Duration:** `{duration} sec`\n" \
                 f"🗂 **Format:** `{mime_type}`\n\n" \
                 f"🔢 **How many screenshots do you want?** (Send a number)"
    
    sent_msg = await message.reply(reply_text)

    # Store user state for the next input
    user_state[message.chat.id] = {"message_id": sent_msg.id, "video": video}

@bot.on_message(filters.text & filters.private)
async def screenshot_request(client, message: Message):
    user_id = message.chat.id

    if user_id not in user_state:
        return  # Ignore if user is not in state

    try:
        num_screenshots = int(message.text)
        if num_screenshots <= 0:
            raise ValueError
    except ValueError:
        await message.reply("⚠️ Please enter a valid number (greater than 0).")
        return

    # Retrieve stored video details
    video_data = user_state.pop(user_id)
    video = video_data["video"]
    video_path = await bot.download_media(video)

    duration = video.duration
    output_images = []
    progress_msg = await message.reply(f"⏳ **Processing...**\n{get_progress_bar(0)}")

    try:
        # First screenshot at 1s
        first_screenshot_path = f"screenshot_1.jpg"
        ffmpeg.input(video_path, ss=1).output(first_screenshot_path, vframes=1).run(quiet=True, overwrite_output=True)
        output_images.append(first_screenshot_path)

        # Screenshots at equal intervals
        interval = duration // num_screenshots
        for i in range(1, num_screenshots + 1):
            time_sec = i * interval
            screenshot_path = f"screenshot_{i+1}.jpg"
            ffmpeg.input(video_path, ss=time_sec).output(screenshot_path, vframes=1).run(quiet=True, overwrite_output=True)
            output_images.append(screenshot_path)

            # Update progress bar
            progress = (i / num_screenshots)
            await progress_msg.edit(f"⏳ **Processing...**\n{get_progress_bar(progress)}")

        # Send screenshots
        for img in output_images:
            await message.reply_photo(img)

        await progress_msg.edit(f"✅ **Screenshots sent!**")

    except Exception as e:
        await message.reply(f"❌ **Error:** {str(e)}")

    finally:
        # Cleanup
        os.remove(video_path)
        for img in output_images:
            os.remove(img)

# Run the bot
bot.run()
