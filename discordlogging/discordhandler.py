import logging
import json
import time
import copy


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
        self.formatter = SimpleDiscordFormatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")

    def create_header(self):
        return {
            'User-Agent': self._agent,
            "Content-Type": "application/json"
        }

    def _write_to_discord(self, message):
        max_retries = 5
        for retry in range(max_retries):
            request = requests.post(self._url,
                                    headers=self._header,
                                    json=message)
            if request.status_code == 404:
                raise requests.exceptions.InvalidURL(
                    "This URL seems wrong... Response = %s" % request.text)
            elif request.status_code == 429:
                retry_after = int(request.headers.get('Retry-After', 500)) / 1000.0
                # print("Retrying after", retry_after)
                time.sleep(retry_after)
                continue
            elif request.status_code >= 400:
                # request unsuccessful
                raise requests.exceptions.HTTPError(
                    f"Request not successful... HTTP Response Code = "
                    f"{request.status_code}, Message = {request.text}")
            elif request.status_code < 400:
                # request successful
                break

    def emit(self, record):
        try:
            # Discord limits messages to 2000 characters
            # Also need padding for JSON formatting
            # TODO test padding length with embed style
            for short_msg in self._chunks(record.getMessage(), 1900):  # 1940 without embed
                chunked_record = copy.copy(record)
                chunked_record.msg = short_msg
                json_record = self.format(chunked_record)
                self._write_to_discord(json_record)
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

        
class SimpleDiscordFormatter(logging.Formatter):
    """Basic formatter without styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def format(self, record):
        # return {'content': record.getMessage()}
        return {'content': super().format(record)}


class DiscordFormatter(logging.Formatter):
    def format(self, record):
        """
        Format message content, timestamp when it was logged and a
        coloured border depending on the severity of the message
        """
        msg = record.getMessage()
        exc = record.__dict__['exc_info']
        if exc:
            msg = msg + '\n```{}```'.format(traceback.format_exc())
        embed = dict()
        embed["description"] = msg
        embed['timestamp'] = datetime.utcnow().isoformat()
        embed['author'] = {'name': '{}@{}'.format(
            record.name, record.filename)}
        try:
            colors = {
                'DEBUG': 810979,
                'INFO': 1756445,
                'WARNING': 15633170,
                'ERROR': 16731648,
                'CRITICAL': 16711680,
            }
            embed['color'] = colors[record.levelname]
        except KeyError:
            pass
        return {'embeds': [embed]}
