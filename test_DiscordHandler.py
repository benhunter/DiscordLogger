# https://github.com/TrayserCassa/DiscordHandler

# Discord Webhook Docs
# https://discordapp.com/developers/docs/resources/webhook

import json
import logging

from DiscordHandler import DiscordHandler


def main():
    with open("config.json", "r") as file:
        config = json.load(file)
    print(config)

    FORMAT = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(FORMAT)

    discord_handler = DiscordHandler.DiscordHandler(config["webhook"], "Test DiscordHandler")
    discord_handler.setLevel(logging.DEBUG)
    discord_handler.setFormatter(FORMAT)


    # logging.basicConfig(format="%(asctime)s:%(name)s:%(levelname)s:%(message)s",
        # level=logging.DEBUG, handlers=[stream_handler, discord_handler])

    logger = logging.getLogger("Python to Discord Logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(discord_handler)

    logger.debug("debug test")
    logger.info("info test")
    logger.warning("warning test")
    logger.error("error test")
    logger.critical("critical test")

    long_msg = range(100)

    logger.info(long_msg)

    # doThings()


def doThings():
    logging.debug("debug test")
    logging.info("info test")
    logging.warning("warning test")
    logging.error("error test")
    logging.critical("critical test")


if __name__ == "__main__":
    main()
