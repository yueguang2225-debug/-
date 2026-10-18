import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Token နှင့် Admin ID များကို ထည့်သွင်းထားပါသည်
TOKEN = "8683026772:AAEJEpIqB0oAMagj9iDP_EmnYkWqc1P5dpM"
ADMIN_ID = 8012437507  

DATA_FILE = "responses.json"
USERS_FILE = "users.json"

# Data သိမ်းဆည်းရန်နှင့် ဖတ်ရန် helper functions
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {} if "responses" in file_path else []

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

responses = load_data(DATA_FILE)
users = load_data(USERS_FILE)

# 1. /start Command (User Count Tracking)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users.append(user_id)
        save_data(USERS_FILE, users)
    await update.message.reply_text("မင်္ဂလာပါ၊ မေးခွန်း Key Word များကို ပို့ပေးပါရန်။")

# 2. !add Command (မေးခွန်း နှင့် အဖြေ သစ် ထည့်သွင်းခြင်း)
async def add_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    text = update.message.text[4:].strip() # '!add ' ကို ဖယ်ထုတ်ခြင်း
    if ":" in text:
        key, answer = text.split(":", 1)
        key = key.strip()
        answer = answer.strip()
        responses[key] = answer
        save_data(DATA_FILE, responses)
        await update.message.reply_text(f"✅ '{key}' မေးခွန်းနှင့် အဖြေကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ!")
    else:
        await update.message.reply_text("ပုံစံ မမှန်ပါ။ ဥပမာ - !add မေးခွန်း : အဖြေ")

# 3. !del / !delete Command (ထည့်ပြီးသား အချက်အလက် ဖျက်ခြင်း)
async def delete_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    key = update.message.text.replace("!del", "").replace("!delete", "").strip()
    if key in responses:
        del responses[key]
        save_data(DATA_FILE, responses)
        await update.message.reply_text(f"🗑️ '{key}' ကို မေးခွန်းစာရင်းမှ ဖျက်ပြီးပါပြီ။")
    else:
        await update.message.reply_text("⚠️ အဆိုပါ မေးခွန်းစာရင်းကို ရှာမတွေ့ပါ။")

# 4. /list Command (သိမ်းဆည်းထားသော မေးခွန်းများ စာရင်းပြခြင်း)
async def list_responses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not responses:
        await update.message.reply_text("📋 သိမ်းဆည်းထားသော မေးခွန်းများ မရှိသေးပါ။")
        return
    
    msg = "📋 **သိမ်းဆည်းထားသော မေးခွန်းများစာရင်း:**\n\n"
    for idx, key in enumerate(responses.keys(), 1):
        msg += f"{idx}. {key}\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# 5. /stats Command (အသုံးပြုသူ စုစုပေါင်း ပြခြင်း)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📊 လက်ရှိ Bot အသုံးပြုနေသူ စုစုပေါင်း: {len(users)} ဦး ရှိပါသည်။")

# 6. Auto-Reply Handler (အလိုအလျောက် စာပြန်ပေးခြင်း)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    if user_text in responses:
        await update.message.reply_text(responses[user_text])

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_responses))
    app.add_handler(CommandHandler("stats", stats))
    
    app.add_handler(MessageHandler(filters.Regex(r"^!add"), add_response))
    app.add_handler(MessageHandler(filters.Regex(r"^!(del|delete)"), delete_response))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
