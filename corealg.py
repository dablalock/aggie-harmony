# Core algorithm module
# An initial approach..
import re
import math
import porter2
import main

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
                tokens = re.findall("[\w']+", doc.lower())
                if stem:
                    tokens = [porter2.stem(token) for token in tokens]
            
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
        print "################### Inverted Index for " + str(corpus_name) +" ################"
        print inverted_index


