import discord
import gspread
import os
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import io
import datetime
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '$')
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', 'credentials.json')
ALLOWED_CHANNEL_ID = int(os.getenv('ALLOWED_CHANNEL_ID')) if os.getenv('ALLOWED_CHANNEL_ID') else None
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Validate required environment variables
if not BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN environment variable is required")
if not SHEET_ID:
    raise ValueError("GOOGLE_SHEET_ID environment variable is required")
if not ALLOWED_CHANNEL_ID:
    raise ValueError("ALLOWED_CHANNEL_ID environment variable is required")

# Google Sheets Setup
try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet("Discord-Bot")
    print(f"✅ Successfully connected to Google Sheets")
except Exception as e:
    print(f"❌ Error connecting to Google Sheets: {e}")
    raise

# Discord Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)

# Custom emojis for different categories
EMOJIS = {
    "dkp": "🏆",
    "stats": "📊",
    "info": "📋",
    "player": "👤",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "help": "ℹ️",
    "link": "🔗",
    "unlink": "🔓",
    "leaderboard": "🏅",
    "compare": "⚔️"
}

# Colors for different embed types
COLORS = {
    "primary": 0x3498DB,  # Blue
    "success": 0x2ECC71,  # Green
    "error": 0xE74C3C,    # Red
    "warning": 0xF39C12,  # Orange
    "dkp_low": 0xF39C12,  # Gold for low DKP
    "dkp_mid": 0x3498DB,  # Blue for mid DKP
    "dkp_high": 0x2ECC71, # Green for high DKP
}

# Function to create progress bar
def create_progress_bar(value, max_value, length=10):
    filled_length = int(length * value / max_value) if max_value > 0 else 0
    bar = "█" * filled_length + "░" * (length - filled_length)
    return bar

# Helper function to send embeds
def create_embed(title, description, color=COLORS["primary"], timestamp=True):
    embed = discord.Embed(title=title, description=description, color=color)
    if timestamp:
        embed.timestamp = datetime.datetime.now()
    embed.set_footer(text="Bot by 义 Ragńàr | Powered by Discord & Google Sheets")
    embed.set_author(name="DKP Discord Bot")
    return embed

# Function to send a channel restriction message
async def send_channel_error(ctx):
    embed = discord.Embed(
        title=f"{EMOJIS['warning']} Command Usage Restriction",
        description=f"This command can only be used in <#{ALLOWED_CHANNEL_ID}>. Please use it there.",
        color=COLORS["error"]
    )
    embed.set_footer(text="Please make sure you're in the correct channel to use the bot.")
    await ctx.send(embed=embed)

# Helper function to format large numbers
def format_number(num):
    try:
        num = int(str(num).replace(",", ""))
        if num >= 1_000_000:
            return f"{num/1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num/1_000:.2f}K"
        else:
            return str(num)
    except ValueError:
        return str(num)

# Command check for channel restriction
def in_allowed_channel():
    async def predicate(ctx):
        if ctx.channel.id != ALLOWED_CHANNEL_ID:
            await send_channel_error(ctx)
            return False
        return True
    return commands.check(predicate)

# 🏷️ Link a user ID
@bot.command()
@in_allowed_channel()
async def linkme(ctx, user_id: str = None):
    if user_id is None:
        await ctx.send(embed=create_embed(f"{EMOJIS['error']} Error", "Please provide a user ID to link (e.g., $linkme <ID>)."))
        return

    discord_user = f"{ctx.author.name}#{ctx.author.discriminator}" if hasattr(ctx.author, 'discriminator') else ctx.author.name
    records = sheet.get_all_values()

    # Check if this user is already linked
    for row in records:
        if row[2] == discord_user:  # Column C = Discord ID
            embed = create_embed(
                f"{EMOJIS['warning']} Already Linked", 
                f"You are already linked to ID **{row[0]}**.", 
                COLORS["warning"]
            )
            await ctx.send(embed=embed)
            return

    # Check if the provided user ID is already linked to another Discord account
    for i, row in enumerate(records):
        if row[0] == user_id:  # Column A = ID
            if row[2]:  # Column C (Discord ID) is not empty, meaning it's already linked
                embed = create_embed(
                    f"{EMOJIS['warning']} ID Already Linked", 
                    f"ID **{user_id}** is already linked to another Discord user.", 
                    COLORS["warning"]
                )
                await ctx.send(embed=embed)
                return

            # If ID is found but not linked, link it
            sheet.update_cell(i + 1, 3, discord_user)  # Column C = Discord ID
            
            embed = create_embed(
                f"{EMOJIS['success']} Link Successful", 
                f"**{discord_user}** has been linked to ID **{user_id}**!", 
                COLORS["success"]
            )
            embed.add_field(name="Next Steps", value="Use $stats to view your DKP statistics!")
            await ctx.send(embed=embed)
            return

    await ctx.send(embed=create_embed(f"{EMOJIS['error']} Error", "ID not found. Please check and try again.", COLORS["error"]))

