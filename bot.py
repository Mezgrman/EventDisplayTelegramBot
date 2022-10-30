"""
Copyright (C) 2022 Julian Metzler
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

import base64
import datetime
import logging
import requests
import time
import traceback

from termcolor import colored

from settings import *
from settings_secure import *

logging.basicConfig()
LOGGER = logging.getLogger(BOT_NAME)
LOGGER.setLevel(logging.INFO)

# List of chat IDs that have alreay been responded to
# in case the event is over. Not persistent.
EVENT_OVER_CIDS = []

"""
LISTENER
"""

def listener_console_logging(messages):
    def _readable(msg):
        if msg.content_type == 'text':
            return msg.text
        else:
            if msg.content_type is not None:
                return colored(msg.content_type.capitalize(), 'blue')
            else:
                return colored("Unknown Message Type", 'blue')

    for msg in messages:
        filtered = filter_message_incoming(msg)
        LOGGER.info("%(filtered)s[%(timestamp)s #%(mid)s %(firstname)s %(lastname)s @%(username)s #%(uid)s @ %(groupname)s #%(cid)s] %(text)s" % {
            'filtered': colored("[FILTERED]", 'red') if not filtered else "",
            'timestamp': datetime.datetime.fromtimestamp(msg.date).strftime("%d.%m.%Y %H:%M:%S"),
            'firstname': colored(msg.from_user.first_name, 'green'),
            'lastname': colored(msg.from_user.last_name, 'magenta'),
            'username': colored(msg.from_user.username, 'yellow'),
            'groupname': colored(msg.chat.title, 'red'),
            'mid': colored(str(msg.message_id), 'blue'),
            'uid': colored(str(msg.from_user.id), 'cyan'),
            'cid': colored(str(msg.chat.id), 'cyan'),
            'text': _readable(msg)
        })


bot = telebot.TeleBot(API_TOKEN, threaded = False)
bot.set_update_listener(listener_console_logging)
bot.me = bot.get_me()


"""
MESSAGE HANDLERS
"""

def filter_message_incoming(msg):
    # Discard any non-admin messages if in admin mode
    if ADMIN_ONLY and msg.chat.id != ADMIN_CID:
        return False
    # Discard messages from blacklisted users
    if msg.chat.id in BLOCKLIST:
        return False
    return True

def prepare_text(in_text):
    text = TEXT_PREPARE_FUNC(in_text)
    out_lines = []
    lines = text.splitlines()

    for line in lines:
        if not line:
            line = " "
        for start in range(0, len(line), CHARACTERS_PER_LINE):
            out_lines.append(line[start:start+CHARACTERS_PER_LINE].ljust(CHARACTERS_PER_LINE))

    for i in range(LINES - len(out_lines)):
        out_lines.append(" " * CHARACTERS_PER_LINE)

    out_lines = out_lines[:LINES]
    out_text = "".join(out_lines)
    return out_lines, out_text

# Handle /start
@bot.message_handler(commands = ['start'], func=filter_message_incoming)
def handle_start(msg):
    cid = msg.chat.id
    if EVENT_OVER:
        if cid not in EVENT_OVER_CIDS:
            EVENT_OVER_CIDS.append(cid)
            try:
                bot.send_message(cid, f"Sorry, seems you were too late. {EVENT_NAME} is over and the display has been removed. I hope you had a great time! ❤️", parse_mode = 'markdown')
            except:
                traceback.print_exc()
    else:
        bot.send_message(cid, f"Hi! Just send me something and I'll display it on the {DISPLAY_TYPE} display{LOCATION}. ({LINES} lines, {CHARACTERS_PER_LINE} characters each)", parse_mode = 'markdown')

# Handle Text
@bot.message_handler(content_types=['text'], func=filter_message_incoming)
def handle_text(msg):
    cid = msg.chat.id
    if EVENT_OVER:
        if cid not in EVENT_OVER_CIDS:
            EVENT_OVER_CIDS.append(cid)
            try:
                bot.send_message(cid, f"Sorry, seems you were too late. {EVENT_NAME} is over and the display has been removed. I hope you had a great time and thank you for playing around with my display! ❤️", parse_mode = 'markdown')
            except:
                traceback.print_exc()
    else:
        try:
            out_lines, out_text = prepare_text(msg.text)
            buffer = base64.b64encode(out_text.encode('latin-1')).decode('latin-1')
            resp = requests.post(f"http://{DISPLAY_HOST}/canvas/update.json", json={"buffer": buffer})
            if resp.status_code != 200:
                raise Exception("Display returned non-200 status code")
            bot.reply_to(msg, "I sent this to the display:\n\n`{display_text}`".format(display_text="\n".join(out_lines)), parse_mode='markdown')
        except:
            bot.reply_to(msg, ERROR_REPLY)
            traceback.print_exc()

"""
RUN
"""

if __name__ == "__main__":
    exit = False
    while not exit:
        try:
            LOGGER.info("Press Ctrl-C again within one second to terminate the bot")
            time.sleep(1)
            LOGGER.info("Starting bot")
            bot.polling()
        except KeyboardInterrupt:
            LOGGER.info("Goodbye!")
            exit = True
        except:
            traceback.print_exc()
            time.sleep(10)
