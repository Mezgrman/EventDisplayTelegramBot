ADMIN_ONLY = False
EVENT_OVER = False

DISPLAY_HOST = "0.0.0.0"

ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ0123456789 -.()!:/\",=ÅØ"
TEXT_PREPARE_FUNC = lambda text: "".join([c for c in text.upper() if c in ALLOWED_CHARS + "\n"])

BOT_NAME = "EventDisplayBot"
EVENT_NAME = "The event"
DISPLAY_TYPE = "split-flap"
LOCATION = " in the hotel lobby"
LINES = 2
CHARACTERS_PER_LINE = 24

ERROR_REPLY = "Sorry, something went wrong."