# 🔗 De-link a user ID
@bot.command()
@in_allowed_channel()
async def unlink(ctx):
    discord_user = f"{ctx.author.name}#{ctx.author.discriminator}" if hasattr(ctx.author, 'discriminator') else ctx.author.name
    records = sheet.get_all_values()

    for i, row in enumerate(records):
        if row[2] == discord_user:  # Column C = Discord ID
            user_id = row[0]  # Save the ID for confirmation message
            
            sheet.update_cell(i+1, 3, "")  # Clear Discord ID (unlink)
            
            embed = create_embed(
                f"{EMOJIS['success']} Unlink Successful", 
                f"**{discord_user}** has been unlinked from ID **{user_id}**.", 
                COLORS["success"]
            )
            await ctx.send(embed=embed)
            return

    await ctx.send(embed=create_embed(f"{EMOJIS['error']} Error", "You are not linked to any ID.", COLORS["error"]))

# 📊 Get user stats
@bot.command()
@in_allowed_channel()
async def stats(ctx, member: Optional[discord.Member] = None):
    # Use message sender if no member specified
    target_user = member or ctx.author
    
    # Get Discord user identifier
    discord_user = f"{target_user.name}#{target_user.discriminator}" if hasattr(target_user, 'discriminator') else target_user.name
    
    # Send loading message
    loading_msg = await ctx.send(embed=create_embed(f"{EMOJIS['stats']} Loading", "Fetching data from the database..."))
    
    records = sheet.get_all_values()
    header = records[0]  # Get header row for field names
    
    # Find the indices of DKP fields
    dkp_score_index = -1
    dkp_goal_index = -1
    dkp_rate_index = -1
    
    for i, field in enumerate(header):
        if "DKP SCORE" in field.upper():
            dkp_score_index = i
        elif "DKP GOAL" in field.upper():
            dkp_goal_index = i
        elif "DKP RATE" in field.upper():
            dkp_rate_index = i
    
    # Hardcoded fallback if the search fails
    if dkp_goal_index == -1:
        dkp_goal_index = 13  # Column N (0-indexed)
    if dkp_score_index == -1:
        dkp_score_index = 14  # Column O (0-indexed)
    if dkp_rate_index == -1:
        dkp_rate_index = 15  # Column P (0-indexed)
    
    for row in records[1:]:  # Skip header
        if len(row) > 2 and row[2] == discord_user:  # Column C = Discord ID
            in_game_name = row[1] if len(row) > 1 else "Unknown"  # Assuming In-Game Name is in column B
            user_id = row[0] if len(row) > 0 else "Unknown"  # User ID in column A

            # Get DKP values for color
            dkp_rate = 0
            
            # Try to get DKP rate for color
            if dkp_rate_index >= 0 and dkp_rate_index < len(row) and row[dkp_rate_index]:
                try:
                    dkp_rate = int(row[dkp_rate_index].replace("%", ""))
                except (ValueError, TypeError):
                    pass
            
            # Determine color based on DKP rate
            if dkp_rate < 100:  # Less than 100% of goal
                embed_color = COLORS["dkp_low"]
            elif dkp_rate < 300:  # Between 100-300% of goal
                embed_color = COLORS["dkp_mid"]
            else:  # More than 300% of goal
                embed_color = COLORS["dkp_high"]

            # Create main embed
            embed = discord.Embed(
                title=f"{EMOJIS['stats']} Stats for {in_game_name}",
                description=f"ID: {user_id}\nIn-Game Name: {in_game_name}",
                color=embed_color
            )
            
            # Add user avatar
            embed.set_thumbnail(url=target_user.display_avatar.url)
            
            # For debugging, print column indices
            if LOG_LEVEL == "DEBUG":
                print(f"DKP Columns - Goal: {dkp_goal_index}, Score: {dkp_score_index}, Rate: {dkp_rate_index}")
                print(f"Row length: {len(row)}")
            
            # Make sure we don't go out of bounds
            dkp_goal_value = row[dkp_goal_index] if dkp_goal_index >= 0 and dkp_goal_index < len(row) else "N/A"
            dkp_score_value = row[dkp_score_index] if dkp_score_index >= 0 and dkp_score_index < len(row) else "N/A"
            dkp_rate_value = row[dkp_rate_index] if dkp_rate_index >= 0 and dkp_rate_index < len(row) else "N/A"
            
            # Always include DKP stats section
            embed.add_field(
                name=f"{EMOJIS['dkp']} DKP Stats",
                value=(
                    f"**DKP Score:** {dkp_score_value}\n"
                    f"**DKP Goal:** {dkp_goal_value}\n"
                    f"**DKP Rate:** {dkp_rate_value}"
                ),
                inline=False
            )
            
            # Categorize stats for other sections
            battle_stats = ""
            info_stats = ""
            
            # Process non-DKP fields
            for j in range(len(row)):
                if j >= len(header):
                    continue
                    
                field_name = header[j]
                value = row[j]
                
                # Skip unwanted, already displayed, or DKP fields
                if (field_name in ["ID", "IN-GAME NAME", "Discord ID", "POWER WEIGHT", "TOTAL SCORE", "RSS ASSISTANCE"] 
                    or not field_name 
                    or "DKP" in field_name):
                    continue
                
                # Group battle stats
                if any(battle_term in field_name.upper() for battle_term in ["KILL", "DEATH", "BATTLE", "WAR", "FIGHT"]):
                    battle_stats += f"**{field_name}:** {value}\n"
                
                # Other info
                else:
                    info_stats += f"**{field_name}:** {value}\n"
            
            # Add battle stats if present
            if battle_stats:
                embed.add_field(
                    name=f"{EMOJIS['stats']} Battle Stats",
                    value=battle_stats,
                    inline=False
                )
            
            # Add additional information
            if info_stats:
                embed.add_field(
                    name=f"{EMOJIS['info']} Additional Info",
                    value=info_stats,
                    inline=False
                )
            
            # Add timestamp and footer
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text="Stats updated after every Major War")
            
            # Delete loading message and send stats
            await loading_msg.delete()
            await ctx.send(embed=embed)
            return
    
    # Delete loading message if user not found
    await loading_msg.delete()
    
    if member:
        await ctx.send(embed=create_embed(
            f"{EMOJIS['error']} User Not Linked",
            f"The requested user is not linked to any ID in the database.",
            COLORS["error"]
        ))
    else:
        await ctx.send(embed=create_embed(
            f"{EMOJIS['error']} Not Linked",
            "You are not linked to any ID. Use $linkme <ID> first.",
            COLORS["error"]
        ))

