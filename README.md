# Reddit images similarity using FSE

First idea was to use BERT, but when I calculated target embeddings size for 66M images and time to 
calculate the embeddings, I decided to use something faster. But the original idea might be not that bad, just 
my hardware is too small :).

## Overview

Input data has the form of reddit topics and urls
```json
["skeptic","袋泡茶\n","http://www.gooddaysco.com/","/r/skeptic/comments/eut3o/袋泡茶/","t3_eut3o"]
["funny","Wut?","http://imgur.com/BKdge","/r/funny/comments/euswo/wut/","t3_euswo"]
["reddit.com","Microwave is happy to see you.","http://imgur.com/SS8Az","/r/reddit.com/comments/euswn/microwave_is_happy_to_see_you/","t3_euswn"]
["reddit.com","Found this in a flee market.","http://i.imgur.com/SztJH.jpg","/r/reddit.com/comments/euswl/found_this_in_a_flee_market/","t3_euswl"]
["funny","Camel Shows - Cameltoe Helper ","http://ididafunny.com/index.php/2011/01/01/camel-shows-kelly-brooks-cameltoe-helper/","/r/funny/comments/euswj/camel_shows_cameltoe_helper/","t3_euswj"]
```

* Images got filtered and text is preprocessed using the tool `data_prepare.py`
* FSE model is created using `train_model.py`
* Query could be made using `query.py`

## Data cleanup

Utility `data_prepare.py` expects the data to be in `data/safe_links_all` (but you can redefine it using command line).
In my case there are 206M rows in the input file.

Images are filtered using extension and small db of image hostings (which could be made better, of course), 
resulting data is stored in several files:
* images.csv: csv file with row ID, reddit, text and url columns
* images.reddit.index: json file with mapping reddit -> row id
* images.txt: tokenized text, one row per line

Spacy english tokenizer used for tokenisation (without models for performance).
Resulting dataset is 66M records.

## Model creation

To compute sentence embeddings I've used FSE package from here: https://github.com/oborchers/Fast_Sentence_Embeddings

It implements Smooth Inverse Frequency methods, details could be found here: https://towardsdatascience.com/fse-2b1ffa791cf9

Anyways, utility `train_model.py` loads the data and builds the SIF model which is stored in `model.dat` file.
It takes about 15-20 minutes and requires 25-30GB of memory.

For word embeddings, pretrained glove vectors were used.

## Query

Once the model is created, it could be queried using `query.py` tool. It loads the sentence embeddings
and allows the user to type the query, which is being tokenized and top10 most similiar texts from the model is being 
queried.

No filtering on reddit is implemented, but it will be fairly simple thing to do.

Below is the example of `query.py` in action.

