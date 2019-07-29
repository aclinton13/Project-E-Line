import os
import webapp2
import jinja2


jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__))
)

from google.appengine.ext import ndb
from google.appengine.api import users

class Information(ndb.Model):
    name = ndb.StringProperty(required=True)
    location = ndb.StringProperty(required=True)
    number = ndb.IntegerProperty(required=True)

class Person(ndb.Model):
    id = ndb.StringProperty(required=True)
    eservice_info = ndb.KeyProperty(repeated=True)
    econtacts_info = ndb.StructuredProperty(Information,repeated=True)


class mainPage(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name") or "World"
        current_user = users.get_current_user()
        signin_link = users.create_login_url('/')
        template_vars = {
            "name": name,
            "current_user": current_user,
            "signin_link": signin_link,
        }
        template = jinja_env.get_template("templates/hello.html")
        self.response.write(template.render(template_vars))

class emergencyPage(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        person = Person.get_by_id(current_user)
        if person == None:
            template = jinja_env.get_template("templates/block.html")
            self.response.write(template.render())
        else:
            template_vars = {
                "person": person,
            }
            template = jinja_env.get_template("templates/emergency.html")
            self.response.write(template.render(template_vars))

class signupPage(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        person = Person.get_by_id(current_user)
        if person == None:
            template = jinja_env.get_template("templates/signup.html")
            self.response.write(template.render())
        else:
            template = jinja_env.get_template("templates/repeat.html")
            self.response.write(template.render())
    def post(self):
        police_info = Information(
            name="Police Department",
            location=self.request.get("Country")+":"+self.request.get("City")+":"+self.request.get("Zip"),
            number=self.request.get("Police Department's Number"))
        fire_info = Information(
            name="Fire Department",
            location=self.request.get("Country")+":"+self.request.get("City")+":"+self.request.get("Zip"),
            number=self.request.get("Fire Department's Number"))
        p = Person(id=users.get_current_user(),eservice_info=[police_info.put(),fire_info.put],econtacts_info=[]).put()
        self.redirect('/emergency?user='+p.id)


app = webapp2.WSGIApplication([
    ('/',mainPage),
    ('/emergency',emergencyPage),
    ('/signup',signupPage),
    ],debug=True
)
