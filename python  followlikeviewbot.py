import os
import json
import time
import html
import logging
import telebot
from telebot import types

BOT_TOKEN = "8880587091:AAGsXm2CjBAj-BlMbQpM6fNde1_AA0CgHDA"
ADMIN_CHAT_ID = 8434665762
PAYMENT_NUMBER = "01953192653"
DATA_FILE = "users_wallet.json"
ONLINE_SHOP_URL = "https://your-online-shop-link.com"

logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

SMM_PACKAGES = {
    "tg_view": {"name": "👁️ Telegram Views (1K)", "price": 3.0, "min_qty": 1000, "platform": "TELEGRAM", "desc": "ভিউ সংখ্যা (Life Time)"},
    "tg_react": {"name": "❤️ Telegram Reacts + Views (1K)", "price": 15.0, "min_qty": 500, "platform": "TELEGRAM", "desc": "আগুন সার্ভিস"},
    "tg_member": {"name": "👥 Telegram Members (1K)", "price": 20.0, "min_qty": 500, "platform": "TELEGRAM", "desc": "গ্রুপ বা চ্যানেল মেম্বার"},
    
    "fb_view": {"name": "🎥 Facebook Video Views (1K)", "price": 12.0, "min_qty": 1000, "platform": "FACEBOOK", "desc": "ভিডিও ভিউজ"},
    "fb_follower": {"name": "👤 Facebook Followers (1K)", "price": 99.0, "min_qty": 500, "platform": "FACEBOOK", "desc": "ফলোয়ার/পেইজ লাইক"},
    "fb_reaction": {"name": "😍 Facebook Reactions (1K)", "price": 35.0, "min_qty": 500, "platform": "FACEBOOK", "desc": "পোস্ট রিঅ্যাকশন"},
    
    "insta_view": {"name": "👁️ Instagram Views (1K)", "price": 3.0, "min_qty": 1000, "platform": "INSTAGRAM", "desc": "রিলস ভিউ"},
    "insta_like": {"name": "❤️ Instagram Likes (1K)", "price": 30.0, "min_qty": 500, "platform": "INSTAGRAM", "desc": "পোস্ট লাইক"},
    "insta_follower": {"name": "⭐ Instagram Followers (1K)", "price": 45.0, "min_qty": 500, "platform": "INSTAGRAM", "desc": "ফলোয়ার সার্ভিস"},
    
    "tiktok_view": {"name": "👁️ TikTok Views (1K)", "price": 5.0, "min_qty": 1000, "platform": "TIKTOK", "desc": "টিকটক ভিডিও ভিউ"},
    "tiktok_like": {"name": "👍 TikTok Likes (1K)", "price": 15.0, "min_qty": 500, "platform": "TIKTOK", "desc": "লাইক সার্ভিস"},
    "tiktok_follower": {"name": "⭐ TikTok Followers (1K)", "price": 179.0, "min_qty": 500, "platform": "TIKTOK", "desc": "ফলোয়ার সার্ভিস"},
    
    "yt_like": {"name": "👍 YouTube Likes (1K)", "price": 35.0, "min_qty": 500, "platform": "YOUTUBE", "desc": "ইউটিউব লাইক"},
    "yt_sub": {"name": "🔔 YouTube Subscribers (1K)", "price": 45.0, "min_qty": 500, "platform": "YOUTUBE", "desc": "সাবস্ক্রাইবার"},
    "yt_view": {"name": "▶️ YouTube Views (1K)", "price": 25.0, "min_qty": 1000, "platform": "YOUTUBE", "desc": "ভিডিও ভিউস"}
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    data.setdefault("users", {})
                    data.setdefault("pending", {})
                    data.setdefault("sessions", {})
                    data.setdefault("social_orders", {})
                    return data
        except Exception:
            pass
    return {"users": {}, "pending": {}, "sessions": {}, "social_orders": {}}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def get_user_session(user_id):
    db = load_data()
    return db.get("sessions", {}).get(str(user_id), {})

def set_user_session(user_id, session_data):
    db = load_data()
    db["sessions"][str(user_id)] = session_data
    save_data(db)

def clear_user_session(user_id):
    db = load_data()
    if str(user_id) in db.get("sessions", {}):
        del db["sessions"][str(user_id)]
        save_data(db)

def get_user_balance(user_id):
    db = load_data()
    return float(db.get("users", {}).get(str(user_id), {}).get("balance", 0.0))

def update_user_balance(user_id, amount_change):
    db = load_data()
    u_str = str(user_id)
    if u_str not in db["users"]:
        db["users"][u_str] = {"balance": 0.0}
    curr = float(db["users"][u_str].get("balance", 0.0))
    new_bal = curr + amount_change
    db["users"][u_str]["balance"] = new_bal
    save_data(db)
    return new_bal

def get_main_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🚀 সার্ভিস শপ (বট মেনু)", callback_data="menu_smm_shop"),
        types.InlineKeyboardButton("🌐 অনলাইন শপ (ওয়েবসাইট)", url=ONLINE_SHOP_URL),
        types.InlineKeyboardButton("💳 টাকা যোগ করুন (Deposit)", callback_data="menu_deposit"),
        types.InlineKeyboardButton("💰 আমার ব্যালেন্স", callback_data="menu_balance"),
        types.InlineKeyboardButton("📞 হেল্পলাইন ও সাপোর্ট", callback_data="menu_helpline")
    )
    return markup