# 🏅 Leaderboard command
@bot.command()
@in_allowed_channel()
async def leaderboard(ctx, category: str = "score"):
    # Send loading message
    loading_msg = await ctx.send(embed=create_embed(f"{EMOJIS['leaderboard']} Loading", "Generating leaderboard..."))
    
    records = sheet.get_all_values()
    header = records[0]
    
    # Map category aliases to the actual field names
    category_aliases = {
        "score": "DKP SCORE",
        "goal": "DKP GOAL",
        "rate": "DKP RATE",
        "kills": "BASE T4 KILLS",
        "power": "BASE POWER",
        "dead": "BASE DEAD",
        "kvk": "KVK KILLS | T4 + T5"
    }
    
    # Try to map the category alias first
    search_category = category_aliases.get(category.lower(), category)
    
    # Find the column index for the specified category
    column_index = -1
    category_name = ""
    
    # Look for exact match first
    for i, field in enumerate(header):
        if search_category.upper() == field.upper():
            column_index = i
            category_name = field
            break
    
    # If no exact match, look for partial match
    if column_index == -1:
        for i, field in enumerate(header):
            if search_category.upper() in field.upper():
                column_index = i
                category_name = field
                break
    
    # Default to DKP SCORE if category not found
    if column_index == -1:
        for i, field in enumerate(header):
            if "DKP SCORE" in field:
                column_index = i
                category_name = field
                break
    
    if column_index == -1:
        await loading_msg.delete()
        await ctx.send(embed=create_embed(
            f"{EMOJIS['error']} Invalid Category",
            "Could not find the specified category. Try using 'dkp' for the default leaderboard.",
            COLORS["error"]
        ))
        return
    
    # Extract data and sort
    leaderboard_data = []
    for row in records[1:]:  # Skip header
        if len(row) > column_index:
            try:
                # Get the raw value
                raw_value = row[column_index].strip()
                
                # Skip empty values
                if not raw_value:
                    continue
                
                # Handle percentage values
                if "%" in raw_value:
                    value = int(raw_value.replace("%", ""))
                # Handle K/M notation (convert to actual numbers)
                elif "M" in raw_value:
                    value = int(float(raw_value.replace(",", "").replace("M", "")) * 1000000)
                elif "K" in raw_value:
                    value = int(float(raw_value.replace(",", "").replace("K", "")) * 1000)
                # Handle normal numbers with commas
                else:
                    value = int(raw_value.replace(",", ""))
                
                # Only include entries with a value and name
                if value > 0 and len(row) > 1 and row[1].strip():
                    leaderboard_data.append({
                        "id": row[0] if row[0] else "N/A",
                        "name": row[1],
                        "value": value,
                        "raw_value": raw_value,  # Keep the original formatted value
                        "discord_id": row[2] if len(row) > 2 else None
                    })
            except (ValueError, TypeError):
                # Skip entries that can't be converted to integers
                pass
    
    # Sort by value (descending)
    leaderboard_data.sort(key=lambda x: x["value"], reverse=True)
    
    # Limit to top 10
    top_entries = leaderboard_data[:10]
    
    if not top_entries:
        await loading_msg.delete()
        await ctx.send(embed=create_embed(
            f"{EMOJIS['error']} No Data",
            f"No valid data found for the '{category_name}' category.",
            COLORS["error"]
        ))
        return
    
    # Create the embed
    embed = discord.Embed(
        title=f"{EMOJIS['leaderboard']} {category_name} Leaderboard",
        description=f"Top players ranked by {category_name}",
        color=COLORS["primary"]
    )
    
    # Add leaderboard entries
    for i, entry in enumerate(top_entries):
        # Add medal emoji for top 3
        if i == 0:
            rank_emoji = "🥇"
        elif i == 1:
            rank_emoji = "🥈"
        elif i == 2:
            rank_emoji = "🥉"
        else:
            rank_emoji = f"#{i+1}"
        
        # Use the original formatted value from the sheet
        formatted_value = entry["raw_value"]
        
        # Check if this is the current user
        discord_user = f"{ctx.author.name}#{ctx.author.discriminator}" if hasattr(ctx.author, 'discriminator') else ctx.author.name
        is_current_user = entry["discord_id"] == discord_user
        
        # Highlight current user with an indicator
        name_display = f"**{entry['name']}**" if is_current_user else entry['name']
        
        # Add to embed
        embed.add_field(
            name=f"{rank_emoji} {name_display}",
            value=f"**{category_name}:** {formatted_value}\n**ID:** {entry['id']}",
            inline=False
        )
    
    # Add timestamp
    embed.timestamp = datetime.datetime.now()
    embed.set_footer(text="Updated after every Major War")
    
    await loading_msg.delete()
    await ctx.send(embed=embed)

