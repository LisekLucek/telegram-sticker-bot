import os
import mysql.connector
import telegram

from PIL import Image
import imagehash

import utils


# SELECT COUNT(*) AS n, * FROM stickers GROUP BY p_hash ORDER BY n DESC
# SELECT * FROM sets, stickers WHERE stickers.set_id = sets.id AND stickers.p_hash = (SELECT p_hash FROM stickers WHERE id = "AgADYQMAAi-vkUU")

def create_connection():
	mydb = mysql.connector.connect(
		host     = os.getenv("MYSQL_HOST"),
		user     = os.getenv("MYSQL_USER"),
		password = os.getenv("MYSQL_PASSWORD"),
		database = os.getenv("MYSQL_DATABASE")
	)

	return mydb


def add_set(sticker_set, stickers):
	con = create_connection()
	cur = con.cursor(buffered = True)

	cur.execute("SELECT id FROM sets WHERE name = %s", (sticker_set[ "name" ],))

	row = cur.fetchone()

	set_id = None

	if not row:
		cur.execute("INSERT INTO sets(name, title) VALUES (%s, %s)",
			(sticker_set["name"], sticker_set["title"]))

		print(f"Sticker set inserted! Set ID: { cur.lastrowid }")
		set_id = cur.lastrowid
	else:
		set_id = row[ 0 ]

	# print(f"Set ID: {set_id}")

	for i, sticker in enumerate(stickers):
		cur.execute("SELECT id FROM stickers WHERE set_id = %s AND in_set_index = %s", (set_id, i + 1))

		row = cur.fetchone()

		sticker_id = None
		if row:
			sticker_id = row[0]

		if sticker_id:
			cur.execute(
				"UPDATE stickers SET in_set_id = %s, hash = %s, emoji = %s, is_animated = %s, is_video = %s "
				"WHERE id = %s",
				(sticker["id"], sticker["p_hash"], sticker["emoji"],
				sticker["is_animated"], sticker["is_video"], sticker_id))
		else:
			cur.execute(
				"INSERT INTO stickers(set_id, in_set_index, in_set_id, hash, emoji, is_animated, is_video) "
				"VALUES (%s, %s, %s, %s, %s, %s, %s)",
				(set_id, i + 1, sticker["id"], sticker["p_hash"], sticker["emoji"],
				sticker["is_animated"], sticker["is_video"]))

	con.commit()
	con.close()


def find_duplicates(sticker):
	try:
		if not os.path.exists(f"stickers"):
			os.mkdir(f"stickers")

		if not os.path.exists(f"stickers/{sticker[ 'set_name' ]}"):
			os.mkdir(f"stickers/{sticker[ 'set_name' ]}")

		if not os.path.exists(f"stickers/{sticker[ 'set_name' ]}/{sticker.file_unique_id}.webp"):
			sticker.get_file().download(f"stickers/{sticker[ 'set_name' ]}/{sticker.file_unique_id}.webp")
	except telegram.TelegramError:
		print("ERROR: Failed to download sticker for searching!")

		return []

	img_hash = utils.hash_image(Image.open(f"stickers/{sticker[ 'set_name' ]}/{sticker.file_unique_id}.webp"))

	# print(int(str(img_hash), 16))

	con = create_connection()
	cur = con.cursor()

	cur.execute("SELECT sets.name, sets.title, "
		"(BIT_COUNT(stickers.hash ^ %s) + IF(stickers.emoji = %s, 0, 4)) AS similarity "
		"FROM sets, stickers WHERE stickers.set_id = sets.id "
		"ORDER BY (BIT_COUNT(stickers.hash ^ %s) + IF(stickers.emoji = %s, 0, 4)) LIMIT 5",
		(img_hash, sticker["emoji"], img_hash, sticker["emoji"]))

	result = []

	for sticker_set in cur.fetchall():
		result.append(sticker_set)

	con.close()

	return result


def recalculate_hashes():
	con = create_connection()
	cur = con.cursor()

	cur.execute("SELECT * FROM sets")

	for sticker_set in cur.fetchall():
		print(f"Recalculating hasher for: { sticker_set[1] }")
		cur.execute("SELECT * FROM stickers WHERE set_id = %s", (sticker_set[0],))

		for sticker in cur.fetchall():
			sticker_img = Image.open(f"stickers/{sticker_set[1]}/{sticker[0]}.webp")
			img_hash = utils.hash_image(sticker_img)

			cur.execute("UPDATE stickers SET hash = %s WHERE set_id = %s AND id = %s",
				(img_hash, sticker_set[0], sticker[0]))

		con.commit()

	con.close()


def get_sets(offset = 0, limit = 100):
	con = create_connection()
	cur = con.cursor()

	cur.execute("SELECT * FROM sets ORDER BY name ASC LIMIT %s OFFSET %s", (limit, offset))

	sets = []

	for sticker_set in cur.fetchall():
		sets.append({
			"name":  sticker_set[1],
			"title": sticker_set[2]
		})

	con.close()

	return sets


def get_set(set_name):
	con = create_connection()
	cur = con.cursor()

	cur.execute("SELECT * FROM sets WHERE name = %s", (set_name,))

	sticker_set = cur.fetchall()

	if not len(sticker_set):
		return None

	sticker_set = sticker_set[0]

	sticker_set_id = sticker_set[0]

	sticker_set = {
		"name":  sticker_set[1],
		"title": sticker_set[2]
	}

	cur.execute("SELECT * FROM stickers WHERE set_id = %s ORDER BY in_set_index ASC", (sticker_set_id,))

	stickers = []

	for sticker in cur.fetchall():
		stickers.append({
			"id": sticker[3],
			"hash": sticker[4],
			"emoji": sticker[5],
			"index": sticker[2],
			"is_animated": sticker[6],
			"is_video": sticker[7]
		})

	sticker_set["stickers"] = stickers

	con.close()

	return sticker_set
