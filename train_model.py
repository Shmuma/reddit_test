#!/usr/bin/env python3
import argparse
import logging
import pathlib
from fse import IndexedLineDocument
from fse.models import SIF

from lib import data, utils, model
import gensim.downloader as api

log = logging.getLogger("train_model")

EXPECTED_LINES = 66836199


if __name__ == "__main__":
    utils.setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", default=data.DEFAULT_OUTPUT_PREFIX,
                        help="Prefix of input data to read, default=" + data.DEFAULT_OUTPUT_PREFIX)
    parser.add_argument("-o", "--output", default=model.DEFAULT_MODEL_FILE,
                        help="File name to save model, default=" + model.DEFAULT_MODEL_FILE)
    args = parser.parse_args()

    glove = api.load("glove-wiki-gigaword-100")
    input_path = pathlib.Path(args.data).with_suffix(".txt")
    sents = IndexedLineDocument(str(input_path))
    model = SIF(glove, workers=2)
    model.train(sents)
    model.save(args.output)
