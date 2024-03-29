import pathlib
import logging
import json
from urllib.parse import urlparse
from typing import Tuple, Optional


log = logging.getLogger("data")

DEFAULT_DATA_FILE = "data/safe_links_all"
DEFAULT_OUTPUT_PREFIX = "data/images"
DEFAULT_IMAGES_FILE = DEFAULT_OUTPUT_PREFIX + ".csv"

# lower-cased set of image-hosting domains
IMAGE_DOMAINS = {'imgur.com', 'i.imgur.com', 'flic.kr', 'twitpic.com', 'www.imagelay.com',
                 'www.flickr.com', 'imgip.com', 'tinypic.com', 'lolpics.se', 'pics.livejournal.com'}

# lower-cased set of image extensions
IMAGE_SUFFICES = {'.jpg', '.png', '.jpeg', '.gif'}


def is_image_url(url: str) -> bool:
    if url.lower().endswith("[/img]"):
        url = url[:-6]

    try:
        u = urlparse(url)
    except ValueError:
        log.info("Error parsing URL: %s", url)
        return False

    # check path suffix
    path = pathlib.Path(u.path)
    if path.suffix.lower() in IMAGE_SUFFICES:
        return True

    # some image hostings do not have file extension
    domain = u.netloc.lower()
    if domain in IMAGE_DOMAINS:
        return True

    return False


def parse_input_line(l: str) -> Optional[Tuple[str, str, str]]:
    """
    Parse the input line from data file
    :param l: input line
    :return: None if parse failed, or tuple with (reddit, text, url)
    """
    try:
        dat = json.loads(l)
        if len(dat) != 5:
            return None
        return tuple(dat[:3])
    except ValueError:
        pass
    return None

