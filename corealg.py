# Core algorithm module
# An initial approach..
import re
import math
import porter2

class Scorer: 
    def __init__(self, user, data_type):
        self.user = user
        self.data_type = data_type #string
        self.friends_data ={} # corpus to search over
        self.inverted_index = {} # Key = term; val = dict with 3 
                                 # keys: df, idf, and list of doc ids

        #self.stop_list = [] # for optional stop list checks?
        self.friend_vecs = {}  # key=docid; val=dict with k=term, v=tf-idf score

    def GatherFriendsData(self): # fill friends_data dict, where key=id; val=full text of given attribute
        wtf = getattr(self.user, self.data_type)
        print "WTF?!?! " + str(wtf)
        print str(dir(self.user))
        for friend in self.user.friends:
            print "LOLOLOL"
            print str(dir(friends))
            self.friends_data[friend.id] = getattr(friend, self.data_type)
        print "gather friends data..."
        print self.friends_data

    def PrepareInvertedIndex(self, stem):
        for k, doc in self.friends_data.items(): # k = assigned id number of doc
            tokens = re.findall("[\w']+", doc.lower())
            if stem:
                tokens = [porter2.stem(token) for token in tokens]
            #if remove_stops:
            #    tokens = [st for st in tokens if st not in self.stop_list]
            
            for s in tokens:
                if s not in self.inverted_index: 
                    self.inverted_index[s] = {}
                    self.inverted_index[s]["doc_ids"] = []
                    self.inverted_index[s]["df"] = 0
                
                if k not in self.inverted_index[s]["doc_ids"]:
                    self.inverted_index[s]["df"] += 1
                self.inverted_index[s]["doc_ids"].append(k)

        # Store the idfs
        N = float(len(self.friends_data))
        for term, val in self.inverted_index.items():
            self.inverted_index[term]["idf"] =  \
            math.log((N/float(self.inverted_index[term]["df"])), 2.0) 
        print "################### II ################"
        print self.inverted_index


