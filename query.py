#!/usr/bin/env python3
import logging
import argparse

from lib import utils, model, data

from fse import IndexedLineDocument
from fse.models import SIF
from fse.models.utils import compute_principal_components

import gensim.downloader as api
from spacy.lang.en import English

log = logging.getLogger("query")


if __name__ == "__main__":
    utils.setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", default=data.DEFAULT_OUTPUT_PREFIX + ".csv",
                        help="CSV file with data, default=" + data.DEFAULT_OUTPUT_PREFIX + ".csv")
    parser.add_argument("-m", "--model", default=model.DEFAULT_MODEL_FILE,
                        help="File with model to load, default=" + model.DEFAULT_MODEL_FILE)
    args = parser.parse_args()

    glove = api.load("glove-wiki-gigaword-100")
    model = SIF(glove)
    model = model.load(args.model)
    # workaround before the issue fixed https://github.com/oborchers/Fast_Sentence_Embeddings/issues/12
    model.svd_res = compute_principal_components(model.sv.vectors, components=model.components)

    log.info("Loading sentence data from %s", args.data)
    data = IndexedLineDocument(args.data)
    log.info("Loaded")

    nlp = English()
    tokenizer = nlp.Defaults.create_tokenizer(nlp)

    print("Enter reddit topic to find 20 most similiar topics from 66M in DB")

    while True:
        q = input("> ")
        tokens = [t.lower_ for t in tokenizer(q)]
        print(tokens)
        sim = model.sv.similar_by_sentence(tokens, model=model)
        for idx, score in sim:
            row = data[idx+1]
            print("  * %.3f: %s" % (score, row))

