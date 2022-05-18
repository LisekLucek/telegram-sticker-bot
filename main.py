#!/usr/bin/python
import datetime
import json
import threading

from PIL import Image
import os.path

# import imagehash
import telegram.ext

import console
import database
import downloader
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

		try:
			if not os.path.exists(f"stickers/{ set_name }/{sticker.file_unique_id}.webp"):
				downloader.download_sticker(sticker.get_file(), f"stickers/{sticker[ 'set_name' ]}/{sticker.file_unique_id}.webp")
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

		# downloader.upload_sticker(f"stickers/{ set_name }/{sticker.file_unique_id}.webp")

		console.progress(f"Downloading stickers [ { set_name }/{ sticker.file_unique_id } ]", i + 1, len(sticker_set["stickers"]))

	database.add_set(sticker_set, stickers)
	console.log_dynamic(f"Updated sticker pack { set_name }!")

	downloader.remove_set(set_name)

	# download_sticker_set()


download_thread = threading.Thread(target = download_full_queue)


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

	set_info = database.get_set_info(update['message']['sticker']['set_name'])

	if set_info:
		now = datetime.datetime.now()
		if (now - set_info[ "update_time" ]).total_seconds() < 24 * 60 * 60:
			return

	download_queue.append(update[ 'message' ][ 'sticker' ][ 'set_name' ])

	if not download_thread.is_alive():
		download_thread = threading.Thread(target = download_full_queue)
		download_thread.start()


dispatcher: telegram.ext.Dispatcher = updater.dispatcher

dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text,    on_message))
dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.sticker, on_sticker))

updater.start_polling()
console.log("Bot started!")

updater.idle()
