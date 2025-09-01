import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Channel IDs
ORDER_CHANNEL_ID = 1411007920744960081      # staff-orders private
DB_CHANNEL_ID = 1398666241832648815         # database-log private

# Slash command setup
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    print(f"✅ Bot is online as {bot.user}")

# /order command
@bot.tree.command(name="order", description="Place a new coffee order")
@app_commands.describe(
    table="What's your table number?",
    details="What do you want to order?"
)
async def order(interaction: discord.Interaction, table: str, details: str):
    # Confirm to customer (ephemeral)
    await interaction.response.send_message(
        "✅ شكرا! طلبك تحت التحضير. خليك ديما فاتح DM 💌", ephemeral=True
    )

    # Send order to private staff channel (NO auto reaction added)
    staff_channel = bot.get_channel(ORDER_CHANNEL_ID)
    await staff_channel.send(
        f"""📥 طلب جديد
🪑 Table: {table}
🍩 {details}
🙋 {interaction.user.mention}"""
    )

    # Log the order
    db_channel = bot.get_channel(DB_CHANNEL_ID)
    await db_channel.send(
        f"📄 تم تسجيل الطلب من {interaction.user.name} ✔️"
    )

# Detect ✅ reaction by staff (done manually)
@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.emoji.name) != "✅":
        return

    if payload.channel_id != ORDER_CHANNEL_ID:
        return

    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    # Get original customer from message content
    lines = message.content.split('\n')
    customer_line = next((l for l in lines if l.startswith("🙋")), None)
    if customer_line:
        user_mention = customer_line.split(' ')[1]
        user_id = int(user_mention.strip('<@!>'))
        user = await bot.fetch_user(user_id)

        # Send DM to let them know the order is ready
        try:
            await user.send("☕ طلبك جاهز! تجم تجي تاخذو ✨")
        except:
            print(f"⚠️ Couldn't send ready DM to {user.name}")

        # Optional: log the completion
        db_channel = bot.get_channel(DB_CHANNEL_ID)
        await db_channel.send(
            f"✅ تم تجهيز الطلب الخاص بـ {user.name}"
        )

# Start keep_alive (optional for fallback)
keep_alive()

import os

token = os.environ.get("TOKEN")
if token:
    bot.run(token)
else:
    print("❌ TOKEN not found in environment variables!")
