import os
import webapp2
import jinja2
from google.appengine.api import urlfetch
import urllib
import json

jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__))
)

from google.appengine.ext import ndb
from google.appengine.api import users

def handleEmergency(person):
    template_vars = {
        "person": person,
    }
    template = jinja_env.get_template("templates/emergency.html")
    return template.render(template_vars)
def listContains(li,subli):
    if len(subli) > len(li):
        return False
    consistent = -1
    pos = 1
    for item in subli:
        if item == "":
            pos = pos+1
            consistent = consistent+1
            continue
        if item in li:
            if consistent == -1:
                consistent = li.index(item)
            else:
                if consistent+1 == li.index(item):
                    consistent = consistent+1
                    pos = pos+1
                else:
                    consistent = -1
                    pos = 1
    if pos == len(subli):
        return True
    else:
        return False


class Information(ndb.Model):
    name = ndb.StringProperty(required=True)
    location = ndb.StringProperty(required=True)
    number = ndb.StringProperty(required=True)

class Person(ndb.Model):
    id = ndb.StringProperty(required=True)
    location = ndb.StringProperty(required=True)
    eservice_info = ndb.KeyProperty(repeated=True)
    econtacts_info = ndb.KeyProperty(repeated=True)
    hotline_info = ndb.KeyProperty(repeated=True)


class mainPage(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        logout_link = users.create_logout_url('/setup')
        template_vars = {
            "current_user": current_user,
            "logout_link": logout_link,
        }
        template = jinja_env.get_template("templates/hello.html")
        self.response.write(template.render(template_vars))

class emergencyPage(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        person = Person.query().filter(Person.id == current_user.email()).fetch()
        if len(person) == 0:
            template = jinja_env.get_template("templates/block.html")
            self.response.write(template.render())
        else:
            self.response.write(handleEmergency(person[0]))

class setupPage(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user().email()
        person = Person.query().filter(Person.id == current_user).fetch()
        if len(person) == 0:
            template = jinja_env.get_template("templates/setup.html")
            self.response.write(template.render())
        else:
            template = jinja_env.get_template("templates/repeat.html")
            self.response.write(template.render())
    def post(self):
        current_user = users.get_current_user().email()
        loc = self.request.get("Country")+":"+self.request.get("City")+":"+self.request.get("Zip")
        input_info =[
        Information(
            name="Police Department",
            location=loc,
            number=self.request.get("Police")
            ),
        Information(
            name="Fire Department",
            location=loc,
            number=self.request.get("Fire")
            ),
        Information(
            name= self.request.get('contact'),
            location=loc,
            number=self.request.get('contact_num')
            ),
        Information(
            name=self.request.get('hotline_function'),
            location=loc,
            number=self.request.get('hotline'),
            ),
        ]
        #l = Information.query().filter((Information.name == input_info[i].name) && (Information.location == input_info[i].location)).fetch()
        #check = lambda x: ((x.name == ))
        #check for the existence of duplicates
        Person(
            id=str(current_user),
            location=loc,
            eservice_info=[police_info.put(),fire_info.put()],
            econtacts_info=[],
            hotline_info=[],
            ).put()

        template = jinja_env.get_template("templates/finished_setup.html")
        self.response.write(template.render())

class contactPage(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user().email()
        person = Person.query().filter(Person.id == current_user).fetch()
        template = jinja_env.get_template("templates/contacts.html")
        self.response.write(template.render())
    def post(self):
        current_user = users.get_current_user().email()
        contact_info= Information(
            name= "Emergency Contacts",
            contact=self.request.get('contact'),
            number=(self.request.get('contact_num'))
            )
        hotline_info= Information(
            name="Hotline Information",
            function=self.request.get('hotline_function'),
            number=self.request.get('hotline'),
            )
        template = jinja_env.get_template("templates/finished_setup.html")
        self.response.write(template.render())


class searchPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_env.get_template("templates/search.html")
        self.response.write(template.render())
    def post(self):
        input_location = [self.request.get("Country"),self.request.get("City"),self.request.get("Zip")]
        locations = Person.query().fetch()
        test = filter(lambda x: listContains(x.location.split(":"),input_location),locations)
        if len(test) == 1:
            self.response.write(handleEmergency(test[0]))
        else:
            template = jinja_env.get_template("templates/not_found.html")
            self.response.write(template.render())

class aboutPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_env.get_template("templates/about.html")
        self.response.write(template.render())

class testPage(webapp2.RequestHandler):
    def get(self):
        api_key = "AIzaSyAm7TCETbqEJZpeY4QGoRJN7mPGEKIx-ZQ"
        params = {"q" : "Neverwhere","api_key" : api_key}
        base_url = "https://www.googleapis.com/books/v1/volumes"
        full_url = base_url+"?"+urllib.urlencode(params)
        #print('full url:',full_url)
        response = urlfetch.fetch(full_url).content
        books = json.loads(response)
        print("books:",books)

        template = jinja_env.get_template("templates/about.html")
        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/',mainPage),
    ('/emergency',emergencyPage),
    ('/setup',setupPage),
    ('/about',aboutPage),
    ('/search',searchPage),
    ('/contacts',contactPage),
    ('/test',testPage),
    ],debug=True
)
