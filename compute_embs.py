#!/usr/bin/env python3
import argparse
import csv
import sys
import tqdm
import json
import logging
import collections
import pathlib
from spacy.lang.en import English

from lib import data, utils

log = logging.getLogger("compute_embs")

EXPECTED_LINES = 66836199


def calc_token_counts(nlp, input_path: pathlib.Path) -> collections.Counter:
    tokenizer = nlp.Defaults.create_tokenizer(nlp)
    token_counts = collections.Counter()

    with input_path.open('rt', encoding='utf-8') as fd:
        reader = csv.DictReader(fd)
        for idx, row in enumerate(tqdm.tqdm(reader, total=EXPECTED_LINES, file=sys.stdout)):
            if args.limit is not None and idx >= args.limit:
                log.info("Limit of input rows has reached, stopping")
                break

            doc = tokenizer(row['text'])
            for t in doc:
                token_counts[t.lower_] += 1
    return token_counts


if __name__ == "__main__":
    utils.setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", default=data.DEFAULT_OUTPUT_PREFIX,
                        help="Prefix of input data to read, default=" + data.DEFAULT_OUTPUT_PREFIX)
    parser.add_argument("--cache-probs", help="If specified, word probabilities will be cached in this file")
    parser.add_argument("--limit", type=int, help="Optional limit of input lines to process, default=No limit")
    args = parser.parse_args()
    nlp = English()

    input_path = pathlib.Path(args.data).with_suffix(".csv")
    count_tokens = 0
    count_no_embs = 0

    if args.cache_probs is not None:
        cache_path = pathlib.Path(args.cache_probs)
        if cache_path.exists():
            token_counts = json.loads(cache_path.read_text(encoding='utf-8'))
        else:
            token_counts = calc_token_counts(nlp, input_path)
            cache_path.write_text(json.dumps(token_counts), encoding='utf-8')
    else:
        token_counts = calc_token_counts(nlp, input_path)
