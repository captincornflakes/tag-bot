import discord
from discord import app_commands
from discord.ext import commands

from utils import user_utils
from utils import choice_loader

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def gender_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=g, value=g)
            for g in choice_loader.load_genders()
            if current.lower() in g.lower()
        ][:25]

    async def pronouns_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=p, value=p)
            for p in choice_loader.load_pronouns()
            if current.lower() in p.lower()
        ][:25]

    async def tag_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=t, value=t)
            for t in choice_loader.load_tags()
            if current.lower() in t.lower()
        ][:25]

    @app_commands.command(name="profile", description="Set your gender, pronouns, and tags")
    @app_commands.describe(
        gender="Select your gender",
        pronouns="Select your pronouns",
        tag="Select a tag"
    )
    @app_commands.autocomplete(
        gender=gender_autocomplete,
        pronouns=pronouns_autocomplete,
        tag=tag_autocomplete
    )
    async def profile(
        self,
        interaction: discord.Interaction,
        gender: str,
        pronouns: str = "",
        tag: str = ""
    ):
        user_id = str(interaction.user.id)
        # Always set show_* and active to True by default when updating profile
        data = {
            "gender": gender,
            "show_gender": True,
            "pronouns": pronouns,
            "show_pronouns": True,
            "tag": tag,
            "show_tag": True,
            "active": True
        }
        user_utils.update_user(user_id, data)

        # Update nickname if enabled and possible
        try:
            if interaction.guild and interaction.guild.me.guild_permissions.manage_nicknames:
                member = interaction.guild.get_member(interaction.user.id)
                if member and data.get("nickname_toggle", True):
                    await user_utils.update_member_nickname(
                        interaction.guild,
                        interaction.user.id,
                        data,
                        member.display_name
                    )
        except Exception as e:
            print(f"[NICKNAME] Could not update nickname for {interaction.user}: {e}")

        await interaction.response.send_message(
            f"Profile updated!\n"
            f"Gender: {gender}\n"
            f"Pronouns: {pronouns}\n"
            f"Tag: {tag}\n"
            f"(Visibility and active are set to True by default. Use /settings to change.)",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Profile(bot))