# ⚔️ Compare stats with another user
@bot.command()
@in_allowed_channel()
async def compare(ctx, member: discord.Member):
    if member == ctx.author:
        await ctx.send(embed=create_embed(
            f"{EMOJIS['error']} Error",
            "You cannot compare with yourself!",
            COLORS["error"]
        ))
        return
    
    # Send loading message
    loading_msg = await ctx.send(embed=create_embed(f"{EMOJIS['compare']} Loading", "Comparing stats..."))
    
    # Get Discord user identifiers
    user1_discord = f"{ctx.author.name}#{ctx.author.discriminator}" if hasattr(ctx.author, 'discriminator') else ctx.author.name
    user2_discord = f"{member.name}#{member.discriminator}" if hasattr(member, 'discriminator') else member.name
    
    records = sheet.get_all_values()
    header = records[0]
    
    # Find both users
    user1_row = None
    user2_row = None
    
    # Get the column indices for important fields
    dkp_score_index = -1
    dkp_goal_index = -1
    dkp_rate_index = -1
    
    # Find the indices of DKP fields
    for i, field in enumerate(header):
        if "DKP SCORE" in field:
            dkp_score_index = i
        elif "DKP GOAL" in field:
            dkp_goal_index = i
        elif "DKP RATE" in field:
            dkp_rate_index = i
    
    for row in records[1:]:
        if len(row) > 2:
            if row[2] == user1_discord:
                user1_row = row
            elif row[2] == user2_discord:
                user2_row = row
    
    # Check if both users are linked
    if not user1_row:
        await loading_msg.delete()
        await ctx.send(embed=create_embed(
            f"{EMOJIS['error']} Not Linked",
            "You are not linked to any ID. Use $linkme <ID> first.",
            COLORS["error"]
        ))
        return
    
    if not user2_row:
        await loading_msg.delete()
        await ctx.send(embed=create_embed(
            f"{EMOJIS['error']} Not Linked",
            f"{member.mention} is not linked to any ID.",
            COLORS["error"]
        ))
        return
    
    # Get user names
    user1_name = user1_row[1] if len(user1_row) > 1 else "Unknown"
    user2_name = user2_row[1] if len(user2_row) > 1 else "Unknown"
    
    # Create comparison embed
    embed = discord.Embed(
        title=f"{EMOJIS['compare']} Stat Comparison",
        description=f"Comparing stats between **{user1_name}** and **{user2_name}**",
        color=COLORS["primary"]
    )
    
    # Find comparable numeric fields
    comparable_fields = []
    
    for i, field in enumerate(header):
        # Skip non-stat fields
        if field in ["ID", "IN-GAME NAME", "Discord ID"]:
            continue
        
        # Check if both users have this field and it's numeric
        if (i < len(user1_row) and i < len(user2_row) and
            user1_row[i] and user2_row[i]):
            try:
                value1 = int(user1_row[i].replace(",", ""))
                value2 = int(user2_row[i].replace(",", ""))
                comparable_fields.append((field, i, value1, value2))
            except (ValueError, TypeError):
                # Skip non-numeric fields
                pass
    
    # Group fields into categories
    dkp_fields = []
    other_fields = []
    
    # Categorize fields
    for field_info in comparable_fields:
        field_name, index, value1, value2 = field_info
        if "DKP" in field_name:
            dkp_fields.append(field_info)
        else:
            other_fields.append(field_info)
    
    # Process DKP fields first if available
    if dkp_fields:
        dkp_comparison = ""
        for field_name, index, value1, value2 in dkp_fields:
            # Determine who has the advantage
            diff = value1 - value2
            if diff > 0:
                emoji = "📈"
                advantage = f"(+{format_number(diff)})"
            elif diff < 0:
                emoji = "📉"
                advantage = f"({format_number(diff)})"
            else:
                emoji = "⏹️"
                advantage = "(=)"
            
            dkp_comparison += f"**{field_name}:** {format_number(value1)} {emoji} {format_number(value2)} {advantage}\n"
        
        embed.add_field(
            name=f"{EMOJIS['dkp']} DKP Comparison",
            value=dkp_comparison or "No comparable DKP stats found.",
            inline=False
        )
    
    # Process other fields
    if other_fields:
        other_comparison = ""
        for field_name, index, value1, value2 in other_fields:
            # Determine who has the advantage
            diff = value1 - value2
            if diff > 0:
                emoji = "📈"
                advantage = f"(+{format_number(diff)})"
            elif diff < 0:
                emoji = "📉"
                advantage = f"({format_number(diff)})"
            else:
                emoji = "⏹️"
                advantage = "(=)"
            
            other_comparison += f"**{field_name}:** {format_number(value1)} {emoji} {format_number(value2)} {advantage}\n"
        
        embed.add_field(
            name=f"{EMOJIS['stats']} Other Stats Comparison",
            value=other_comparison or "No other comparable stats found.",
            inline=False
        )
    
    embed.add_field(
        name="Legend",
        value=f"{ctx.author.display_name} {EMOJIS['compare']} {member.display_name}",
        inline=False
    )
    
    embed.timestamp = datetime.datetime.now()
    
    # Add user avatars
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    
    # Create chart for visual comparison
    if dkp_fields:
        # Create comparison chart
        plt.figure(figsize=(10, 6))
        
        # Extract names and values for chart
        chart_labels = [field[0] for field in dkp_fields]
        user1_values = [field[2] for field in dkp_fields]
        user2_values = [field[3] for field in dkp_fields]
        
        # Set bar width and positions
        bar_width = 0.35
        x = range(len(chart_labels))
        
        # Plot bars
        plt.bar([i - bar_width/2 for i in x], user1_values, bar_width, label=user1_name, color='royalblue', alpha=0.8)
        plt.bar([i + bar_width/2 for i in x], user2_values, bar_width, label=user2_name, color='crimson', alpha=0.8)
        
        # Customize chart
        plt.ylabel('Value')
        plt.title('DKP Comparison')
        plt.xticks(x, chart_labels, rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save chart to a buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        plt.close()
        
        # Create file object
        chart_file = discord.File(buffer, filename="comparison_chart.png")
        
        # Delete loading message
        await loading_msg.delete()
        
        # Send comparison with chart
        embed.set_image(url="attachment://comparison_chart.png")
        await ctx.send(file=chart_file, embed=embed)
    else:
        # Delete loading message
        await loading_msg.delete()
        
        # Send comparison without chart
        await ctx.send(embed=embed)

# 💡 Debug Command
@bot.command()
@in_allowed_channel()
async def debug(ctx):
    """Command to debug sheet structure and column positions"""
    # Send loading message
    loading_msg = await ctx.send(embed=create_embed("Debugging", "Analyzing sheet structure..."))
    
    records = sheet.get_all_values()
    header = records[0]  # Get header row
    
    # Find matching user
    discord_user = f"{ctx.author.name}#{ctx.author.discriminator}" if hasattr(ctx.author, 'discriminator') else ctx.author.name
    user_row = None
    
    for row in records[1:]:
        if len(row) > 2 and row[2] == discord_user:
            user_row = row
            break
    
    if not user_row:
        await loading_msg.delete()
        await ctx.send(embed=create_embed("Debug Error", "User not found in sheet"))
        return
    
    # Create debug message
    debug_text = "**Sheet Structure:**\n"
    
    # Show header with column letters
    header_text = ""
    for i, field in enumerate(header):
        if field:  # Only include non-empty fields
            col_letter = chr(65 + i) if i < 26 else chr(64 + (i // 26)) + chr(65 + (i % 26))
            header_text += f"Column {col_letter} ({i}): '{field}'\n"
    
    debug_text += header_text
    
    # Show DKP values for current user
    debug_text += "\n**Your DKP Values:**\n"
    
    # Check all potential DKP fields
    for i, field in enumerate(header):
        if "DKP" in field.upper():
            if i < len(user_row):
                debug_text += f"{field}: '{user_row[i]}'\n"
            else:
                debug_text += f"{field}: Out of range\n"
    
    # Additional debug info
    debug_text += f"\n**Row Length:** {len(user_row)}\n"
    debug_text += f"**Discord ID method:** {ctx.author.name}#{ctx.author.discriminator if hasattr(ctx.author, 'discriminator') else ''}"
    
    # Send debug info
    await loading_msg.delete()
    
    # Split into multiple messages if too long
    if len(debug_text) > 1900:
        parts = [debug_text[i:i+1900] for i in range(0, len(debug_text), 1900)]
        for i, part in enumerate(parts):
            await ctx.send(embed=create_embed(f"Debug Info (Part {i+1}/{len(parts)})", part))
    else:
        await ctx.send(embed=create_embed("Debug Info", debug_text))

# 💡 Help Command
@bot.command()
@in_allowed_channel()
async def how(ctx):
    embed = discord.Embed(title=f"{EMOJIS['help']} Bot Commands", description="Here are the available commands:", color=COLORS["primary"])
    
    # Account commands
    embed.add_field(
        name="Account Management",
        value=(
            f"{COMMAND_PREFIX}linkme <ID> - Links your Discord account to an ID\n"
            f"{COMMAND_PREFIX}unlink - Unlinks your Discord account from the current ID"
        ),
        inline=False
    )
    
    # Stats commands
    embed.add_field(
        name="Statistics",
        value=(
            f"{COMMAND_PREFIX}stats [user] - Shows your stats or another user's stats\n"
            f"{COMMAND_PREFIX}leaderboard [category] - Shows top players by category\n"
            f"{COMMAND_PREFIX}compare <user> - Compares your stats with another user"
        ),
        inline=False
    )
    
    # Leaderboard categories
    embed.add_field(
        name="Leaderboard Categories",
        value=(
            f"{COMMAND_PREFIX}leaderboard score - Players ranked by DKP Score (default)\n"
            f"{COMMAND_PREFIX}leaderboard goal - Players ranked by DKP Goal\n"
            f"{COMMAND_PREFIX}leaderboard rate - Players ranked by DKP completion rate\n"
            f"{COMMAND_PREFIX}leaderboard kills - Players ranked by kill count\n"
            f"{COMMAND_PREFIX}leaderboard power - Players ranked by power\n"
            f"{COMMAND_PREFIX}leaderboard kvk - Players ranked by KVK kills"
        ),
        inline=False
    )
    
    # Help command
    embed.add_field(
        name="Help & Debug",
        value=(
            f"{COMMAND_PREFIX}how - Displays this help message\n"
            f"{COMMAND_PREFIX}debug - Debug sheet structure (troubleshooting)"
        ),
        inline=False
    )
    
    embed.timestamp = datetime.datetime.now()
    
    await ctx.send(embed=embed)

# 🟢 Bot is ready
@bot.event
async def on_ready():
    print(f"✅ Bot is ready! Logged in as {bot.user}")
    print(f"📊 Connected to Google Sheet: {SHEET_ID}")
    print(f"🔧 Command prefix: {COMMAND_PREFIX}")
    print(f"📢 Allowed channel: {ALLOWED_CHANNEL_ID}")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        # Channel restriction error already handled
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=create_embed(
            f"{EMOJIS['error']} Missing Argument", 
            f"Please provide all required arguments. Use {COMMAND_PREFIX}how for help.",
            COLORS["error"]
        ))
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=create_embed(
            f"{EMOJIS['error']} Unknown Command", 
            f"Command not found. Use {COMMAND_PREFIX}how to see available commands.",
            COLORS["error"]
        ))
    else:
        print(f"❌ Error: {error}")
        await ctx.send(embed=create_embed(
            f"{EMOJIS['error']} Error", 
            "An unexpected error occurred. Please try again or contact support.",
            COLORS["error"]
        ))

if __name__ == "__main__":
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        print("Please check your environment variables and credentials.")