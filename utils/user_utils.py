import os
import json
import discord
import grapheme

USERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'users')

# Ensure users directory exists
os.makedirs(USERS_DIR, exist_ok=True)

def create_user(user_id, data=None):
    """Create a new user JSON file."""
    print(f"[DEBUG] Creating user file for {user_id}")
    if data is None:
        data = {}
    file_path = os.path.join(USERS_DIR, f"{user_id}.json")
    if os.path.exists(file_path):
        print(f"[DEBUG] User file already exists: {file_path}")
        raise FileExistsError("User file already exists")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"[DEBUG] User file created: {file_path}")

def update_user(user_id, new_data):
    """Update an existing user JSON file. If it doesn't exist, create it first."""
    print(f"[DEBUG] Updating user file for {user_id}")
    file_path = os.path.join(USERS_DIR, f"{user_id}.json")
    if not os.path.exists(file_path):
        print(f"[DEBUG] User file does not exist: {file_path}, creating new file.")
        create_user(user_id)
    with open(file_path, 'r', encoding='utf-8') as f:
        current_data = json.load(f)
    current_data.update(new_data)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, indent=4)
    print(f"[DEBUG] User file updated: {file_path}")

def delete_user(user_id):
    """Delete a user JSON file."""
    print(f"[DEBUG] Deleting user file for {user_id}")
    file_path = os.path.join(USERS_DIR, f"{user_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"[DEBUG] User file deleted: {file_path}")
    else:
        print(f"[DEBUG] User file does not exist: {file_path}")
        raise FileNotFoundError("User file does not exist")

def get_user(user_id):
    """Retrieve user data from JSON file. If it doesn't exist, create it."""
    print(f"[DEBUG] Retrieving user file for {user_id}")
    file_path = os.path.join(USERS_DIR, f"{user_id}.json")
    if not os.path.exists(file_path):
        print(f"[DEBUG] User file does not exist: {file_path}, creating new file.")
        create_user(user_id)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"[DEBUG] User data loaded for {user_id}")
    return data

def safe_discord_nick(nick: str, max_len: int = 32) -> str:
    # Convert iterator to list before slicing
    return ''.join(list(grapheme.graphemes(nick))[:max_len])

async def update_member_nickname(guild: discord.Guild, user_id: int, user_data: dict, display_name: str):
    try:
        if guild and guild.me.guild_permissions.manage_nicknames:
            member = guild.get_member(user_id)
            if member:
                # Reset nickname to display_name first to avoid doubling
                if member.nick and member.nick != display_name:
                    await member.edit(nick=display_name, reason="Reset nickname before updating by tag-bot")

                tag = user_data.get("tag", "")
                show_tag = user_data.get("show_tag", True)

                # Build nickname parts
                parts = [display_name]
                if show_tag and tag:
                    parts.append(f"[{tag}]")

                new_nick = " ".join(parts)
                new_nick = safe_discord_nick(new_nick, 32)
                if member.nick != new_nick:
                    await member.edit(nick=new_nick, reason="Updated by tag-bot")
    except Exception as e:
        print(f"[NICKNAME] Could not update nickname for {user_id}: {e}")
