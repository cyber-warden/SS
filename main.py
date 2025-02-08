import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from video_processor import VideoProcessor
from ui_helper import UIHelper

API_ID = "23883349"
API_HASH = "9ae2939989ed439ab91419d66b61a4a4"
BOT_TOKEN = "7763711532:AAGh6rz7TPCXb_dca2j26sbv77j6wN9plCM"

app = Client("screenshot_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
video_processor = VideoProcessor()
ui_helper = UIHelper()

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text(ui_helper.get_welcome_message())

@app.on_message(filters.video)
async def handle_video(client: Client, message: Message):
    chat_id = message.chat.id
    video = message.video

    # Send initial processing message
    processing_msg = await message.reply_text("🎥 Processing your video... Please wait.")

    try:
        # Download video
        video_path = await message.download()

        # Analyze video
        metadata = await video_processor.analyze_video(video_path)

        # Update message with metadata and prompt
        await processing_msg.edit_text(ui_helper.get_metadata_message(metadata))

        # Wait for user input
        while True:
            try:
                user_input = await client.wait_for_message(chat_id, timeout=300)  # 5 minutes timeout
                num_screenshots = int(user_input.text)
                if 1 <= num_screenshots <= 10:
                    break
                else:
                    await message.reply_text("Please enter a number between 1 and 10.")
            except ValueError:
                await message.reply_text("Please enter a valid number.")
            except asyncio.TimeoutError:
                await message.reply_text("Timeout. Please send the video again.")
                return

        # Generate screenshots
        progress_msg = await message.reply_text("Generating screenshots: [⬜⬜⬜⬜⬜]")
        screenshots = await video_processor.generate_screenshots(video_path, num_screenshots, progress_callback=lambda p: asyncio.create_task(ui_helper.update_progress(progress_msg, p)))

        # Send screenshots
        media_group = [InputMediaPhoto(screenshot) for screenshot in screenshots]
        await client.send_media_group(chat_id, media_group)

        await progress_msg.delete()
        await message.reply_text("✅ Screenshots generated successfully!")

    except Exception as e:
        await message.reply_text(f"❌ An error occurred: {str(e)}")
    finally:
        # Clean up
        video_processor.cleanup(video_path)

if __name__ == "__main__":
    app.run()
