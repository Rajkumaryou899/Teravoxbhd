from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import TERABOX_USERNAME, TERABOX_PASSWORD
import subprocess

API_ID = 24057026  # Your API ID
API_HASH = "f9247ca212b28b03bf70a74cbf4b33c4"  # Your API HASH
BOT_TOKEN = "7919305104:AAEXivRr4lqCj0YUjBsNXHbLB_I_nTa1oc4"  # Your BOT TOKEN

REQUIRED_CHANNELS = ["Ashlynn_Repository", "Ashlynn_RepositoryBot"]
PREMIUM_USERS = set()

bot = Client("terabox_premium_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def is_user_joined(client, user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True

@bot.on_message(filters.command("start"))
async def start(client, message: Message):
    buttons = [
        [InlineKeyboardButton(f"Join {ch}", url=f"https://t.me/{ch}")]
        for ch in REQUIRED_CHANNELS
    ]
    buttons.append([InlineKeyboardButton("🔄 Check Again", callback_data="check_again")])
    await message.reply(
        "**⚠️ Channel Membership Required**\n\nPlease join all channels below to use this bot:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@bot.on_callback_query(filters.regex("check_again"))
async def check_again(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if await is_user_joined(client, user_id):
        PREMIUM_USERS.add(user_id)
        await callback_query.message.edit_text(
            "✅ **Thanks for joining!**\n\n🎉 Terabox Premium Subscription Enabled.\n📦 Account: `premium_user_001`"
        )
    else:
        await callback_query.answer("❌ Please join all channels first!", show_alert=True)

@bot.on_message(filters.text & ~filters.command("start"))
async def handle_link(client, message: Message):
    user_id = message.from_user.id
    link = message.text.strip()

    if user_id not in PREMIUM_USERS:
        if await is_user_joined(client, user_id):
            PREMIUM_USERS.add(user_id)
            await message.reply("✅ Premium Enabled.\nSend your Terabox link.")
        else:
            await message.reply("❌ Please join all required channels first and press 🔄 Check Again.")
            return

    if "terabox" in link:
        await message.reply("⏬ Downloading your video using premium account...")

        try:
            result = subprocess.run(
                ["python", "download_terabox.py", link, TERABOX_USERNAME, TERABOX_PASSWORD],
                capture_output=True,
                text=True
            )
            output = result.stdout or result.stderr
            await message.reply(f"✅ Done!\n\n```\n{output}\n```")
        except Exception as e:
            await message.reply(f"❌ Error downloading: {e}")
    else:
        await message.reply("❌ Invalid Terabox link. Please send a proper link.")

bot.run()
