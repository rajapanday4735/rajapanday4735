import telebot
import requests
import os
from urllib.parse import quote_plus
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8375545383:AAEMnp48xXivpUqkcOa1t3tXuDfFxWqe03A"
TMDB_API_KEY = os.getenv("TMDB_API_KEY") or "03985d11f17343d76561cebc240f5a32"

# Apni website ka search URL (movie name auto add hoga)
MOVIE_WEBSITE = "https://www.filmyfiy.mov/site-1.html?to-search="

# Optional (caption me show hoga)
BOT_USERNAME = "@filmyrajabot"

# =========================================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie/"
POSTER_BASE = "https://image.tmdb.org/t/p/w500"


# ================= START ==================
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "🎬 <b>Movie / OTT Info Bot</b>\n\n"
        "👉 Kisi bhi movie ka <b>naam likho</b>\n"
        "👉 Multiple options milenge\n"
        "👉 Watch Now se website open hogi"
    )


# ================= SEARCH =================
@bot.message_handler(func=lambda m: True)
def search_movie(message):
    query = message.text.strip()

    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "include_adult": False,
        "language": "en-US",
        "page": 1
    }

    try:
        r = requests.get(TMDB_SEARCH_URL, params=params, timeout=10)
        data = r.json()
    except Exception:
        bot.reply_to(message, "⚠️ TMDB error, baad me try karo")
        return

    if not data.get("results"):
        bot.reply_to(message, "❌ Movie nahi mili")
        return

    markup = InlineKeyboardMarkup()
    results = data["results"][:10]

    for movie in results:
        title = movie.get("title", "Unknown")
        year = movie.get("release_date", "")[:4]
        movie_id = movie.get("id")

        markup.add(
            InlineKeyboardButton(
                f"{title} ({year})",
                callback_data=f"movie_{movie_id}"
            )
        )

    bot.send_message(
        message.chat.id,
        "🎥 <b>Select Movie</b>",
        reply_markup=markup
    )


# ============== DETAILS ===================
@bot.callback_query_handler(func=lambda call: call.data.startswith("movie_"))
def movie_details(call):
    movie_id = call.data.split("_")[1]

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }

    r = requests.get(TMDB_MOVIE_URL + movie_id, params=params)
    movie = r.json()

    title = movie.get("title", "Unknown")
    overview = movie.get("overview", "No description available")
    rating = movie.get("vote_average", "N/A")
    year = movie.get("release_date", "")[:4]
    poster = movie.get("poster_path")

    search_name = quote_plus(title)
    watch_url = MOVIE_WEBSITE + search_name

    caption = (
        f"🎬 <b>{title}</b> ({year})\n\n"
        f"⭐ Rating: {rating}\n\n"
        f"{overview}\n\n"
        f"🔎 Via {BOT_USERNAME}"
    )

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("▶️ Watch Now", url=watch_url),
        InlineKeyboardButton("📢 Join Channel", url="https://t.me/+xToZATTgDhk5MGM1"),
        InlineKeyboardButton("🎥 Request Movie", url="https://t.me/+CoqbU5nFeCU4ZDFl")
    )

    if poster:
        bot.send_photo(
            call.message.chat.id,
            POSTER_BASE + poster,
            caption=caption,
            reply_markup=markup
        )
    else:
        bot.send_message(
            call.message.chat.id,
            caption,
            reply_markup=markup
        )

    bot.answer_callback_query(call.id)


# ================= RUN ====================
print("Bot started...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
