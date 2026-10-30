import os

# .env फ़ाइल (VPS/लोकल) से वैल्यू लोड करो; Heroku/Docker में env पहले से सेट होते हैं
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _int(name, default=0):
    value = os.environ.get(name, "")
    try:
        return int(str(value).strip()) if str(value).strip() else default
    except ValueError:
        return default


# ------------------------------------------------
#  REQUIRED  (अपने environment में डालो)
# ------------------------------------------------
API_ID = _int("API_ID", 0)
API_HASH = os.environ.get("API_HASH", "").strip()
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
MONGO_URL = os.environ.get("MONGO_URL", "").strip()

# ------------------------------------------------
#  BRANDING  –  iamtghelp
# ------------------------------------------------
BRAND_NAME = os.environ.get("BRAND_NAME", "IamTgHelp")
BRAND_USERNAME = os.environ.get("BRAND_USERNAME", "iamtghelp").lstrip("@")   # without @
BRAND_LINK = f"https://t.me/{BRAND_USERNAME}"
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
BOT_TEXT = BRAND_NAME
ADMIN_BOT_USERNAME = os.environ.get("ADMIN_BOT_USERNAME", BRAND_USERNAME).lstrip("@")  # without @
join = f'<a href="{BRAND_LINK}">✳️ JOIN {BRAND_NAME.upper()}</a>'

# ------------------------------------------------
#  OWNER & LOG GROUP
# ------------------------------------------------
OWNER_ID = _int("OWNER_ID", 7951185227,5886149022)
LOG_GROUP = _int("LOG_GROUP", -1003506524877)

# सभी लॉग / फ़ाइल आउटपुट इसी ग्रुप में जाते हैं
CHANNEL_ID = _int("CHANNEL_ID", LOG_GROUP)
PREMIUM_LOGS = _int("PREMIUM_LOGS", LOG_GROUP)

# Force-subscribe चैनल: डिफ़ॉल्ट = @iamtghelp चैनल (बॉट को उस चैनल में admin बनाना ज़रूरी)
# env में CHANNEL_ID2 = -100xxxxxxxxxx या @username डाल सकते हो; 0 = बंद
def _channel(name, default):
    value = os.environ.get(name, "").strip() or str(default)
    if value in ("0", "off", "false", "False", "none", "None"):
        return 0
    try:
        return int(value)
    except ValueError:
        return value if value.startswith("@") else "@" + value

CHANNEL_ID2 = _channel("CHANNEL_ID2", "@" + BRAND_USERNAME)

# ------------------------------------------------
#  PRIVATE MODE – सिर्फ़ OWNER + allowed यूज़र्स
# ------------------------------------------------
PRIVATE_MODE = os.environ.get("PRIVATE_MODE", "true").strip().lower() not in ("0", "false", "off", "no")
# शुरुआती allowed IDs (comma separated), बाकी बॉट में /allow से जोड़ो
ALLOWED_USERS = [int(x) for x in os.environ.get("ALLOWED_USERS", "").replace(" ", "").split(",") if x.lstrip("-").isdigit()]

# ------------------------------------------------
#  IMAGES
# ------------------------------------------------
# /start पर दिखने वाली फोटो (लोकल फ़ाइल)
START_PHOTO = os.environ.get("START_PHOTO", os.path.join(BASE_DIR, "Extractor", "thumbs", "start.jpg"))

# प्रीमियम पेमेंट QR की इमेज का लिंक (खाली = QR नहीं दिखेगा)
PAYMENT_QR_URL = os.environ.get("PAYMENT_QR_URL", "").strip()

# txt फ़ाइलों पर लगाने वाला वैकल्पिक थंबनेल (URL). खाली = कोई कस्टम थंबनेल नहीं
THUMB_URL = os.environ.get("THUMB_URL", "").strip()

# Classplus "without login" फ़्लो के लिए वैकल्पिक टोकन
CP_FREE_TOKEN = os.environ.get("CP_FREE_TOKEN", "").strip()
