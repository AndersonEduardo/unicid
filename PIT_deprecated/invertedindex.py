import Levenshtein
import os
import pandas as pd

from nltk.tokenize import word_tokenize
from parameters import *
from decisiontable import *


class InvertedIndex:

    def __init__(self) -> None:
        
        self.inverted_index = dict()
        self.stopwords = STOPWORDS
        self.microtoken = MICROTOKEN
        self.largetoken = LARGETOKEN


    def _reset_inverted_index(self) -> None:

        self.inverted_index = dict()


    def get_inverted_index(self, corpus:list, return_output:bool = False) -> dict:

        self._reset_inverted_index()

        for sentence in corpus:

            tokens = [x for x in word_tokenize(sentence.lower().strip()) if x not in self.stopwords]

            for key in tokens:
                
                if key not in self.inverted_index:

                    self.inverted_index[key] = {sentence}

                else:

                    self.inverted_index[key].update({sentence})

                # if len(key) > self.largetoken:

                #     for i in range(len(key)):

                #         if (i + self.microtoken) <= len(key):

                #             self.inverted_index[ key[i:(i + self.microtoken)] ] = { sentence }

        if return_output is True:

            return self.inverted_index


    def _get_synonyms_tokenized(self, sin_list:list) -> set:

        tokenized = set()

        for s in sin_list:

            tokenized.update({
                x 
                for x in word_tokenize(s) 
                if x not in STOPWORDS
            })

        return tokenized


    def _load_synonyms(self, synonyms_path:str = None) -> dict:

        if synonyms_path is None:
            
            synonyms_path = SYNONYMS_PATH


        filepaths = [os.path.join(synonyms_path, x) 
                    for x in os.listdir(synonyms_path)]

        synonyms_raw = dict()
        synonyms = dict()


        for filepath in filepaths:

            df = pd.read_excel(
                filepath, 
                usecols=['TERMO', 'SINÔNIMOS']
            )

            df['SINÔNIMOS_SPLIT'] = df.apply(
                lambda x: [w.strip().lower() 
                        for w in x['SINÔNIMOS'].strip().split(';')], 
                axis=1
            )

            synonyms_raw.update(
                df[['TERMO', 'SINÔNIMOS_SPLIT']].\
                    set_index('TERMO').\
                    transpose().\
                    to_dict(orient='records')[0]
            )


        for (k, v) in synonyms_raw.items():

            k_splitted = k.split()

            if len(k_splitted) > 1:

                for token in k_splitted:

                    synonyms.update({token.strip().lower(): set(v)})

            else:

                synonyms.update({k.strip().lower(): set(v)})


        del synonyms_raw

        return synonyms


    def add_synonyms(self, synonyms:dict = None) -> None:
        
        if synonyms is None:

            # synonyms = self._load_synonyms()
            raise NotImplementedError('For now, only implemented for direct input using a python dict.')

        for (sin_dict_key, sin_dict_val) in synonyms.items():

            sin_dict_val_tokenized = self._get_synonyms_tokenized(sin_dict_val)

            for token in sin_dict_val_tokenized:

                ii_labels = self.inverted_index.get(token)

                if ii_labels is None:

                    self.inverted_index.update({token: {sin_dict_key}})

                else:

                    self.inverted_index[token].update({sin_dict_key})


