"""
Private-mode access control.
सिर्फ़ OWNER और owner द्वारा allow किए गए यूज़र ही बॉट इस्तेमाल कर सकते हैं।

Owner commands:
  /allow <user_id>      (या किसी के मैसेज पर reply करके /allow)
  /unallow <user_id>    (या reply करके)
  /allowed              allowed यूज़र्स की लिस्ट
"""
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from motor.motor_asyncio import AsyncIOMotorClient

from Extractor import app
from config import MONGO_URL, OWNER_ID, PRIVATE_MODE, ALLOWED_USERS, BRAND_USERNAME

_col = AsyncIOMotorClient(MONGO_URL).access.allowed_users
_cache = None  # set of allowed user ids (loaded lazily)

DENY_TEXT = (
    "🔒 <b>This is a private bot.</b>\n\n"
    f"Access is only for approved users. Contact @{BRAND_USERNAME} to get access."
)


async def _load():
    global _cache
    if _cache is None:
        ids = set(ALLOWED_USERS)
        try:
            async for d in _col.find():
                ids.add(int(d["_id"]))
        except Exception as e:
            print(f"[access] DB load error: {e}")
        _cache = ids
    return _cache


async def is_allowed(user_id: int) -> bool:
    if not PRIVATE_MODE or user_id == OWNER_ID:
        return True
    return user_id in await _load()


async def add_allowed(user_id: int):
    ids = await _load()
    ids.add(user_id)
    await _col.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)


async def remove_allowed(user_id: int):
    ids = await _load()
    ids.discard(user_id)
    await _col.delete_one({"_id": user_id})


# ---------------- gate: सबसे पहले चलता है (group -100) ---------------- #

@app.on_message(filters.incoming, group=-100)
async def gate_messages(client, message: Message):
    user = message.from_user
    if user and await is_allowed(user.id):
        return
    if message.chat and message.chat.type.name == "PRIVATE":
        try:
            await message.reply_text(DENY_TEXT)
        except Exception:
            pass
    message.stop_propagation()


@app.on_callback_query(group=-100)
async def gate_callbacks(client, query: CallbackQuery):
    if await is_allowed(query.from_user.id):
        return
    try:
        await query.answer("🔒 Private bot – access not granted.", show_alert=True)
    except Exception:
        pass
    query.stop_propagation()


# ---------------- owner commands ---------------- #

def _target(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id
    if len(message.command) > 1:
        try:
            return int(message.command[1])
        except ValueError:
            return None
    return None


@app.on_message(filters.command("allow") & filters.user(OWNER_ID))
async def allow_cmd(client, message: Message):
    uid = _target(message)
    if not uid:
        return await message.reply_text("Usage: <code>/allow user_id</code> (या किसी के मैसेज पर reply करो)")
    await add_allowed(uid)
    await message.reply_text(f"✅ <code>{uid}</code> को access दे दिया।")


@app.on_message(filters.command("unallow") & filters.user(OWNER_ID))
async def unallow_cmd(client, message: Message):
    uid = _target(message)
    if not uid:
        return await message.reply_text("Usage: <code>/unallow user_id</code> (या reply करो)")
    await remove_allowed(uid)
    await message.reply_text(f"🚫 <code>{uid}</code> का access हटा दिया।")


@app.on_message(filters.command("allowed") & filters.user(OWNER_ID))
async def allowed_cmd(client, message: Message):
    ids = sorted(await _load())
    if not ids:
        return await message.reply_text("कोई allowed यूज़र नहीं है। /allow user_id से जोड़ो।")
    text = "👥 <b>Allowed users:</b>\n\n" + "\n".join(f"• <code>{i}</code>" for i in ids)
    await message.reply_text(text)
