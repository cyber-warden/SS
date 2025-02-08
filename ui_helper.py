from pyrogram.types import Message

class UIHelper:
    def get_welcome_message(self) -> str:
        return (
            "👋 Welcome to the Video Screenshot Bot! 🎬\n\n"
            "Send me a video, and I'll generate high-quality screenshots for you. "
            "You can choose how many screenshots you want, and I'll extract them "
            "at equal intervals throughout the video.\n\n"
            "Let's get started! 🚀"
        )

    def get_metadata_message(self, metadata: dict) -> str:
        return (
            f"📊 Video Analysis:\n\n"
            f"📁 File Name: `{metadata['filename']}`\n"
            f"📏 Size: **{metadata['size']}**\n"
            f"⏱ Duration: **{metadata['duration']}**\n"
            f"🎞 Format: **{metadata['format']}**\n\n"
            f"How many screenshots would you like? (1-10)"
        )

    async def update_progress(self, message: Message, progress: float):
        progress_bar = self.generate_progress_bar(progress)
        await message.edit_text(f"Generating screenshots: {progress_bar}")

    @staticmethod
    def generate_progress_bar(progress: float) -> str:
        filled = int(progress * 5)
        return f"[{'🟩' * filled}{'⬜' * (5 - filled)}]"
