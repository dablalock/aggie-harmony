#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
A barebones AppEngine application that uses Facebook for login.

1.  Make sure you add a copy of facebook.py (from python-sdk/src/)
    into this directory so it can be imported.
2.  Don't forget to tick Login With Facebook on your facebook app's
    dashboard and place the app's url wherever it is hosted
3.  Place a random, unguessable string as a session secret below in
    config dict.
4.  Fill app id and app secret.
5.  Change the application name in app.yaml.

"""

import facebook
import auth
import webapp2
import os
import jinja2
import urllib2

from google.appengine.ext import db
from webapp2_extras import sessions

config = {}
config['webapp2_extras.sessions'] = dict(secret_key=auth.SESSION_SECRET)


class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)

    @property
    def friends(self):
        return Friend.gql("WHERE users = :1", self.key())

class Friend(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    bio = db.StringProperty()
    music = db.StringProperty()
    movies = db.StringProperty()
    books = db.StringProperty()
    users = db.ListProperty(db.Key)

class BaseHandler(webapp2.RequestHandler):
    """Provides access to the active Facebook user in self.current_user

    The property is lazy-loaded on first access, using the cookie saved
    by the Facebook JavaScript SDK to determine the user ID of the active
    user. See http://developers.facebook.com/docs/authentication/ for
    more information.
    """
    @property
    def current_user(self):
        if self.session.get("user"):
            # User is logged in
            return self.session.get("user")
        else:
            # Either used just logged in or just saw the first page
            # We'll see here
            cookie = facebook.get_user_from_cookie(self.request.cookies,
                                                   auth.FACEBOOK_APP_ID,
                                                   auth.FACEBOOK_APP_SECRET)
            if cookie:
                # Okay so user logged in.
                # Now, check to see if existing user
                user = User.get_by_key_name(cookie["uid"])
                if not user:
                    # Not an existing user so get user info
                    graph = facebook.GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    user = User(
                        key_name=str(profile["id"]),
                        id=str(profile["id"]),
                        name=profile["name"],
                        profile_url=profile["link"],
                        access_token=cookie["access_token"]
                    )
                    user.put()

                    # Store the user's friends
                    friendz = graph.get_connections("me", "friends", 
                        fields="name,link,gender,bio,education,relationship_status")
                    for friend in friendz["data"]:
                        # For now, don't bother constructing friend unless A&M student 
                        # and not already in relationship. Non-provided relationship
                        # assumed single!
                        #if facebook.feasible_friend(friend["education"], friend["relationship_status"]):
                        if facebook.feasible_friend(friend["education"]): # keyerror on rel_status?!?
                            f = Friend.gql("WHERE id = :1", str(friend["id"])).get()
                            if not f:
                                f = Friend(
                                    key_name=str(friend["id"]),
                                    id=str(friend["id"]),
                                    name=friend["name"],
                                    profile_url=friend["link"],
                                    bio=friend["bio"],
                                    music = facebook.make_conn_str(graph.get_connections(
                                        friend["id"], "music", fields="id,name")), 
                                    movies = facebook.make_conn_str(graph.get_connections(
                                        friend["id"], "movies", fields="id,name")), 
                                    books = facebook.make_conn_str(graph.get_connections(
                                        friend["id"], "books", fields="id,name")), 
                                    users=[]
                                )
                            f.users.append(user.key())
                            f.put()                

                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                # User is now logged in
                self.session["user"] = dict(
                    name=user.name,
                    profile_url=user.profile_url,
                    id=user.id,
                    access_token=user.access_token
                )
                return self.session.get("user")
        return None

    def dispatch(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        return self.session_store.get_session()


class HomeHandler(BaseHandler):
    def get(self):
        user = self.current_user
        friends = None
        if user:
            u = User.gql("WHERE id = :1", user["id"]).get()
            friends = u.friends.fetch(limit=10)
        template = jinja_environment.get_template('main.html')
        self.response.out.write(template.render(dict(
            facebook_app_id=auth.FACEBOOK_APP_ID,
            current_user=user,
            friends=friends
        )))


class LogoutHandler(BaseHandler):
    def get(self):
        if self.current_user is not None:
            self.session['user'] = None

        self.redirect('/')

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

app = webapp2.WSGIApplication(
    [('/', HomeHandler), ('/logout', LogoutHandler)],
    debug=True,
    config=config
)
