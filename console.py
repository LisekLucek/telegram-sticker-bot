import shutil
from datetime import datetime

COLOUR_ERROR: str = u"\u001b[38;2;255;0;0m"    # u"\u001b[31m"
COLOUR_WARN:  str = u"\u001b[38;2;255;255;0m"  # u"\u001b[33m"
COLOUR_RESET: str = u"\u001b[0m"

log_file: str

dynamic_log_contents = ""
dynamic_log_lines = 0


def _time_str():
	now = datetime.now()
	return now.strftime("%H:%M:%S %Y-%m-%d")


def _format(message, log_type: str, max_terminal_width = False) -> str:
	"""
	Formats the string for terminal output
	:param message: message to format
	:param log_type: type of output (max 5 chars)
	:param max_terminal_width: if output should be limited by the terminal width
	:return: formatted string
	"""
	global dynamic_log_lines

	dynamic_log_lines = 0

	message_str = str(message)
	message_arr = message_str.split("\n")

	if max_terminal_width:
		term_size = shutil.get_terminal_size()
		w = term_size[0] - 28

		new_message_arr = []

		for line in message_arr:

			for new_line in [line[i:i + w] for i in range(0, len(line), w)]:
				new_message_arr.append(new_line)

		message_arr = new_message_arr

	type_fixed = (log_type + " ").rjust(6)

	message_ret = ""

	if len(message_arr) == 1:
		message_ret += type_fixed + _time_str() + " ═ " + message_arr[0]
	else:
		message_ret += type_fixed + _time_str() + " ╦ " + message_arr[0] + "\n"
		for line in message_arr[1:-1]:
			message_ret += "                          ║ " + line + "\n"
		message_ret += "                          ╚ " + message_arr[-1]

	return message_ret


def log_output(file_path: str):
	global log_file

	log_file = file_path


def log(message):
	global log_file

	dynamic_reset()

	msg_file = _format(message, "LOG") + "\n"
	msg_term = _format(message, "LOG", True)

	if log_file:
		with open(log_file, "a") as f:
			f.write(msg_file)
	print(msg_term)


def debug(message):
	global log_file

	dynamic_reset()

	msg_file = _format(message, "DEBUG") + "\n"
	msg_term = _format(message, "DEBUG", True)

	if log_file:
		with open(log_file, "a") as f:
			f.write(msg_file + "\n")
	print(msg_term)


def warn(message):
	global log_file

	dynamic_reset()

	msg = _format(message, "WARN")
	if log_file:
		with open(log_file, "a") as f:
			f.write(msg + "\n")
	print(COLOUR_WARN + msg + COLOUR_RESET)


def error(message):
	global log_file

	dynamic_reset()

	msg = _format(message, "ERROR")
	if log_file:
		with open(log_file, "a") as f:
			f.write(msg + "\n")
	print(COLOUR_ERROR + msg + COLOUR_RESET)


def dynamic_reset():
	global log_file, dynamic_log_lines, dynamic_log_contents

	dynamic_log_lines = 0

	if dynamic_log_contents and log_file:
		with open(log_file, "a") as f:
			f.write(dynamic_log_contents)
			dynamic_log_contents = ""


def log_dynamic(message, final = False):
	global dynamic_log_lines, dynamic_log_contents

	if not final:
		for i in range(dynamic_log_lines):
			print(u"\u001b[1F\u001b[K", end = "")

	msg_file = _format(message, "LOG") + "\n"
	msg_term = _format(message, "LOG", True)

	if final and log_file:
		with open(log_file, "a") as f:
			f.write(msg_file)

	print(msg_term)

	dynamic_log_lines = msg_term.count("\n") + 1
	dynamic_log_contents = msg_file


# progress_animation_step = 0
# progress_animation = "🬀🬃🬏🬑🬖🬭🬮🬱🬳🬹🬺🮋🬹🬰🬭🬋🬂 "
# progress_animation = "🮠🮧🮬🮮🮪🮦🮢 🮡🮥🮪🮮🮫🮤🮠 🮣🮦🮫🮮🮭🮧🮡 🮢🮤🮭🮮🮬🮥🮣 "
# progress_animation = "▖▘▝▗"


def progress(message, current, max, final = False):
	# global progress_animation, progress_animation_step

	fract_blocks = " ▏▎▍▌▋▊▉█"

	term_size = shutil.get_terminal_size()
	w = term_size[ 0 ] - 28 - 10 - len(str(max)) * 2 - 26

	current_norm = int(current / max * w)
	current_fract = int(current / max * w * 8) % 8
	current_norm_rest = w - current_norm - 1
	if current_norm_rest < 0:
		current_norm_rest = 0

	current_fract_block = "" if current // max == 1 else fract_blocks[ current_fract ]

	# background = u"\u001b[43m\u001b[32m"
	background = u"\u001b[48;2;32;32;32m"
	reset = u"\u001b[0m"

	# progr = f"{ progress_animation[progress_animation_step] }  { background }{ '█' * current_norm }{ fract_blocks[current_fract] }{ ' ' * (w - current_norm - 1) }{ reset } { (current / max * 100) :.2f}% [ { current } / { max } ]"
	progr = f"{background}{'█' * current_norm}{ current_fract_block }{' ' * current_norm_rest}{reset} {(current / max * 100) :.2f}% [ {current} / {max} ]"

	log_dynamic(message + "\n" + progr, final)

	# progress_animation_step += 1
	# progress_animation_step %= 32
