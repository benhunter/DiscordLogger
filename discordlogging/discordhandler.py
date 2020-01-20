import logging
import json
import time


try:
    import requests
except ImportError as ex:
    print("Please Install requests")
    raise ImportError(ex)


class DiscordHandler(logging.Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to a Discord Server using webhooks.
    """

    def __init__(self, webhook_url, agent=None):
        logging.Handler.__init__(self)

        if webhook_url is None or webhook_url == "":
            raise ValueError("Webhook_url parameter cannot be empty!")

        if agent is None or agent == "":
            agent = "DiscordHandler"

        self._url = webhook_url
        self._agent = agent
        self._header = self.create_header()
        self._name = ""

    def create_header(self):
        return {
            'User-Agent': self._agent,
            "Content-Type": "application/json"
        }

    def _write_to_discord(self, message):
        content = json.dumps({"content": message})

        max_retries = 5
        for retries in range(max_retries):
            request = requests.post(self._url,
                                    headers=self._header,
                                    data=content)
            if request.status_code == 404:
                raise requests.exceptions.InvalidURL(
                    "This URL seems wrong... Response = %s" % request.text)
            elif request.status_code == 429:
                retry_after = int(request.headers.get('Retry-After', 500)) / 1000.0
                # print("Retrying after", retry_after)
                time.sleep(retry_after)
                continue
            elif request.status_code >= 400:
                # request was unsuccessful
                raise requests.exceptions.HTTPError(
                    f"Request not successful... HTTP Response Code = "
                    f"{request.status_code}, Message = {request.text}")
            elif request.status_code < 400:
                # request was successful
                break

    def emit(self, record):
        try:
            msg = self.format(record)
            # Discord limits messages to 2000 characters
            for short_msg in self._chunks(msg, 1950):
                self._write_to_discord(f"```{short_msg}```")
        except Exception:  # necessary for handling exceptions called while logging
            self.handleError(record)

    def _chunks(self, seq, length):
        ''' Divide an iterable into smaller chunks.
        :param seq: Iterable sequence object like string or list.
        :param length: The length of the chunks.
        :return: The next group from seq of length.
        '''
        for i in range(0, len(seq), length):
            yield seq[i:i + length]
