from sentence_transformers import SentenceTransformer, util
from nltk import sent_tokenize
import numpy as np

def coding_test():
    #model = SentenceTransformer('all-MiniLM-L6-v2')
    model = SentenceTransformer('bert-base-nli-mean-tokens')
  
  # Two lists of sentences
    sentences1 = ['dog',
                'cat',
                'cat',
                'kitten']

    sentences2 = ['puppy',
                  'kitten',
                  'dog',
                  'puppy']

    #Compute embedding for both lists
    embeddings1 = model.encode(sentences1, convert_to_tensor=True)
    embeddings2 = model.encode(sentences2, convert_to_tensor=True)

    #Compute cosine-similarities
    cosine_scores = util.cos_sim(embeddings1, embeddings2)

    #Output the pairs with their score
    for i in range(len(sentences1)):
        print("{} \t\t {} \t\t Score: {:.4f}".format(sentences1[i], sentences2[i], cosine_scores[i][i]))

def wordScore(word1, word2, model):
    if model == 'bert':
      model = SentenceTransformer('bert-base-nli-mean-tokens')
    else:
      model = SentenceTransformer('all-MiniLM-L6-v2')

    cosine_scores = []

    # Make word 1 to be an equal length to word 2
    word1_arr = [word1] * len(word2)

    embeddings1 = model.encode(word1_arr)
    embeddings2 = model.encode(word2)

    # compute cosine_scores
    cosine_matrix = util.cos_sim(embeddings1, embeddings2)
    cosine_scores = cosine_matrix.diagonal()

    # convert the tensor array to a list and return
    return cosine_scores.tolist()