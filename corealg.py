# Core algorithm module
# An initial approach..
import re
import math
import porter2
import main

def Tokenize(text, stem):
    tokens = re.findall("[\w']+", text.lower())
    if stem:
        tokens = [porter2.stem(token) for token in tokens]
    return tokens

def EuclideanLength(v):
    sum_sqs = 0.0
    for term, val in v.iteritems():
        sum_sqs += (val**2)  
    return math.sqrt(sum_sqs)

def DotProduct(v1, v2):
    dot_prod = 0.0
    for term, val in v1.iteritems():
        # Assuming key-error proof! ... 
        dot_prod += val * v2[term]
    return dot_prod

def CosineSim(v1, v2):
    return DotProduct(v1, v2) / (EuclideanLength(v1) * EuclideanLength(v2))

class Scorer: 
    def __init__(self, user, friends):
        self.user = user
        self.friends = friends
        
        # Inverted indexes
        self.bio_index = {} # Key = term; val = dict with 3 keys: doc_ids (list of friends with this term), df, and idf   
        self.music_index = {} 
        self.movies_index = {}
        self.books_index = {}

        # The "corpuses": key = friend id; val = raw string of liked items as stored in DS
        self.bio_docs = {}
        self.music_docs = {}
        self.movies_docs = {}
        self.books_docs = {}

        # Friends' interests in weighted vector form
        # key=docid; val=dict with k=term, v=tf-idf score
        self.bio_vecs = {}
        self.music_vecs = {}
        self.movies_vecs = {}
        self.books_vecs = {}

    def GatherFriendsData(self): # fill friends_data dict, where key=id; val=full text of given attribute
        for friend in self.friends:
            self.bio_docs[friend.id] = friend.bio
            self.music_docs[friend.id] = friend.music
            self.movies_docs[friend.id] = friend.movies
            self.books_docs[friend.id] = friend.books

    def PrepareInvertedIndexes(self):
        self.PrepareInvertedIndex("bio_docs", "bio_index", True)    
        self.PrepareInvertedIndex("music_docs", "music_index", True)    
        self.PrepareInvertedIndex("movies_docs", "movies_index", True)    
        self.PrepareInvertedIndex("books_docs", "books_index", True)    

    def PrepareInvertedIndex(self, corpus_name, index_name, stem): # index_type string identifies whether bio, music, etc.
        inverted_index = getattr(self, index_name)   
        corpus = getattr(self, corpus_name) 
        
        for k, doc in corpus.items(): # k = assigned id number of doc (friend id in this case)
            if doc is not None:
                tokens = Tokenize(doc, stem)
            
                for s in tokens:
                    if s not in inverted_index: 
                        inverted_index[s] = {}
                        inverted_index[s]["doc_ids"] = []
                        inverted_index[s]["df"] = 0
                
                    if k not in inverted_index[s]["doc_ids"]:
                        inverted_index[s]["df"] += 1
                    inverted_index[s]["doc_ids"].append(k)

        # Store the idfs
        N = float(len(corpus))
        for term, val in inverted_index.items():
            inverted_index[term]["idf"] =  \
            math.log((N/float(inverted_index[term]["df"])), 2.0) 

    def MakeAllDocVectors(self):
        self.MakeDocVectorsForAttr("bio_docs", "bio_index", "bio_vecs")
        self.MakeDocVectorsForAttr("music_docs", "music_index", "music_vecs")
        self.MakeDocVectorsForAttr("movies_docs", "movies_index", "movies_vecs")
        self.MakeDocVectorsForAttr("books_docs", "books_index", "books_vecs")

    def MakeDocVectorsForAttr(self, corpus_name, index_name, vecs_name):
        inverted_index = getattr(self, index_name)
        vectors = getattr(self, vecs_name)
        for k in getattr(self, corpus_name).keys():
            vectors[k] = {}
            for term in inverted_index:
                raw_tf = inverted_index[term]["doc_ids"].count(k)
                weighted_tf = 0.0
                if raw_tf > 0:
                    weighted_tf = 1.0 + math.log(float(raw_tf), 2.0)
                vectors[k][term] = weighted_tf * inverted_index[term]["idf"] 

    def DoRanking(self):
        for friend in self.friends:
            print "FRIEND------" + str(friend.name)
            mutual_fields = 0
            overall_sim = 0.0
            # condense this...?
            bio_sim = 0.0
            if self.user["bio"] is not None and friend.bio is not None:
                mutual_fields += 1
                # Building queries with raw tfs
                bio_qry = dict.fromkeys(self.bio_index, 0)
                for token in Tokenize(self.user["bio"], True):
                    if token in self.bio_index:
                        bio_qry[token] += 1            
                bio_sim = CosineSim(bio_qry, self.bio_vecs[friend.id])    
                print "BIO SIM: " + str(bio_sim)           
 
            music_sim = 0.0
            if self.user["music"] is not None and friend.music is not None:
                mutual_fields += 1
                music_qry = dict.fromkeys(self.music_index, 0)
                for token in Tokenize(self.user["music"], True):
                    if token in self.music_index:
                        music_qry[token] += 1            
                music_sim = CosineSim(music_qry, self.music_vecs[friend.id])    
                print "MUSIC SIM: " + str(music_sim)

            movies_sim = 0.0
            if self.user["movies"] is not None and friend.movies is not None:
                mutual_fields += 1
                movies_qry = dict.fromkeys(self.movies_index, 0)
                for token in Tokenize(self.user["movies"], True):
                    if token in self.movies_index:
                        movies_qry[token] += 1
                movies_sim = CosineSim(movies_qry, self.movies_vecs[friend.id])    
                print "MOVIES SIM: " + str(movies_sim)            
            
            books_sim = 0.0
            if self.user["books"] is not None and friend.books is not None:
                mutual_fields += 1
                books_qry = dict.fromkeys(self.books_index, 0)
                for token in Tokenize(self.user["books"], True):
                    if token in self.books_index:
                        books_qry[token] += 1
                books_sim = CosineSim(books_qry, self.books_vecs[friend.id])    
                print "BOOKS SIM: " + str(books_sim)            
                    
           
            if mutual_fields > 0:
                overall_sim = (1.0 / mutual_fields) * (bio_sim + music_sim + movies_sim + books_sim)
            print "OVERALL SIM SCORE FOR " + str(friend.name) + ": " + str(overall_sim)
            print "---------------------------------------------"

