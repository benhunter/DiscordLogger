# https://github.com/TrayserCassa/DiscordHandler

# Discord Webhook Docs
# https://discordapp.com/developers/docs/resources/webhook

# Tests require config.json file in same directory to hold the key "webhook" with
# the full Discord webhook URL. Treat the webhook like a password!

import functools
import json
import logging
import time

import discordlogging


def timeit_wrapper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()  # Alternatively, you can use time.process_time()
        # start = time.process_time()
        func_return_val = func(*args, **kwargs)
        end = time.perf_counter()
        print('{0:<10}.{1:<8} : {2:<8}'.format(func.__module__,
                                               func.__name__,
                                               end - start))
        return func_return_val
    return wrapper


@timeit_wrapper
def main():
    with open("config.json", "r") as file:
        config = json.load(file)
    print(config)

    FORMAT = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(FORMAT)

    discord_handler = discordlogging.DiscordHandler(config["webhook"],
                                                    "Test DiscordHandler")
    discord_handler.setLevel(logging.DEBUG)
    discord_handler.setFormatter(FORMAT)

    logger = logging.getLogger("Python to Discord Logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(discord_handler)

    # Test rate limiting
    for count in range(100):
        # logger.debug(f"debug test {count}")
        logger.info(f"info test {count}")
        # logger.warning(f"warning test {count}")
        # logger.error(f"error test {count}")
        # logger.critical(f"critical test {count}")

    # Test message longer than Discord limit
    long_msg = ' '.join([str(x) for x in range(1000)])
    logger.info(f"{len(long_msg)}, {long_msg}")


if __name__ == "__main__":
    main()