def get_deposit_methods_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📱 বিকাশ (bKash Personal)", callback_data="pay_bkash"),
        types.InlineKeyboardButton("🍊 নগদ (Nagad Personal)", callback_data="pay_nagad"),
        types.InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="menu_main")
    )
    return markup

def get_platforms_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔵 Telegram", callback_data="plat_TELEGRAM"),
        types.InlineKeyboardButton("🔷 Facebook", callback_data="plat_FACEBOOK"),
        types.InlineKeyboardButton("🟣 Instagram", callback_data="plat_INSTAGRAM"),
        types.InlineKeyboardButton("⚫ TikTok", callback_data="plat_TIKTOK"),
        types.InlineKeyboardButton("🔴 YouTube", callback_data="plat_YOUTUBE"),
        types.InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="menu_main")
    )
    return markup

def get_main_menu_text(user_name, user_id):
    bal = get_user_balance(user_id)
    return f"<b>👑 অনলাইন শপ বটে স্বাগতম, {html.escape(user_name)}!</b>\n\n🆔 <b>ইউজার ID:</b> <code>{user_id}</code>\n💰 <b>ওয়ালেট ব্যালেন্স:</b> <code>৳ {bal:.2f}</code>\n\n👇 নিচে থেকে আপনার পছন্দের সোশ্যাল মিডিয়া সার্ভিস সিলেক্ট করুন:"

