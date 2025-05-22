import discord
from discord import app_commands
from discord.ext import commands

from utils import user_utils
from utils import choice_loader

class VisibilityView(discord.ui.View):
    def __init__(self, user_id, current_settings):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.current_settings = current_settings

        self.gender_select = discord.ui.Select(
            placeholder="Show Gender?",
            options=[
                discord.SelectOption(label="Yes", value="True", default=current_settings.get("show_gender", True)),
                discord.SelectOption(label="No", value="False", default=not current_settings.get("show_gender", True)),
            ]
        )
        self.pronouns_select = discord.ui.Select(
            placeholder="Show Pronouns?",
            options=[
                discord.SelectOption(label="Yes", value="True", default=current_settings.get("show_pronouns", True)),
                discord.SelectOption(label="No", value="False", default=not current_settings.get("show_pronouns", True)),
            ]
        )
        self.tag_select = discord.ui.Select(
            placeholder="Show Tag?",
            options=[
                discord.SelectOption(label="Yes", value="True", default=current_settings.get("show_tag", True)),
                discord.SelectOption(label="No", value="False", default=not current_settings.get("show_tag", True)),
            ]
        )
        self.active_select = discord.ui.Select(
            placeholder="Active?",
            options=[
                discord.SelectOption(label="Yes", value="True", default=current_settings.get("active", True)),
                discord.SelectOption(label="No", value="False", default=not current_settings.get("active", True)),
            ]
        )

        self.add_item(self.gender_select)
        self.add_item(self.pronouns_select)
        self.add_item(self.tag_select)
        self.add_item(self.active_select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only allow the user who invoked the command to interact
        return str(interaction.user.id) == self.user_id

    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Update user data from selects
        user_data = user_utils.get_user(self.user_id)
        user_data["show_gender"] = self.gender_select.values[0] == "True"
        user_data["show_pronouns"] = self.pronouns_select.values[0] == "True"
        user_data["show_tag"] = self.tag_select.values[0] == "True"
        user_data["active"] = self.active_select.values[0] == "True"
        user_utils.update_user(self.user_id, user_data)  # Save changes

        # Reload user data to ensure latest info is used for nickname
        user_data = user_utils.get_user(self.user_id)

        # Update or clear nickname based on "active"
        try:
            if interaction.guild and interaction.guild.me.guild_permissions.manage_nicknames:
                member = interaction.guild.get_member(int(self.user_id))
                if member:
                    if not user_data.get("active", True):
                        # Clear nickname (reset to user's display name)
                        if member.nick != member.display_name:
                            await member.edit(nick=member.display_name, reason="Nickname cleared by tag-bot (inactive)")
                    elif user_data.get("nickname_toggle", True):
                        await user_utils.update_member_nickname(
                            interaction.guild,
                            int(self.user_id),
                            user_data,
                            member.display_name
                        )
        except Exception as e:
            print(f"[NICKNAME] Could not update nickname for {self.user_id}: {e}")

        await interaction.response.edit_message(
            content="Visibility and active settings updated!",
            embed=None,
            view=None
        )

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="settings", description="Edit your profile visibility and active settings")
    async def settings(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        try:
            user_data = user_utils.get_user(user_id)
        except FileNotFoundError:
            user_data = {"show_gender": True, "show_pronouns": True, "show_tag": True, "active": True}
        embed = discord.Embed(
            title="Edit Profile Visibility & Active",
            description="Choose which profile fields to show to others and set your active status.\n\n"
                        "**Current Settings:**",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Show Gender",
            value=f"**{'Yes' if user_data.get('show_gender', True) else 'No'}**",
            inline=False
        )
        embed.add_field(
            name="Show Pronouns",
            value=f"**{'Yes' if user_data.get('show_pronouns', True) else 'No'}**",
            inline=False
        )
        embed.add_field(
            name="Show Tag",
            value=f"**{'Yes' if user_data.get('show_tag', True) else 'No'}**",
            inline=False
        )
        embed.add_field(
            name="Active",
            value=f"**{'Yes' if user_data.get('active', True) else 'No'}**",
            inline=False
        )
        view = VisibilityView(user_id, user_data)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Settings(bot))