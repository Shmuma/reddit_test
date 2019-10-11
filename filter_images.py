#!/usr/bin/env python3
import csv
import sys
import tqdm
import json

import argparse
import logging
import collections
import pathlib
from typing import Tuple, Optional

from spacy.lang.en import English

from lib import data, utils

log = logging.getLogger("filter_images")

EXPECTED_LINES = 206669601


def handle_line(l: str, tokenizer) -> Optional[Tuple[bool, str, str, str, str]]:
    """
    Concurrent job to process the input line
    :param l: input line
    :return: Tuple with (is_image, reddit, text, text_parsed, url)
    """
    parsed_l = data.parse_input_line(l)
    if parsed_l is None:
        return None
    reddit, text, url = parsed_l
    if not data.is_image_url(url):
        return False, reddit, text, text, url

    doc = tokenizer(text)
    tokens = [t.lower_ for t in doc]
    text_parsed = " ".join(tokens)
    return True, reddit, text, text_parsed, url


if __name__ == "__main__":
    utils.setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", default=data.DEFAULT_DATA_FILE,
                        help="Data file to read, default=" + data.DEFAULT_DATA_FILE)
    parser.add_argument("-o", "--output", default=data.DEFAULT_OUTPUT_PREFIX,
                        help="Output data prefix to produce. Suffixes will be added "
                             "to this path, default=" + data.DEFAULT_OUTPUT_PREFIX)
    parser.add_argument("--limit", type=int, help="Optional limit of input lines to process, default=No limit")
    args = parser.parse_args()

    # using only tokenizer from spacy, this is much faster
    nlp = English()
    tokenizer = nlp.Defaults.create_tokenizer(nlp)

    data_path = pathlib.Path(args.data)
    output_path = pathlib.Path(args.output)

    reddit_index = collections.defaultdict(list)
    next_image_id = 0
    count_rows = 0
    count_images = 0
    count_failed = 0
    count_skipped = 0

    with output_path.with_suffix(".csv").open("wt", encoding='utf-8') as out_fd:
        with output_path.with_suffix(".txt").open("wt", encoding='utf-8') as out_text_fd:
            output_writer = csv.writer(out_fd)
            output_writer.writerow(["id", "reddit", "text", "url"])

            with data_path.open("rt", encoding='utf-8') as fd:
                for input_idx, l in enumerate(tqdm.tqdm(fd, total=EXPECTED_LINES, file=sys.stdout)):
                    count_rows += 1
                    if args.limit is not None and input_idx >= args.limit:
                        log.info("Limit of input rows has reached, stopping")
                        break

                    parsed_l = data.parse_input_line(l)
                    if parsed_l is None:
                        log.warning("Parse error: %s", l)
                        count_failed += 1
                        continue
                    reddit, text, url = parsed_l
                    if not data.is_image_url(url):
                        count_skipped += 1
                        continue

                    reddit_index[reddit].append(next_image_id)
                    output_writer.writerow([next_image_id, reddit, text, url])

                    doc = tokenizer(text)
                    tokens = [t.lower_ for t in doc]
                    text_parsed = " ".join(tokens)
                    out_text_fd.write(text_parsed + "\n")
                    next_image_id += 1
                    count_images += 1

    log.info("Processed %d rows, %d failed, %d skipped. Found %d images in %d reddits",
             count_rows, count_failed, count_skipped, count_images, len(reddit_index))

    with output_path.with_suffix(".reddit.index").open("wt", encoding='utf-8') as out_fd:
        json.dump(reddit_index, out_fd)
