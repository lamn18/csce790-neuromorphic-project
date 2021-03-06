import json
import math
import pandas as pd

CW_PATH = 'data/curated_words.xlsx'
DOCS_PATH = 'data/lemma_docs.xlsx'
OUT_PATH = 'data/tf_idf.xlsx'

curated_freq = pd.read_excel(CW_PATH, engine='openpyxl')
curated_freq = curated_freq.set_index('word')

# Come back and make sure to include labelling column in the future
docs = pd.read_excel(DOCS_PATH, engine='openpyxl', usecols=['vid_id', 'class', 'word_counts'])

docs['tf_idf'] = ''

curated_words = curated_freq.index.unique()

err_count = 0
'''
Based off of:
https://towardsdatascience.com/tf-term-frequency-idf-inverse-document-frequency-from-scratch-in-python-6c2b61b78558
'''
def calc_tf_idf(row):

    global err_count

    tf_idf = {}
    try:
        # Comment out until '# ---' after fixing errors in previous scripts
        word_counts_str = row.word_counts
        word_counts_str = [char for char in word_counts_str]
        edit = False
        for a in range(0, word_counts_str.__len__()):
            if not edit:
                if word_counts_str[a] == '"':
                    word_counts_str[a] = '\''
                    edit = True
            else:
                if word_counts_str[a] == '\'':
                    word_counts_str[a] = '_'
                elif word_counts_str[a] == '"':
                    word_counts_str[a] = '\''
                    edit = False
        # ---
        word_counts_str = ''.join(word_counts_str)
        word_counts = word_counts_str.replace('\'', '"')
        word_counts_dict = json.loads(word_counts)
        for word in curated_words:
            if word in word_counts_dict:
                tf = word_counts_dict[word]
                idf = round(math.log((1 + docs.shape[0])/(1 + curated_freq.loc[word].vid_count)) + 1, 5)
                tf_idf[word] = tf * idf
            else:
                tf_idf[word] = 0
        # Remove all keys that are 0
        tf_idf = {x:y for x,y in tf_idf.items() if y!=0}
        row['tf_idf'] = json.dumps(tf_idf).replace(' ', '')
    except Exception as e:
        # Most of the errors are due to escape characters
        err_count += 1
    return row

def main():

    global docs

    print('Calculating the TF-IDF for corpora... (This may take a while...)')
    docs = docs.apply(lambda row: calc_tf_idf(row), axis=1)
    print('Failed attempt at calculating TF-IDF for {}/{} corpus'.format(err_count, docs.shape[0]))

    # Remove rows where the failed tf_idf occured
    docs = docs[~(docs.tf_idf == '')]

    print('Saving data...')
    docs.to_excel(OUT_PATH, index=False)

if __name__ == '__main__':
    
    print('Starting vectorize_tf_idf...')
    main()
    