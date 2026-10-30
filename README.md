# ⚡ IamTgHelp Extractor Bot

Telegram bot (Python + Pyrogram) — branding: **IamTgHelp**.

## Required environment variables
| Name | Description |
|---|---|
| `API_ID`, `API_HASH` | my.telegram.org से |
| `BOT_TOKEN` | @BotFather से |
| `MONGO_URL` | MongoDB connection string |
| `OWNER_ID` | Owner user ID (default `7951185227`) |
| `LOG_GROUP` | Log group ID (default `-1003506524877`) |

Optional: `BRAND_NAME`, `BRAND_USERNAME`, `CHANNEL_ID2` (force-sub चैनल, default `@iamtghelp`, 0 = off), `PAYMENT_QR_URL`, `THUMB_URL`, `CP_FREE_TOKEN`, `START_PHOTO`.
`.env.example` को `.env` नाम से कॉपी करके भर सकते हो।

## Run
**VPS / local**
```bash
pip install -r requirements.txt
cp .env.example .env   # वैल्यू भरो
python -m Extractor
```
**Docker:** `docker build -t iamtghelp-bot . && docker run --env-file .env iamtghelp-bot`
**Heroku / Render / Railway:** env variables सेट करो, `Procfile`/`Dockerfile` इस्तेमाल होगा।

बॉट को LOG_GROUP में admin बनाना ज़रूरी है ताकि लॉग/फ़ाइल जा सकें।

## Private mode (सिर्फ़ तुम्हारे चुने हुए लोग)
डिफ़ॉल्ट रूप से बॉट private है। सिर्फ़ OWNER और allow किए गए यूज़र चला सकते हैं; बाकी को "private bot" मैसेज मिलता है।
- `/allow <user_id>` (या यूज़र के मैसेज पर reply करके `/allow`)
- `/unallow <user_id>`
- `/allowed` – लिस्ट देखो
- `PRIVATE_MODE=false` से सबके लिए खोल सकते हो; `ALLOWED_USERS=id1,id2` से शुरुआती लिस्ट।

## Start photo
`Extractor/thumbs/start.jpg` बदलकर /start की फोटो बदली जा सकती है।

## License
GNU GPL v3 (see `LICENSE`).