@bot.message_handler(commands=['start'])
def handle_start(message):
    user = message.from_user
    clear_user_session(user.id)
    txt = get_main_menu_text(user.first_name, user.id)
    bot.send_message(message.chat.id, txt, reply_markup=get_main_menu_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user = call.from_user
    
    if call.data == "menu_main":
        clear_user_session(user.id)
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=get_main_menu_text(user.first_name, user.id),
                reply_markup=get_main_menu_keyboard()
            )
        except Exception:
            bot.send_message(call.message.chat.id, get_main_menu_text(user.first_name, user.id), reply_markup=get_main_menu_keyboard())

    elif call.data == "menu_balance":
        bal = get_user_balance(user.id)
        msg = f"<b>💳 আপনার ওয়ালেট ব্যালেন্স</b>\n\n👤 <b>ইউজার:</b> {html.escape(user.first_name)}\n🆔 <b>ইউজার ID:</b> <code>{user.id}</code>\n💰 <b>বর্তমান ব্যালেন্স:</b> <code>৳ {bal:.2f}</code>"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="menu_main"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=markup)

    elif call.data == "menu_helpline":
        msg = "<b>📞 হেল্পলাইন ও সাপোর্ট</b>\n\nযেকোনো সমস্যায় যোগাযোগ করুন:\n👤 <b>অফিশিয়াল সাপোর্ট:</b> @nibir11525"
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("💬 সরাসরি চ্যাট", url="https://t.me/nibir11525"),
            types.InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="menu_main")
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=markup)

    elif call.data == "menu_deposit":
        msg = f"<b>💳 ডিপোজিট সেকশন</b>\n\nসেন্ড মানি করুন:\n📌 <b>নম্বর:</b> <code>{PAYMENT_NUMBER}</code> (bKash/Nagad)"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=get_deposit_methods_keyboard())

    elif call.data == "menu_smm_shop":
        msg = "📲 <b>সোশ্যাল মিডিয়া – প্ল্যাটফর্ম সিলেক্ট করুন</b>"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=get_platforms_keyboard())

    elif call.data.startswith("plat_"):
        platform = call.data.replace("plat_", "")
        markup = types.InlineKeyboardMarkup(row_width=1)
        for pkg_id, pkg in SMM_PACKAGES.items():
            if pkg["platform"] == platform:
                btn_text = f"{pkg['name']} — ৳{pkg['price']:.1f}"
                markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"buy_pkg_{pkg_id}"))
        markup.add(types.InlineKeyboardButton("🔙 প্ল্যাটফর্ম তালিকা", callback_data="menu_smm_shop"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"<b>📂 {platform} সার্ভিসসমূহ:</b>",
            reply_markup=markup
        )

    elif call.data.startswith("buy_pkg_"):
        pkg_id = call.data.replace("buy_pkg_", "")
        if pkg_id in SMM_PACKAGES:
            pkg = SMM_PACKAGES[pkg_id]
            set_user_session(user.id, {"step": "WAIT_QTY", "pkg_id": pkg_id})
            prompt = f"<b>📦 প্যাকেজ: {pkg['name']}</b>\n📉 <b>মিনিমাম পরিমাণ:</b> {pkg['min_qty']}\n\n👉 কত পরিমাণ নিতে চান সংখ্যায় লিখুন:"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=prompt)

    elif call.data in ["pay_bkash", "pay_nagad"]:
        method = "বিকাশ (bKash)" if call.data == "pay_bkash" else "নগদ (Nagad)"
        set_user_session(user.id, {"step": "WAIT_AMOUNT", "method": method})
        prompt = f"<b>💳 {method} পেমেন্ট</b>\n\nকত টাকা ডিপোজিট করতে চান সংখ্যায় লিখুন:"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=prompt)

    elif call.data.startswith("app_") or call.data.startswith("rej_"):
        if user.id != ADMIN_CHAT_ID:
            bot.answer_callback_query(call.id, "❌ আপনি এডমিন নন!", show_alert=True)
            return
        action, req_id = call.data.split("_", 1)
        db = load_data()
        pending = db.get("pending", {})
        if req_id not in pending:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="❌ রিকোয়েস্টটি ইতিমধ্যে প্রসেস করা হয়েছে।")
            return
        req = pending[req_id]
        target_id = req["user_id"]
        amount = float(req["amount"])

        if action == "app":
            u_str = str(target_id)
            db["users"].setdefault(u_str, {"balance": 0.0})
            new_bal = float(db["users"][u_str]["balance"]) + amount
            db["users"][u_str]["balance"] = new_bal
            del db["pending"][req_id]
            save_data(db)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ এপ্রুভ সফল। ৳{amount} যোগ হয়েছে।")
            try:
                bot.send_message(target_id, f"🎉 <b>আপনার ডিপোজিট সফলভাবে এপ্রুভ হয়েছে!</b>\n💵 জমা হয়েছে: ৳{amount:.2f}\n💰 বর্তমান ব্যালেন্স: ৳{new_bal:.2f}")
            except Exception:
                pass
        elif action == "rej":
            del db["pending"][req_id]
            save_data(db)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="❌ বাতিল করা হয়েছে।")
            try:
                bot.send_message(target_id, f"❌ <b>আপনার ডিপোজিট রিকোয়েস্টটি বাতিল করা হয়েছে।</b>\nপরিমাণ: ৳{amount:.2f}")
            except Exception:
                pass

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user = message.from_user
    text = message.text.strip()
    session = get_user_session(user.id)

    if not session:
        bot.send_message(message.chat.id, get_main_menu_text(user.first_name, user.id), reply_markup=get_main_menu_keyboard())
        return

    step = session.get("step")

    if step == "WAIT_QTY":
        try:
            qty = int(text)
            pkg_id = session.get("pkg_id")
            pkg = SMM_PACKAGES[pkg_id]
            if qty < pkg["min_qty"]:
                bot.send_message(message.chat.id, f"❌ সর্বনিম্ন পরিমাণ হতে হবে অন্তত {pkg['min_qty']}। আবার লিখুন:")
                return
            
            session["qty"] = qty
            session["step"] = "WAIT_LINK"
            set_user_session(user.id, session)

            bot.send_message(message.chat.id, "<b>🔗 লিংক দিন (Public Link Only)</b>\n\n⚠️ অ্যাকাউন্ট বা ভিডিও সম্পূর্ণ <b>পাবলিক</b> থাকতে হবে। এখন আপনার লিংক পাঠান:")
        except ValueError:
            bot.send_message(message.chat.id, "❌ দয়া করে সঠিক সংখ্যায় পরিমাণ লিখুন:")
        return

    elif step == "WAIT_LINK":
        pkg_id = session.get("pkg_id")
        qty = session.get("qty")
        pkg = SMM_PACKAGES[pkg_id]
        clear_user_session(user.id)

        total_price = (pkg["price"] * qty) / 1000.0
        user_bal = get_user_balance(user.id)

        if user_bal < total_price:
            bot.send_message(message.chat.id, f"❌ পর্যাপ্ত ব্যালেন্স নেই! প্রয়োজন: ৳{total_price:.2f}", reply_markup=get_main_menu_keyboard())
            return

        new_bal = update_user_balance(user.id, -total_price)
        order_id = f"OS{int(time.time())}"

        db = load_data()
        db.setdefault("social_orders", {})
        db["social_orders"][order_id] = {
            "user_id": user.id, "service": pkg["name"], "qty": qty, "link": text, "price": total_price
        }
        save_data(db)

        # Added warning note about duplicate orders as requested
        success_msg = (
            f"🎉 <b>অর্ডার সফলভাবে জমা হয়েছে!</b>\n"
            f"অর্ডার আইডি: <code>{order_id}</code>\n"
            f"মূল্য কেটে নেওয়া হয়েছে: ৳{total_price:.2f}\n"
            f"অবশিষ্ট ব্যালেন্স: ৳{new_bal:.2f}\n\n"
            f"⚠️ <b>সতর্কতা:</b> আপনার ফলোয়ার/ভিউ/লাইক সম্পূর্ণ পাওয়ার আগ পর্যন্ত এই লিংকে নতুন কোনো অর্ডার প্লেস করবেন না!"
        )
        bot.send_message(message.chat.id, success_msg, reply_markup=get_main_menu_keyboard())

        try:
            bot.send_message(ADMIN_CHAT_ID, f"🔔 <b>নতুন সোশ্যাল অর্ডার!</b>\n👤 ক্রেতা: {user.first_name} (<code>{user.id}</code>)\n📦 সার্ভিস: {pkg['name']} ({qty})\n🔗 লিংক: <code>{html.escape(text)}</code>")
        except Exception:
            pass
        return

    elif step == "WAIT_AMOUNT":
        try:
            amount_val = float(text)
            if amount_val <= 0:
                raise ValueError()
        except ValueError:
            bot.send_message(message.chat.id, "❌ সঠিক সংখ্যায় টাকার পরিমাণ লিখুন:")
            return

        method = session.get("method", "পেমেন্ট")
        set_user_session(user.id, {"step": "WAIT_TRXID", "method": method, "amount": amount_val})
        bot.send_message(message.chat.id, f"<b>💳 {method}</b>\nসেন্ড মানি করুন: <code>{PAYMENT_NUMBER}</code>\n\nপেমেন্ট সম্পন্ন করে <b>TrxID</b> লিখে পাঠান:")
        return

    elif step == "WAIT_TRXID":
        trx_id = text
        amount = session.get("amount", 0.0)
        method = session.get("method", "পেমেন্ট")
        clear_user_session(user.id)

        req_id = f"r_{int(time.time())}_{user.id}"
        db = load_data()
        db["pending"][req_id] = {
            "user_id": user.id, "user_name": user.first_name, "amount": amount, "trx_id": trx_id, "method": method
        }
        save_data(db)

        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ এপ্রুভ", callback_data=f"app_{req_id}"),
            types.InlineKeyboardButton("❌ বাতিল", callback_data=f"rej_{req_id}")
        )
        try:
            bot.send_message(ADMIN_CHAT_ID, f"🔔 <b>নতুন ডিপোজিট রিকোয়েস্ট!</b>\n👤 {user.first_name} (<code>{user.id}</code>)\n💵 ৳{amount}\nTrxID: <code>{trx_id}</code>", reply_markup=admin_markup)
        except Exception:
            pass

        # Updated message informing the user that the payment request has been sent to the admin
        bot.send_message(message.chat.id, "📌 আপনার পেমেন্টের রিকোয়েস্টটি এডমিনের কাছে পাঠানো হয়েছে। এডমিন যাচাই করে আপনার ওয়ালেটে ব্যালেন্স যোগ করে দেবে।", reply_markup=get_main_menu_keyboard())
        return

    else:
        bot.send_message(message.chat.id, get_main_menu_text(user.first_name, user.id), reply_markup=get_main_menu_keyboard())

if __name__ == "__main__":
    print("🤖 Online Shop Bot Running Successfully...")
    bot.infinity_polling(skip_pending=True)