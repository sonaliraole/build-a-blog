#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)



def get_posts(limit, offset):
    sql_string = ("SELECT * FROM Post ORDER BY created DESC LIMIT " + str(limit)
        + " OFFSET " + str(offset))
    posts = db.GqlQuery(sql_string)
    return posts


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        self.redirect('/blog')

class BlogPage(Handler):
    def get(self):
        more = "N"
        page = self.request.get("page")

        if page == "":
            page = 1
        else:
            page = int(page)

        posts = get_posts(5, (page - 1) * 5)

        if(posts.count(limit = 5, offset=(page*5)) > 0):
            more = "Y"
        self.render("index.html", posts=posts, error="", more=more, page=page)

class NewPost(Handler):
     def get(self):
         self.render("add.html", title="", body="", error="")

     def post(self):
         title = self.request.get("title")
         body = self.request.get("body")

         if title and body :
             newpost = Post(title=title, body=body)
             newpost.put()
             blog_post_id = str(newpost.key().id())
             self.redirect("/blog/" + blog_post_id)
         else:
             error = "Please enter both title and body"
             self.render("add.html", title=title, body=body, error=error)

class ViewPostHandler(Handler):
     def get(self, id):
        a = Post.get_by_id(int(id))
        self.render("permalink.html", post = a)




app = webapp2.WSGIApplication([
      ('/', MainPage),
      ('/blog', BlogPage),
      ('/newpost', NewPost),
      webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug=True)    
