import os
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import cv2
from moviepy.editor import VideoFileClip
import numpy as np

# Replace with your own values
API_ID = "23883349"
API_HASH = "9ae2939989ed439ab91419d66b61a4a4"
BOT_TOKEN = "7763711532:AAGh6rz7TPCXb_dca2j26sbv77j6wN9plCM"

app = Client("screenshot_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text("👋 Welcome to the Screenshot Generator Bot!\n\n"
                             "Send me a video, and I'll analyze it for you. "
                             "Then you can generate up to 20 screenshots from it. 🎬📸")

@app.on_message(filters.video)
async def handle_video(client: Client, message: Message):
    video = message.video
    file_name = f"{message.from_user.id}_{int(time.time())}.mp4"
    
    # Download the video
    await message.reply_text("⏳ Downloading and analyzing the video...")
    await message.download(file_name)
    
    # Analyze video
    clip = VideoFileClip(file_name)
    duration = int(clip.duration)
    size = os.path.getsize(file_name) / (1024 * 1024)  # Size in MB
    
    # Send analysis results
    await message.reply_text(f"📊 Video Analysis:\n\n"
                             f"🎞️ Name: {video.file_name}\n"
                             f"📏 Size: {size:.2f} MB\n"
                             f"⏱️ Duration: {duration} seconds\n"
                             f"🖼️ Format: {video.mime_type}\n\n"
                             f"How many screenshots do you want? (1-20)")
    
    # Set user state
    app.user_state[message.from_user.id] = {
        "file_name": file_name,
        "duration": duration
    }

@app.on_message(filters.text & filters.private)
async def generate_screenshots(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in app.user_state:
        await message.reply_text("Please send a video first.")
        return
    
    try:
        num_screenshots = int(message.text)
        if num_screenshots < 1 or num_screenshots > 20:
            raise ValueError
    except ValueError:
        await message.reply_text("Please enter a valid number between 1 and 20.")
        return
    
    file_name = app.user_state[user_id]["file_name"]
    duration = app.user_state[user_id]["duration"]
    
    await message.reply_text(f"🎬 Generating {num_screenshots} screenshots...")
    
    # Generate screenshots
    cap = cv2.VideoCapture(file_name)
    frames = []
    for i in range(num_screenshots):
        time = int((i + 1) * duration / (num_screenshots + 1))
        cap.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    
    # Create a collage of screenshots
    rows = int(np.ceil(np.sqrt(num_screenshots)))
    cols = int(np.ceil(num_screenshots / rows))
    cell_width = 640
    cell_height = 360
    collage = np.zeros((rows * cell_height, cols * cell_width, 3), dtype=np.uint8)
    
    for i, frame in enumerate(frames):
        row = i // cols
        col = i % cols
        resized_frame = cv2.resize(frame, (cell_width, cell_height))
        collage[row * cell_height:(row + 1) * cell_height,
                col * cell_width:(col + 1) * cell_width] = resized_frame
    
    # Save and send the collage
    collage_file = f"{user_id}_collage.jpg"
    cv2.imwrite(collage_file, collage)
    await message.reply_photo(collage_file, caption=f"🖼️ Here are your {num_screenshots} screenshots!")
    
    # Clean up
    os.remove(file_name)
    os.remove(collage_file)
    del app.user_state[user_id]

app.user_state = {}

print("Bot is running...")
app.run()

