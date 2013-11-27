#!/usr/bin/env python
"""
Use this file to demo the core algorithm. (For checkpoint 3.)
"""

import corealg

class User():
    def __init__(self, _id, _name, _profile_url, _bio, _music, _movies, _books, _access_token):
        self.id = _id
        self.name = _name
        self.profile_url = _profile_url
        self.bio = _bio
        self.music = _music
        self.movies = _movies
        self.books = _books
        self.access_token = _access_token

class Friend():
    def __init__(self, _id, _name, _profile_url, _bio, _music, _movies, _books):
        self.id = _id
        self.name = _name
        self.profile_url = _profile_url
        self.bio = _bio
        self.music = _music
        self.movies = _movies
        self.books = _books

if __name__=="__main__":
    user = User(
            0,
            "James Caverlee",
            "caverlee.com",
            "Aaron and Nicole are my favorite students ever.",
            "Miley Cyrus, One Direction, Nickleback, Rebecca Black, Justin Bieber",
            "Space Jam, The Notebook, Twilight",
            "Twilight, 50 Shades of Gray",
            "token"
            );

    friends = []
    friends.append(Friend(
            "1",
            "Cav Friend 1",
            "cavfriend1.com",
            "Aaron and Nicole are Cav's favorite students.",
            "Miley Cyrus, Rececca Black",
            "Space Jam",
            "50 Shades of Gray"
            ));
    friends.append(Friend(
            "2",
            "Cav Friend 2",
            "cavfriend2.com",
            "I like fishing and boating and long walks on the beach.",
            "Red Hot Chili Peppers",
            "The Hobbit, The Hunger Games",
            "Harry Potter, The Cat In the Hat",
            ));
    friends.append(Friend(
            "3",
            "Cav Friend 3",
            "cavfriend3.com",
            "Bob and Joe are Cav's favorite students.",
            "Miley Cyrus, Elton John",
            "Twilight, The Hunger Games",
            "Twilight, The Bible",
            ));

    scorer = corealg.Scorer(user, friends)
    scorer.GatherFriendsData()
    scorer.PrepareInvertedIndexes()
    scorer.MakeAllDocVectors()
    rankings = sorted(scorer.DoRanking(), reverse=True)
    scores = [r[0] for r in rankings]
    names = [r[1].name for r in rankings]
    print "Rankings for " + user.name + ":"
    print "Name\tSimilarity"
    print "----------------------"
    for i in range(len(rankings)):
        print names[i] + '\t' + str(scores[i])