```bash
2019-10-13 11:38:05,581 INFO query Loading sentence data from data/images.csv
2019-10-13 11:38:58,896 INFO query Sentences loaded, loading model...
2019-10-13 11:38:59,865 INFO gensim.models.utils_any2vec loading projection weights from /home/shmuma/gensim-data/glove-wiki-gigaword-100/glove-wiki-gigaword-100.gz
2019-10-13 11:39:27,768 INFO gensim.models.utils_any2vec loaded (400000, 100) matrix from /home/shmuma/gensim-data/glove-wiki-gigaword-100/glove-wiki-gigaword-100.gz
2019-10-13 11:39:27,769 INFO gensim.utils loading SIF object from small.dat
2019-10-13 11:39:29,683 INFO gensim.utils loading wv recursively from small.dat.wv.* with mmap=None
2019-10-13 11:39:29,683 INFO gensim.utils loading vectors from small.dat.wv.vectors.npy with mmap=None
2019-10-13 11:39:30,744 INFO gensim.utils loading sv recursively from small.dat.sv.* with mmap=None
2019-10-13 11:39:30,745 INFO gensim.utils loading vectors from small.dat.sv.vectors.npy with mmap=None
2019-10-13 11:39:31,281 INFO gensim.utils loading prep recursively from small.dat.prep.* with mmap=None
2019-10-13 11:39:31,281 INFO gensim.utils loaded small.dat
2019-10-13 11:39:32,054 INFO fse.models.utils computing 1 principal components took 0s
Enter reddit topic to find 20 most similiar topics from 66M in DB
> something funny
['something', 'funny']
2019-10-13 11:40:28,691 INFO fse.models.base_s2v scanning all indexed sentences and their word counts
2019-10-13 11:40:28,692 INFO fse.models.base_s2v finished scanning 1 sentences with an average length of 2 and 2 total words
2019-10-13 11:40:28,692 INFO fse.models.sif no removal of principal components
2019-10-13 11:40:28,693 INFO fse.models.sentencevectors precomputing L2-norms of sentence vectors
  * 0.621: 6890,4chan,you so funny /b/,http://imgur.com/MyHh9
  * 0.608: 21902,pics,Mildly Funny?,http://imgur.com/nRNxU.png
  * 0.592: 157742,IDAP,and its a 7ft long tank,http://imgur.com/a/WBibu
  * 0.589: 53950,MCNSA,"My apology for being on every day, ever wonder what makes me want cancer just so I can abuse Make a Wish Foundation?",http://i.imgur.com/eyhpu.jpg
  * 0.589: 147072,funny,Something I found in a grocery store when I was in India,http://img198.imageshack.us/img198/618/imgp1563j.jpg
  * 0.572: 79284,nfl,I'm fairly certain this man is planning to unleash Hell on Sunday.,http://i.imgur.com/25kMd.jpg
  * 0.565: 73137,fffffffuuuuuuuuuuuu,Vending machine challenge.,http://imgur.com/gbfPX
  * 0.558: something funny or relatable.  ",http://i.imgur.com/k4kCo.png
  * 0.541: 42881,atheism,Just something I thought was funny,http://i.imgur.com/ofjzo.jpg
  * 0.539: 130773,trees,Obligatory. Haaaaaw Yeah!,http://i.imgur.com/YsD0t.jpg
Enter reddit topic to find 20 most similiar topics from 66M in DB
> new year
['new', 'year']
2019-10-13 11:44:50,815 INFO fse.models.base_s2v scanning all indexed sentences and their word counts
2019-10-13 11:44:50,816 INFO fse.models.base_s2v finished scanning 1 sentences with an average length of 2 and 2 total words
2019-10-13 11:44:50,816 INFO fse.models.sif no removal of principal components
2019-10-13 11:44:50,817 INFO fse.models.sentencevectors precomputing L2-norms of sentence vectors
  * 0.555: 14934,pics,New Year Photobomb,http://imgur.com/D9Wtq
  * 0.494: 1663,fffffffuuuuuuuuuuuu,Every New Year,http://i.imgur.com/AFcKD.jpg
  * 0.491: 268,gifs,"new year, new life",http://i.imgur.com/TfZlN.gif
  * 0.488: 149879,trees,I painted the dream i had last night. Enjoy fellow ents,http://i.imgur.com/dtewG.jpg
  * 0.478: 2582,pics,Every New Year's,http://i.imgur.com/Zj4UI.png
  * 0.478: 1329,trees,Bringing In The New Year,http://i.imgur.com/vLjDo.jpg
  * 0.469: 2265,fffffffuuuuuuuuuuuu,Goddammit new year.,http://i.imgur.com/agZyz.jpg
  * 0.467: 2540,windowshots,Happy New Year from NYC,http://imgur.com/HjyXm
  * 0.467: 3531,pics,"New year, new lighter",http://i.imgur.com/KwO5T.jpg
  * 0.463: 4034,fffffffuuuuuuuuuuuu,first thing new year's day.,http://i.imgur.com/j8EQf.jpg
``` 

## Further steps

Tons of improvements could be made, both in functionality and efficiency. But it took some time, so, I'd prefer 
to keep it short. 

* custom embeddings could be trained, dataset is large enough for that
* image contents could be used (but will require fetching 66M of images, which might become a separate project)
* moar features in the query
* etc, etc
