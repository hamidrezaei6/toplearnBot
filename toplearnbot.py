# 7565377609:AAFpwYewvC2zH74A7AG_yvmVeLDe9oj0BgQ
# pip install python-telegram-bot beautifulsoup4 requests

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup , ReplyKeyboardMarkup , KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests
from bs4 import BeautifulSoup

TOKEN = '7565377609:AAFpwYewvC2zH74A7AG_yvmVeLDe9oj0BgQ'


def fetch_courses():
    url = 'https://toplearn.com/courses'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    cousres = []
    for course in soup.select('.col-lg-4.course-col'):
        title = course.select_one('h2 a').text.strip()
        instructor = course.select_one('.top a').text.strip()
        duration = course.select_one('.time').text.strip()
        discount_element = course.select_one('.off-section')
        if discount_element:
            discount = discount_element.text.strip()
        else:
            discount = 'دوره تخفیف ندارد'

        # بررسی لینک تصویر
        image_tag = course.select_one(".img-layer img")
        image = "https://toplearn.com" + (
                image_tag.get("data-src") or image_tag.get("src"))  # استفاده از data-src یا src

        # لینک دوره
        link_tag = course.select_one('h2 a')
        link = 'https://toplearn.com' + link_tag.get('href')

        cousres.append({
            'title': title,
            'instructor': instructor,
            'duration': duration,
            'discount': discount,
            'image': image,
            'link': link,
        })

    return cousres


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [KeyboardButton("📜 نمایش دوره ها")],
        [KeyboardButton("ℹ️ درباره ربات")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
    await update.message.reply_text(
        "سلام! برای دریافت اطلاعات دوره های تاپ لرن ، کلمه 'دوره' را وارد کنید.",
        reply_markup=reply_markup
    )


async def send_courses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    courses = fetch_courses()
    if not courses:
        await update.message.reply_text('متاسفانه در حال حاضر اطلاعاتی یافت نشد.')
        return

    for course in courses[:5]:  # ارسال ۵ دوره اول
        keyboard = [
            [InlineKeyboardButton("👀 مشاهده لینک دوره", url=course["link"])],
            [InlineKeyboardButton("ℹ️ اطلاعات بیشتر", callback_data=f"info_{course['title']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_photo(
            photo=course["image"],
            caption=f"🎓 {course['title']}\n"
                    f"👨‍🏫 مدرس: {course['instructor']}\n"
                    f"⏱ مدت زمان دوره: {course['duration']}\n"
                    f" 📴 میزان تخفیف دوره :{course['discount']}\n",
            # f"🔗 [مشاهده لینک دوره] :{course['link']})",

            reply_markup=reply_markup
        )


async def course_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    course_title = query.data.replace('info_', '')
    courses = fetch_courses()
    course = next((c for c in courses if c['title'] == course_title), None)

    if course:
        await query.edit_message_text(
            text=f"🎓 {course['title']}\n"
                 f"👨‍🏫 مدرس: {course['instructor']}\n"
                 f"⏱ مدت زمان دوره: {course['duration']}\n"
                 f"🔗 [مشاهده لینک دوره] {course['link']})",
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text('متاسفانه اطلاعات این دوره در حال حاضر موجود نیست.')


async def about(update:Update,context:ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🤖 این ربات برای نمایش اطلاعات دوره‌های سایت تاپ‌لرن طراحی شده است.\n"
        "برای دریافت اطلاعات دوره‌ها، روی دکمه '📚 نمایش دوره‌ها' کلیک کنید."
    )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    # application.add_handler(MessageHandler(filters.TEXT & filters.Regex('دوره'), send_courses))
    application.add_handler(MessageHandler(filters.Regex("📜 نمایش دوره ها"),send_courses))
    application.add_handler(MessageHandler(filters.Regex("ℹ️ درباره ربات"),about))
    application.add_handler(CallbackQueryHandler(course_info))

    application.run_polling()


if __name__ == '__main__':
    main()
