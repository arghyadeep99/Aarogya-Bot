# Quora Question Pair

This is an attempt at the kaggle's quora question pair duplication recognition problem.

## Approach

Approach is to use Siamese network. Let the embeddings of two questions be passed through the same network and then concatenate them and apply sigmoid at the end to get an output.
For embeddings, GloVe embeddings have been used.

**Why the Siamese network?**
A siamese network is when two different inputs go through the exact same neural network and finally the end-feature vectors that come out of them are merged or compared.
In face recognition, a siamese network is often used to tell if two face pictures are of the same person or different persons. Here, once we'll have embeddings of the text, we could use a similar approach.

## Project Structure

`predict.py` : To make a prediction

`train_model.py` : To train the model

`quora-question-pairs.ipynb` : The jupyter notebook that contains all the steps I followed to finally create the model

`dictionary.json` : This contains word indices built from tokenizing all the questions in the training set

`train.csv` : The training file provided

`requirements.txt` : For installing all requirements to run this project

`model.json` : The keras model which is finally used. This is loaded when you run predict.py

The weights file is available [here](https://drive.google.com/open?id=1-96-hj0tDjoLXW4wESu7LTRrC-t4iiX6). After downloading, put it in the same directory as these files. 

## How to run?

### Installation

`pip install -r requirements.txt`

### Training

It may take a while. This is not required as I've provided the [weights file](https://drive.google.com/open?id=1-96-hj0tDjoLXW4wESu7LTRrC-t4iiX6) and you could just use that and directly use predict.py to make a prediction.

`python train_model.py`

### Predicting

The file `predict.py` has been made as a CLI tool. So, you could type `python predict.py --help` and it would return you all the commands and options you can have.
Right now, it is super-limited (read hardcoded). This will change in future though to allow for custom model and custom weights to be used.

`python predict.py find_if_duplicate_questions --ques1 "What's R programming?" --ques2 "What's R in programming?"`

## How it can improve?

1. For the reasons of training take a long time, I reduced the number and types of layers in the architecture. Ideally, if we could add another shared LSTM and dropout and then have a bunch of groups of [Dense, Dropout, BatchNormalization] layers then that would probably improve the model by a lot.
2. Instead of concatenating the final feature vectors of both, find dot product / cosine similarity between them and let that be last layer
3. Train for more epochs. I was able to train only for 10 epochs as that itself took a long time.

## Author

Bhavul Gauri
