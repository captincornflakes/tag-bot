import discord
from discord import app_commands
from discord.ext import commands
from utils import user_utils

NICKNAME_TOGGLE_KEY = "nickname_toggle"

class NicknameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nickname", description="Toggle automatic nickname changes by the bot")
    async def nickname(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        user_data = user_utils.get_user(user_id)
        current = user_data.get(NICKNAME_TOGGLE_KEY, True)
        new_value = not current
        user_data[NICKNAME_TOGGLE_KEY] = new_value
        user_utils.update_user(user_id, user_data)
        status = "enabled" if new_value else "disabled"

        # Update or reset nickname immediately
        try:
            if interaction.guild and interaction.guild.me.guild_permissions.manage_nicknames:
                member = interaction.guild.get_member(interaction.user.id)
                if member:
                    if new_value:
                        # Reload user data to ensure latest info
                        user_data = user_utils.get_user(user_id)
                        await user_utils.update_member_nickname(
                            interaction.guild,
                            interaction.user.id,
                            user_data,
                            interaction.user.display_name
                        )
                    else:
                        try:
                            if member.nick != interaction.user.display_name:
                                await member.edit(nick=interaction.user.display_name, reason="Nickname reset by tag-bot")
                        except discord.Forbidden as e:
                            if getattr(e, "code", None) == 50013:
                                await interaction.response.send_message(
                                    "❌ I do not have permission to change your nickname. Please check my role position and permissions.",
                                    ephemeral=True
                                )
                                return
                            else:
                                print(f"[NICKNAME] Could not reset nickname for {interaction.user}: {e}")
        except discord.Forbidden as e:
            if getattr(e, "code", None) == 50013:
                await interaction.response.send_message(
                    "❌ I do not have permission to change your nickname. Please check my role position and permissions.",
                    ephemeral=True
                )
                return
            else:
                print(f"[NICKNAME] Could not update nickname for {interaction.user}: {e}")
        except Exception as e:
            print(f"[NICKNAME] Could not update nickname for {interaction.user}: {e}")

        await interaction.response.send_message(
            f"Automatic nickname changes are now **{status}** for you.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(NicknameCog(bot))