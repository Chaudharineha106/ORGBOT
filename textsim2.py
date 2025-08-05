import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

def count_matching_words(sentence1, sentence2):
    # Tokenize the sentences
    tokens1 = word_tokenize(sentence1.lower())
    tokens2 = word_tokenize(sentence2.lower())
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens1 = [word for word in tokens1 if word not in stop_words]
    tokens2 = [word for word in tokens2 if word not in stop_words]
    
    # Count matching words
    #print(tokens1)
    #print(tokens2)

    matching_words = set(tokens1) & set(tokens2)
    
    return len(matching_words)

sentence1 = "This is a sentence."
sentence2 = "This is another sentence sentence."

matching_words_count = count_matching_words(sentence1, sentence2)
print("Number of matching words:", matching_words_count)