class LevenshteinBasedInvertedIndex(InvertedIndex):

    def __init__(self) -> None:

        self.k_output = set()
        self.top_k = TOP_K
        self.levenshtein_threshold = LEVENSHTEIN_THESHOLD
        super().__init__()


    def search(self, query:str, return_tokens:bool) -> list:

        k_output = None
        d_output = None
        query_tokenized = [x 
                           for x in word_tokenize(query.lower().strip()) 
                           if x not in self.stopwords]

        for k in self.inverted_index.keys():

            for query_token in query_tokenized:

                d = Levenshtein.distance(query_token, k)

                if k_output is None:

                    k_output = [k]
                    d_output = [d]
                    q_output = [query_token]

                else:

                    # este `top_k` eh para chaves do indice invertido, 
                    # e NAO para o output (i.e., `labels` no output).
                    if len(k_output) < self.top_k: 

                        k_output.append(k)
                        d_output.append(d)
                        q_output.append(query_token)

                    else:

                        if d <= max(d_output):

                            d_output.append(d)
                            k_output.append(k)
                            q_output.append(query_token)

                            idx_max = d_output.index(max(d_output))

                            d_output.pop(idx_max)
                            k_output.pop(idx_max)
                            q_output.pop(idx_max)

        if k_output is None:

            return pd.DataFrame(columns=['label', 'score', 'key', 'query_token'])
        
        elif len(k_output) == 0:
            
            return pd.DataFrame(columns=['label', 'score', 'key', 'query_token'])

        else:

            k_output_sorted = [(i,j,k) 
                for (i,j,k) in sorted(zip(d_output, k_output, q_output), reverse=False)]

            output_raw = [(self.inverted_index[j], i, j, k) 
                          for (i,j,k) in k_output_sorted]

            output = pd.DataFrame(columns=['label', 'score', 'key', 'query_token'])

            for (l,s,k,q) in output_raw:

                for l_ in l:

                    output = output.append({'label': l_, 
                                            'score': s,
                                            'key': k,
                                            'query_token': q}, ignore_index=True)

            # eliminando outputs duplicados e resetando o indice do dataframe
            output = output\
                        .reset_index(drop=True)\
                        # .drop_duplicates(subset='label')


        if return_tokens is True:

            return (query_tokenized, output)

        else:

            return output.reset_index(drop=True)


class Autocomplete:

    def autocomplete(self, age:str, sex:str, query:str) -> dict:

        lbii_clinical_indication = LevenshteinBasedInvertedIndex()
        lbii_subcategory = LevenshteinBasedInvertedIndex()
        clinical_indication_corpus = set()
        subcategory_corpus = set()

        dtab = DecisionTable(PARAMETERS)
        dtab.build()

        for i in range(len(dtab.rules)):

            if age == dtab.rules[i].get('IDADE') and sex == dtab.rules[i].get('SEXO'):

                clinical_indication_corpus.update({dtab.rules[i].get('INDICAÇÃO CLÍNICA')})
                subcategory_corpus.update({dtab.rules[i].get('SUBCATEGORIA')})

        lbii_clinical_indication.get_inverted_index(clinical_indication_corpus)
        lbii_subcategory.get_inverted_index(subcategory_corpus)

        query_output_clinical_indication = lbii_clinical_indication.search(query, return_tokens=False)
        query_output_subcategory = lbii_subcategory.search(query, return_tokens=False)

        query_output_clinical_indication['score'] = query_output_clinical_indication.apply(
            lambda x: min(1, 1 - x['score']/len(x['key'])), 
            axis=1
        )
        query_output_subcategory['score'] = query_output_subcategory.apply(
            lambda x: min(1, 1 - x['score']/len(x['key'])), 
            axis=1
        )

        query_output_clinical_indication = query_output_clinical_indication.pivot_table(
            index = 'label',
            columns = 'query_token',
            values = 'score',
            fill_value = 0
        )
        query_output_subcategory = query_output_subcategory.pivot_table(
            index = 'label',
            columns = 'query_token',
            values = 'score',
            fill_value = 0
        )

        clinical_indication_idx = query_output_clinical_indication\
            .apply(
                lambda x: all(x.values >= THESHOLD4LBII), 
                axis=1
            )\
            .values
        subcategory_idx = query_output_subcategory\
            .apply(
                lambda x: all(x.values >= THESHOLD4LBII), 
                axis=1
            )\
            .values

        query_output_clinical_indication = query_output_clinical_indication[clinical_indication_idx]
        query_output_subcategory = query_output_subcategory[subcategory_idx]

        query_output_clinical_indication = query_output_clinical_indication\
            .mean(axis=1)\
            .reset_index(drop=False)\
            .rename(columns={0:'score'})\
            .sort_values(by='score', ascending=False)
        query_output_subcategory = query_output_subcategory\
            .mean(axis=1)\
            .reset_index(drop=False)\
            .rename(columns={0:'score'})\
            .sort_values(by='score', ascending=False)

        clinical_indication_label = query_output_clinical_indication["label"].tolist()
        subcategory_label = query_output_subcategory["label"].tolist()


        return {
            'adherent_clinical_indication_labels': clinical_indication_label,
            'adherent_subcategory_labels': subcategory_label
        }
