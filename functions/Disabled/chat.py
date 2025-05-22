import discord
from discord.ext import commands
import os

from utils import user_utils

USERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'users')

class ChatHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from bots
        if message.author.bot:
            return

        user_id = str(message.author.id)
        user_file = os.path.join(USERS_DIR, f"{user_id}.json")

        if not os.path.exists(user_file):
            return  # Ignore if user file does not exist

        try:
            user_data = user_utils.get_user(user_id)
        except Exception as e:
            print(f"[CHAT] Failed to load user data for {user_id}: {e}")
            return

        # Only process if user is active
        if not user_data.get("active", True):
            return

        # Build display parts based on show_* flags
        display_name = message.author.display_name

        tag = user_data.get("tag", "")
        pronouns = user_data.get("pronouns", "")
        gender = user_data.get("gender", "")

        show_tag = user_data.get("show_tag", True)
        show_pronouns = user_data.get("show_pronouns", True)
        show_gender = user_data.get("show_gender", True)

        display_parts = [display_name]

        # Tag with gray background using Discord's code block formatting
        if show_tag and tag:
            display_parts.append(f"`{tag}`")
        # Gender and pronouns in parentheses
        extra_info = []
        if show_gender and gender:
            extra_info.append(gender)
        if show_pronouns and pronouns:
            extra_info.append(pronouns)
        if extra_info:
            display_parts.append(f"({' | '.join(extra_info)})")

        display_line = " ".join(display_parts)

        # Output to console
        print(f"[CHAT] {display_line} (ID: {user_id}): {message.content}")

        # Send formatted message to channel and delete original
        try:
            await message.channel.send(f"**{display_line}:**\n{message.content}")
            #await message.delete()
        except discord.Forbidden:
            print(f"[CHAT] Missing permissions to send/delete messages in {message.channel}")
        except discord.NotFound:
            pass

        # Update user's nickname if possible
        try:
            if message.guild and message.guild.me.guild_permissions.manage_nicknames:
                member = message.guild.get_member(message.author.id)
                if member:
                    # Only update if nickname_toggle is enabled
                    if user_data.get("nickname_toggle", True):
                        await user_utils.update_member_nickname(
                            message.guild,
                            message.author.id,
                            user_data,
                            member.display_name
                        )
        except Exception as e:
            print(f"[CHAT] Could not update nickname for {message.author}: {e}")

async def setup(bot):
    await bot.add_cog(ChatHandler(bot))

