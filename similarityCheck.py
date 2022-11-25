from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')

def coding_test():
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

def wordScore(word1, word2):
  embeddings1 = model.encode(word1, convert_to_tensor=True)
  embeddings2 = model.encode(word2, convert_to_tensor=True)

  #Compute cosine-similarities
  cosine_scores = util.cos_sim(embeddings1, embeddings2)

  return cosine_scores
  
  #Output the pairs with their score
  #print("{} \t\t {} \t\t Score: {:.4f}".format(word1, word2, cosine_scores[i][i]))