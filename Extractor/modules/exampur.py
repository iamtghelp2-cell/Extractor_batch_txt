import os
import json
import logging
from datetime import datetime
from urllib.parse import quote
import pytz
import requests
import cloudscraper

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from Extractor import app
from config import CHANNEL_ID, BOT_TEXT
from Extractor.core.utils import forward_to_log

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def exampur_txt(app: Client, message: Message):
    """Start the Exampur extraction process."""
    try:
        start_time = datetime.now()
        
        # 1. Ask for credentials
        editable = await message.reply_text(
            "🔹 <b>EXAMPUR EXTRACTOR PRO</b> 🔹\n\n"
            "Send login details in this format:\n"
            "1️⃣ <b>ID*Password:</b> <code>Email*Password</code>\n"
            "2️⃣ <b>Token:</b> <code>your_auth_token</code>\n\n"
            "<i>Example:</i>\n"
            "- ID*Pass: <code>user@mail.com*pass123</code>\n"
            "- Token: <code>eyJhbGciOiJ...</code>"
        )

        input1 = await app.listen(chat_id=message.chat.id)
        await forward_to_log(input1, "Exampur Extractor")
        raw_text = input1.text.strip()
        await input1.delete()

        # Setup initial headers
        rwa_url = "https://auth.exampurcache.xyz/auth/login"
        hdr = {
            "appauthtoken": "no_token",
            "User-Agent": "Dart/2.15(dart:io)",
            "Content-Type": "application/json; charset=UTF-8",
            "Accept-Encoding": "gzip"
        }

        token = None

        # Process login
        try:
            if '*' in raw_text:
                email, password = raw_text.split("*", 1)
                info = {
                    "phone_ext": "91",
                    "phone": "",
                    "email": email.strip(),
                    "password": password.strip()
                }

                scraper = cloudscraper.create_scraper()
                res = scraper.post(rwa_url, json=info, headers=hdr, timeout=30)
                
                if res.status_code != 200:
                    await editable.edit_text(
                        f"❌ <b>Login Failed (HTTP {res.status_code})</b>\n\n"
                        "कृपया अपनी ईमेल और पासवर्ड चेक करें।"
                    )
                    return

                output = res.json()
                if 'data' not in output or 'authToken' not in output['data']:
                    await editable.edit_text(
                        "❌ <b>Login Failed</b>\n\n"
                        "सर्वर से ऑथेंटिकेशन टोकन नहीं मिला।"
                    )
                    return

                token = output["data"]["authToken"]
            else:
                token = raw_text

            # Headers for authenticated requests
            hdr1 = {
                "appauthtoken": token,
                "User-Agent": "Dart/2.15(dart:io)",
                "Accept-Encoding": "gzip"
            }

        except Exception as e:
            logger.error(f"Login error: {e}")
            await editable.edit_text(
                "❌ <b>Login Failed</b>\n\n"
                f"Error: <code>{str(e)}</code>"
            )
            return

        # 2. Fetch courses
        try:
            res1 = requests.get("https://auth.exampurcache.xyz/mycourses", headers=hdr1, timeout=30)
            if res1.status_code != 200:
                await editable.edit_text(
                    "❌ <b>Failed to fetch courses</b>\n\n"
                    "टोकन एक्सपायर हो गया है या कोर्स लिस्ट लोड नहीं हुई।"
                )
                return

            courses_data = res1.json().get('data', [])
            if not courses_data:
                await editable.edit_text(
                    "❌ <b>No Batches Found</b>\n\n"
                    "आपके अकाउंट में कोई बैच उपलब्ध नहीं है।"
                )
                return

            # Format batches text
            batch_text = ""
            for course in courses_data:
                batch_text += f"<code>{course.get('_id', '')}</code> - <b>{course.get('title', 'Unknown')}</b> 💰\n\n"

            await editable.edit_text(
                f"✅ <b>Login Successful!</b>\n\n"
                f"📚 <b>Available Batches:</b>\n\n{batch_text}"
            )
        except Exception as e:
            logger.error(f"Course fetch error: {e}")
            await editable.edit_text(f"❌ <b>Failed to fetch courses:</b>\n<code>{str(e)}</code>")
            return

        # 3. Ask for Batch ID
        try:
            input2 = await app.ask(
                message.chat.id,
                "<b>📥 Send the Batch ID to download</b>"
            )
            batch_id = input2.text.strip()
            await input2.delete()

            progress_msg = await message.reply_text(
                "🔄 <b>Processing Batch</b>\n"
                f"└─ Initializing batch: <code>{batch_id}</code>"
            )

            # Fetch subjects/topics
            scraper = cloudscraper.create_scraper()
            res_subj = scraper.get(f"https://auth.exampurcache.xyz/course_subject/{batch_id}", headers=hdr1, timeout=30)
            output0 = res_subj.json()

            if 'data' not in output0 or not output0["data"]:
                await progress_msg.edit_text("❌ <b>Invalid batch ID or no subjects found!</b>")
                return

            subjID = output0["data"]
            topic_ids = [str(item["_id"]) for item in subjID if "_id" in item]
            topic_ids_str = "&".join(topic_ids)

            # 4. Ask for topic selection
            input4 = await app.ask(
                message.chat.id,
                "<b>📥 Select Topics to Download</b>\n\n"
                f"<b>💡 For ALL topics:</b> <code>{topic_ids_str}</code>\n\n"
                "<i>Separate multiple IDs with '&' (e.g. 1&2&3)</i>"
            )
            selected_topics = input4.text.strip().split('&')
            await input4.delete()

        except Exception as e:
            logger.error(f"Batch selection error: {e}")
            await message.reply_text(f"❌ <b>Error selecting batch:</b>\n<code>{str(e)}</code>")
            return

        # 5. Process chapters and materials
        try:
            all_urls = []
            processed = 0
            total_topics = len(selected_topics)

            for topic_id in selected_topics:
                topic_id = topic_id.strip()
                if not topic_id:
                    continue

                await progress_msg.edit_text(
                    "🔄 <b>Processing Large Batch</b>\n"
                    f"├─ Progress: {processed}/{total_topics} topics\n"
                    f"├─ Current Topic: <code>{topic_id}</code>\n"
                    f"└─ Links found: {len(all_urls)}"
                )

                # Fetch chapters under this topic
                res4 = requests.get(
                    f"https://auth.exampurcache.xyz/course_material/chapter/{topic_id}/{batch_id}",
                    headers=hdr1,
                    timeout=30
                )
                if res4.status_code != 200:
                    processed += 1
                    continue

                chapters = res4.json().get('data', [])
                for chapter in chapters:
                    # Safe URL encode for chapter names containing spaces or symbols
                    safe_chapter = quote(str(chapter))
                    res5 = requests.get(
                        f"https://auth.exampurcache.xyz/course_material/material/{topic_id}/{batch_id}/{safe_chapter}",
                        headers=hdr1,
                        timeout=30
                    )
                    if res5.status_code != 200:
                        continue

                    materials = res5.json().get('data', [])
                    for material in materials:
                        title = material.get('title', '').strip()
                        url = material.get('video_link', '').strip()
                        if url:
                            all_urls.append(f"{title}: {url}")

                processed += 1

            if not all_urls:
                await progress_msg.edit_text("❌ <b>No content found in selected topics</b>")
                return

            # 6. Calculate stats & write file
            end_time = datetime.now()
            duration = end_time - start_time
            minutes, seconds = divmod(duration.total_seconds(), 60)

            video_count = sum(1 for url in all_urls if any(ext in url.lower() for ext in ['.mp4', '.m3u8', '.mpd', 'youtu']))
            pdf_count = sum(1 for url in all_urls if '.pdf' in url.lower())
            doc_count = sum(1 for url in all_urls if any(ext in url.lower() for ext in ['.doc', '.docx', '.ppt', '.pptx']))
            drm_count = sum(1 for url in all_urls if '.mpd' in url.lower())

            file_name = f"Exampur_{batch_id}_{int(start_time.timestamp())}.txt"
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write('\n'.join(all_urls))

            # Caption preparation
            caption = (
                f"🎓 <b>COURSE EXTRACTED</b> 🎓\n\n"
                f"📱 <b>APP:</b> Exampur\n"
                f"📚 <b>BATCH ID:</b> {batch_id}\n"
                f"⏱ <b>EXTRACTION TIME:</b> {int(minutes):02d}:{int(seconds):02d}\n"
                f"📅 <b>DATE:</b> {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y %H:%M:%S')} IST\n\n"
                f"📊 <b>CONTENT STATS</b>\n"
                f"├─ 📁 Total Links: {len(all_urls)}\n"
                f"├─ 🎬 Videos: {video_count}\n"
                f"├─ 📄 PDFs: {pdf_count}\n"
                f"├─ 📑 Documents: {doc_count}\n"
                f"└─ 🔐 Protected: {drm_count}\n\n"
                f"🚀 <b>Extracted by:</b> @{(await app.get_me()).username}\n\n"
                f"<code>╾───• {BOT_TEXT} •───╼</code>"
            )

            # Send document to user and channel
            await message.reply_document(
                document=file_name,
                caption=caption,
                parse_mode=ParseMode.HTML
            )
            if CHANNEL_ID:
                try:
                    await app.send_document(CHANNEL_ID, document=file_name, caption=caption, parse_mode=ParseMode.HTML)
                except Exception as ce:
                    logger.warning(f"Failed to send to channel: {ce}")

            # Cleanup
            if os.path.exists(file_name):
                os.remove(file_name)

            await progress_msg.edit_text(
                "✅ <b>Extraction completed successfully!</b>\n\n"
                f"📊 <b>Final Status:</b>\n"
                f"📚 Processed: {total_topics} topics\n"
                f"🔗 Links Found: {len(all_urls)}\n"
                f"📤 File has been uploaded\n\n"
                f"Thank you for using Exampur Extractor! 🌟"
            )

        except Exception as e:
            logger.error(f"Processing error: {e}")
            await message.reply_text(f"❌ <b>Failed to process topics:</b>\n<code>{str(e)}</code>")

    except Exception as e:
        logger.error(f"Fatal error in exampur_txt: {e}")
        await message.reply_text(f"❌ <b>An error occurred:</b>\n<code>{str(e)}</code>")
        
