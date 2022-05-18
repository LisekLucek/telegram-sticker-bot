#!/usr/bin/python

import json
import threading

from PIL import Image
import os.path

# import imagehash
import telegram.ext

import console
import database
import utils

from dotenv import load_dotenv
load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")

console.log_output("bot.log")

console.log("Starting bot...")

updater = telegram.ext.Updater(BOT_TOKEN)
bot = updater.bot

download_queue = []


def download_full_queue():
	while len(download_queue):
		download_sticker_set()


def download_sticker_set():
	if not len(download_queue):
		return

	set_name = download_queue.pop(0)

	# print(f"Downloading sticker pack { set_name }...")

	try:
		sticker_set = bot.get_sticker_set(set_name)
	except telegram.TelegramError:
		return download_sticker_set()

	stickers = []

	# print(sticker_set)

	console.progress(f"Downloading stickers [ {set_name} ]", 0, len(sticker_set[ "stickers" ]), True)

	for i, sticker in enumerate(sticker_set["stickers"]):

		console.progress(f"Downloading stickers [ { set_name }/{ sticker.file_unique_id } ]", i, len(sticker_set["stickers"]))

		if not os.path.exists(f"stickers"):
			os.mkdir(f"stickers")
		
		if not os.path.exists(f"stickers/{ set_name }"):
			os.mkdir(f"stickers/{ set_name }")

		try:
			if not os.path.exists(f"stickers/{ set_name }/{sticker.file_unique_id}.webp"):
				sticker.get_file().download(f"stickers/{ set_name }/{sticker.file_unique_id}.webp")
		except telegram.TelegramError:
			console.warn(f"Failed to download sticker! [ { set_name }/{ sticker.file_unique_id } ]")
			continue

		img_hash = utils.hash_image(Image.open(f"stickers/{ set_name }/{sticker.file_unique_id}.webp"))

		# print(f"Image downloaded! Hash: { img_hash }")
		stickers.append({
			"id": sticker["file_unique_id"],
			"emoji": sticker["emoji"],
			"p_hash": img_hash,
			"is_animated": sticker["is_animated"],
			"is_video": sticker["is_video"]
		})

		console.progress(f"Downloading stickers [ { set_name }/{ sticker.file_unique_id } ]", i + 1, len(sticker_set["stickers"]))

	database.add_set(sticker_set, stickers)
	console.log_dynamic(f"Downloaded sticker pack { set_name }!")

	# download_sticker_set()


download_thread = threading.Thread(target = download_full_queue)

# chat = bot.get_chat("@NiuEarsup")
# chatL = bot.get_chat(1213349698)
# print(chat)
# print(chatL)
#
# bot.forward_message(chatL.id, chat.id, 91)


def on_message(update, callback):
	console.log(f'\n@{update["message"]["from_user"]["username"]} » {update["message"]}\n')
	# print(callback)


def on_sticker(update, callback):
	global download_thread

	console.log(f"{ update['message']['from_user']['username'] } » { update['message']['sticker']['set_name'] }/{ update['message']['sticker']['file_unique_id'] }")
	# print(update)

	duplicates = database.find_duplicates(update["message"]["sticker"])

	resp = "Found similar stickers in:\n"

	for duplicate in duplicates:
		resp += f"{ duplicate[1] } — https://t.me/addstickers/{ duplicate[0] } ({ '{:.0f}'.format((1 - (duplicate[2] / 64)) * 100) }%)\n"

	update.effective_message.reply_text(resp, quote = True)
	# f"Got sticker from https://t.me/addstickers/{ update['message']['sticker']['set_name'] }!"

	download_queue.append(update[ 'message' ][ 'sticker' ][ 'set_name' ])

	if not download_thread.is_alive():
		download_thread = threading.Thread(target = download_full_queue)
		download_thread.start()


# with open("result_NK.json", "r") as f:
# 	chat = json.load(f)

# for message in chat["messages"]:
#     if type(message["text"]) is list:
#         for line in message["text"]:
#             if "text" in line and "type" in line:
#                 if line["type"] != "link":
#                     continue
#                 if line["text"][0:25] != "https://t.me/addstickers/":
#                     continue
#                 download_sticker_set(line["text"][25:])

# database.recalculate_hashes()

#i = 0

#while True:
	#sets = database.get_sets(i)
	#i += 100
	#if not sets:
		#break

	#for sticker_set in sets:
		#download_queue.append(sticker_set["name"])

		#if not download_thread.is_alive():
			#download_thread = threading.Thread(target = download_full_queue)
			#download_thread.start()


dispatcher: telegram.ext.Dispatcher = updater.dispatcher

dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text,    on_message))
dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.sticker, on_sticker))

updater.start_polling()
console.log("Bot started!")

updater.idle()
