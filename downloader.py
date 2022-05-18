import os
import shutil


def create_path(path):
	if not os.path.exists(path):
		create_path(os.path.dirname(path))
		os.mkdir(path)


def download_sticker(sticker_file, local_path):

	create_path(os.path.dirname(local_path))
	sticker_file.download(local_path)


def remove_set(set_name):
	if os.path.exists(os.path.join("stickers", set_name)):
		shutil.rmtree(os.path.join("stickers", set_name))
