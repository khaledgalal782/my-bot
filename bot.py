import json
import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# 1. الإعدادات وبيانات التواصل
BOT_TOKEN = "9018184038:AAHfCI0G34jBtIPeh15DIuMjiKZMdmsNAoM"
ADMIN_CHAT_ID = 8085630413
WALLET_NUMBER = "01060340749"
TELEGRAM_USER = "@khaled_galal"

BALANCES_FILE = "balances.json"

# دوال حفظ وقراءة الرصيد
def load_balances():
    if os.path.exists(BALANCES_FILE):
        try:
            with open(BALANCES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_balances(data):
    with open(BALANCES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_balance(user_id):
    balances = load_balances()
    return balances.get(str(user_id), 0.0)

def add_user_balance(user_id, amount):
    balances = load_balances()
    current = balances.get(str(user_id), 0.0)
    balances[str(user_id)] = round(current + amount, 2)
    save_balances(balances)
    return balances[str(user_id)]

def deduct_user_balance(user_id, amount):
    balances = load_balances()
    current = balances.get(str(user_id), 0.0)
    if current >= amount:
        balances[str(user_id)] = round(current - amount, 2)
        save_balances(balances)
        return True, balances[str(user_id)]
    return False, current

# 2. الخدمات المتاحة
SERVICES = {
    "canva": {
        "name": "اشتراك كانفا برو 3 سنوات",
        "price": 75,
        "desc": "يتم ارسال البريد الالكتروني الخاص بك وببعتلك دعوة عبر جيميل ويمكنك ذلك قبول الدعوة وبتروح علي كانفا بمجرد قبول الدعوة بتلاقي الحساب اتفعل وجميع المميزات متاحه عليه"
    },
    "capcut_1m": {
        "name": "كاب كات برو شهر",
        "price": 150,
        "desc": "كاب كات برو لمدة شهر كامل بدون علامة مائية وبكل الميزات يتم تسليمك حساب جاهز بريد وباسورد بتسجل الدخول بيهم وبتلاقي الحساب برو"
    },
    "capcut_6m": {
        "name": "كاب كات برو 6 شهور",
        "price": 950,
        "desc": "اشتراك كاب كات برو 6 أشهر مع ضمان كامل المدة يتم تسليمك حساب جاهز بريد وباسورد بتسجل الدخول بيهم وبتلاقي الحساب برو"
    },
    "gemini": {
        "name": "جوجل جيمناي 18 شهر",
        "price": 200,
        "desc": "برجاء ارسال البريد الالكتروني الخاص بك وبيتم ارسال الدعوة عبر جيميل بعد ذلك يمكنك الضغط علي قبول الدعوة وبكده حسابك بيكون مفعل برو"
    },
}

def get_main_menu():
    keyboard = [
        [KeyboardButton("🛍️ الخدمات"), KeyboardButton("👤 حسابي")],
        [KeyboardButton("💬 الدعم"), KeyboardButton("📦 طلباتي")],
        [KeyboardButton("💰 إضافة رصيد"), KeyboardButton("⚙️ الإعدادات")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_services_keyboard():
    keyboard = []
    row = []
    for s_id, s_data in SERVICES.items():
        button_text = f"🔹 {s_data['name']} | {s_data['price']} ج"
        row.append(InlineKeyboardButton(button_text, callback_data=f"buy_{s_id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "👑 أهلاً بك في متجر الخدمات الرقمية!\nاختر من القائمة أدناه لتصفح الخدمات المتاحة:"
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu())
    await update.message.reply_text("⚡ اختر الخدمة المطلوبة:", reply_markup=get_services_keyboard())

async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == "🛍️ الخدمات":
        await update.message.reply_text("⚡ اختر الخدمة المطلوبة:", reply_markup=get_services_keyboard())
    elif text == "👤 حسابي":
        balance = get_user_balance(user.id)
        msg = (
            f"👤 بيانات الحساب:\n\n"
            f"الاسم: {user.full_name}\n"
            f"المعرف (ID): {user.id}\n"
            f"💵 رصيدك الحالي: {balance} جنيه مصري"
        )
        await update.message.reply_text(msg)
    elif text == "💬 الدعم":
        await update.message.reply_text(
            f"📞 للتواصل مع الدعم الفني:\n"
            f"واتساب: {WALLET_NUMBER}\n"
            f"تليجرام: {TELEGRAM_USER}"
        )
    elif text == "💰 إضافة رصيد":
        msg = (
            f"💳 لإضافة رصيد إلى حسابك:\n\n"
            f"1️⃣ قم بتحويل المبلغ المطلوب عبر فودافون كاش أو إنستاباي إلى:\n"
            f"`{WALLET_NUMBER}`\n\n"
            f"2️⃣ بعد التحويل، يرجى إرسال صورة إيصال التحويل (اسكرين شوت) مع إرسال رقم الـ ID الخاص بك ({user.id}) إلى:\n"
            f"📱 واتساب: {WALLET_NUMBER}\n"
            f"💬 تليجرام: {TELEGRAM_USER}\n\n"
            f"📸 أو يمكنك إرسال صورة الإيصال مباشرة هنا في البوت وسنقوم بإضافة الرصيد فوراً."
        )
        await update.message.reply_text(msg)
    elif text == "📦 طلباتي":
        await update.message.reply_text("📦 لمتابعة طلباتك، يرجى التواصل مع الدعم الفني مباشرة.")
    else:
        await update.message.reply_text("يرجى الاختيار من القائمة السفلية.")

async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    service_id = query.data.replace("buy_", "")
    service = SERVICES.get(service_id)
    if not service:
        await query.edit_message_text("حدث خطأ في تحديد الخدمة.")
        return

    context.user_data["selected_service"] = service_id
    user_id = query.from_user.id
    balance = get_user_balance(user_id)
    price = service["price"]

    msg = (
        f"📦 الخدمة المحددة: {service['name']}\n\n"
        f"📝 التفاصيل:\n{service['desc']}\n\n"
        f"💰 المبلغ المطلوب: {price} جنيه\n"
        f"💵 رصيدك الحالي في البوت: {balance} جنيه\n\n"
    )

    keyboard = []
    # إذا كان لديه رصيد كافٍ يستطيع الشراء مباشرة
    if balance >= price:
        msg += "✅ رصيدك الحالي كافٍ لإتمام عملية الشراء فوراً بالخصم من الرصيد."
        keyboard.append([InlineKeyboardButton("⚡ شراء فوري بالخصم من الرصيد", callback_data=f"pay_balance_{service_id}")])
    else:
        msg += (
            f"💳 بيانات الدفع والتحويل:\n"
            f"فودافون كاش / إنستاباي: {WALLET_NUMBER}\n\n"
            f"⚠️ برجاء إرسال إيصال التحويل بعد الدفع عبر:\n"
            f"واتساب: {WALLET_NUMBER}\n"
            f"تليجرام: {TELEGRAM_USER}\n\n"
            f"📸 أو أرسل صورة الإيصال (اسكرين شوت) هنا في البوت لتأكيد الطلب."
        )

    keyboard.append([InlineKeyboardButton("🔙 رجوع للخدمات", callback_data="back_to_services")])
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def pay_with_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    service_id = query.data.replace("pay_balance_", "")
    service = SERVICES.get(service_id)

    if not service:
        await query.edit_message_text("حدث خطأ.")
        return

    success, new_balance = deduct_user_balance(user.id, service["price"])
    if success:
        await query.edit_message_text(
            f"🎉 تم شراء {service['name']} بنجاح بالخصم من رصيدك!\n"
            f"💵 المتبقي في رصيدك: {new_balance} جنيه.\n"
            f"جاري مراجعة طلبك وإرسال بيانات الحساب لك فوراً."
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"🚨 **طلب شراء مدفوع من الرصيد:**\n\n"
                f"👤 العميل: @{user.username if user.username else 'بدون معرف'}\n"
                f"🆔 المعرف: `{user.id}`\n"
                f"📦 الخدمة: {service['name']}\n"
                f"💰 المبلغ المخصوم: {service['price']} جنيه"
            )
        )
    else:
        await query.edit_message_text("⚠️ رصيدك غير كافٍ لإتمام العملية.")

async def back_to_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⚡ اختر الخدمة المطلوبة من القائمة أدناه:", reply_markup=get_services_keyboard())

# استقبال صورة الإيصال إذا أرسلها العميل داخل الشات
async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    service_id = context.user_data.get("selected_service")
    service = SERVICES.get(service_id, {})
    price = service.get("price", 0)

    await update.message.reply_text("✅ تم استلام صورة الإيصال بنجاح! جاري مراجعة التحويل وتنفيذ طلبك خلال لحظات.")

    photo_id = update.message.photo[-1].file_id
    caption = (
        f"🔔 طلب شراء / شحن جديد بوصل تحويل:\n\n"
        f"👤 العميل: @{user.username if user.username else 'بدون معرف'}\n"
        f"🆔 المعرف: {user.id}\n"
        f"📦 الخدمة المحددة: {service.get('name', 'شحن رصيد عام')}\n"
        f"💵 المبلغ: {price} جنيه"
    )

    admin_keyboard = [
        [
            InlineKeyboardButton("✅ تأكيد وشحن الرصيد", callback_data=f"approve_{user.id}_{price}"),
            InlineKeyboardButton("❌ رفض الطلب", callback_data=f"reject_{user.id}"),
        ]
    ]

    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo_id,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(admin_keyboard)
    )

async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    action = data[0]
    user_id = int(data[1])

    if action == "approve":
        amount = float(data[2])
        new_total = add_user_balance(user_id, amount)
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎉 تم تأكيد الدفع بنجاح!\nتمت إضافة {amount} جنيه إلى رصيد حسابك.\n💵 رصيدك الإجمالي الآن: {new_total} جنيه."
        )
        await query.edit_message_caption(caption=f"{query.message.caption}\n\n✔️ الحالة: تم التأكيد وإضافة الرصيد.")

    elif action == "reject":
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ نعتذر، لم يتم العثور على التحويل في حسابنا. يرجى مراجعة الدعم."
        )
        await query.edit_message_caption(caption=f"{query.message.caption}\n\n✖️ الحالة: تم رفض الطلب.")

# أمر شحن يدوي للأدمن: /add ID AMOUNT
async def add_balance_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    try:
        target_id = int(context.args[0])
        amount = float(context.args[1])
        total = add_user_balance(target_id, amount)
        await update.message.reply_text(f"✅ تم بنجاح شحن {amount} جنيه للمستخدم {target_id}.\nرصيده الحالي: {total} جنيه.")
        await context.bot.send_message(
            chat_id=target_id,
            text=f"🎁 تمت إضافة رصيد لحسابك بقيمة {amount} جنيه من الإدارة!\n💵 رصيدك الحالي: {total} جنيه."
        )
    except (IndexError, ValueError):
        await update.message.reply_text("طريقة كتابة الأمر:\n/add معرف_العميل المبلغ\nمثال:\n/add 8085630413 50")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_balance_manual))
    app.add_handler(CallbackQueryHandler(select_service, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(pay_with_balance, pattern="^pay_balance_"))
    app.add_handler(CallbackQueryHandler(back_to_services, pattern="^back_to_services$"))
    app.add_handler(CallbackQueryHandler(admin_decision, pattern="^(approve|reject)_"))
    app.add_handler(MessageHandler(filters.PHOTO, receive_receipt))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))

    app.run_polling()