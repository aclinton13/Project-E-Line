import os
import webapp2
import jinja2
from google.appengine.api import urlfetch
import urllib
import json
from logging import info as loginfo
from random import randint

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
    loginfo(li)
    loginfo(subli)
    loginfo("EARTH\n\n\n")
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

def getPerson():
    current_user = users.get_current_user()
    person = Person.query().filter(Person.id == current_user.email()).fetch()
    if len(person) == 1:
        return person[0]
    else:
        return None

def insurePerson(handler):
    if getPerson() is None:
        handler.redirect("/setup")

def removePerson(person):
    # for item in person.eservice_info:
    #     item.delete()
    for item in person.econtacts_info:
        item.delete()
    person.key.delete()

def mostCommon(infos,attr1,attr1_value,attr2):
    if len(infos) == 0:
        return ""
    freq = {}
    ret_freq = {}
    for info in infos:
        #loginfo(info._properties["name"])
        #loginfo(freq)
        #loginfo("\n\n\n\n")
        if info._properties[attr1] == attr1_value:
            val = info._properties[attr2]
            #loginfo(val)
            #loginfo("WATER\n\n\n\n")
            if val in freq:
                freq[val] = freq[val]+1
            else:
                ret_freq[val] = info
                freq[val] = 1
    ret = [freq[name] for name in freq]
    ret.sort()

    # return [ret_freq[i] for i in freq if freq[i] == ret[-1]][0]


class Information(ndb.Model):
    name = ndb.StringProperty(required=True)
    location = ndb.StringProperty(required=True)
    number = ndb.StringProperty(required=True)

class Person(ndb.Model):
    id = ndb.StringProperty(required=True)
    location = ndb.StringProperty(required=True)
    eservice_info = ndb.KeyProperty(repeated=True)
    econtacts_info = ndb.KeyProperty(repeated=True)


class mainPage(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        person = getPerson()
        if not person:
            self.redirect("/setup")
        else:
            logout_link = users.create_logout_url('/')
            template_vars = {
                "current_user": current_user,
                "logout_link": logout_link,
            }
            template = jinja_env.get_template("templates/eline.html")
            self.response.write(template.render(template_vars))

#Make it the emergency.html display all infor
class emergencyPage(webapp2.RequestHandler):
    def get(self):
        person = getPerson()
        insurePerson(self)
        self.response.write(handleEmergency(person))

class setupPage(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user().email()
        person = Person.query().filter(Person.id == current_user).fetch()
        if len(person) == 0:
            template_vars = {
                "post_location" : "/setup"
            }
            template = jinja_env.get_template("templates/form.html")
            self.response.write(template.render(template_vars))
        else:
            template = jinja_env.get_template("templates/repeat.html")
            self.response.write(template.render())
    def post(self):
        names = ["Police Department","Fire Department"]
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
        ]
        toplace_info = []
        input_keys = []
        for i in range(len(input_info)):

            l = Information.query().filter(ndb.AND(Information.name == input_info[i].name,Information.location == input_info[i].location)).fetch()

            input_keys.append(input_info[i].put())

            most_common_number = mostCommon(l,"name",names[i],"number")
            if most_common_number != "":
                toplace_info.append(mostCommon(l,"name",names[i],"number"))
            else:
                toplace_info.append(input_info[i])
        super_persons = Person.query().filter(Person.id == loc).fetch()
        # if len(super_persons) == 0:
        #     Person(
        #         id=loc,
        #         location=loc,
        #         eservice_info=[toplace_info[0].put(),toplace_info[1].put()],
        #         econtacts_info=[],
        #         ).put()
        # else:
        #     super_person = super_persons[0]
        #     super_person.eservice_info=[toplace_info[0].put(),toplace_info[1].put()]
        if len(super_persons) == 0:
            Person(
                id=loc,
                location=loc,
                eservice_info=[toplace_info[0].put(),toplace_info[1].put()],
                econtacts_info=[],
                ).put()
        else:
            super_person = super_persons[0]
            super_person.eservice_info=[toplace_info[0].put(),toplace_info[1].put()]

        Person(
            id=str(current_user),
            location=loc,
            eservice_info=[input_keys[0],input_keys[1]],
            econtacts_info=[],
            ).put()

        template = jinja_env.get_template("templates/finished_setup.html")
        self.response.write(template.render())

class addContactsPage(webapp2.RequestHandler):
    def get(self):
        insurePerson(self)
        template = jinja_env.get_template("templates/addContacts.html")
        self.response.write(template.render())
    def post(self):
        current_user = users.get_current_user().email()
        person = getPerson()
        loc = self.request.get("Country")+":"+self.request.get("City")+":"+self.request.get("Zip")
        person.econtacts_info.append(
            Information(
                name= self.request.get("Name"),
                location=loc,
                number = (self.request.get("Number"))
                ).put()
            )
        template = jinja_env.get_template("templates/finished_adding_contact.html")
        self.response.write(template.render())

class editInformationPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_env.get_template("templates/changes.html")
        self.response.write(template.render())
    def post(self):
        people=getPerson()
        # index=findInfo(people)
        self.request.get('name')
        if(people==-1):
            Information(
                name="Police Department",
                location=loc,
                number=self.request.get("Police")),
            Information(
                name="Fire Department",
                location=loc,
                number=self.request.get("Fire"),
                )
        people.location.remove()
        people.location.append()
        people.eservice_info.remove()
        people.eservice_info.append()

        # for i in range(len(loc or eservice):
        #     people.location[i]=        people.location.append()
        #     people.eservice_info[]=        people.eservice_info.append()

        template_vars = {
            "post_location" : "/setup"
        }
        removePerson(getPerson())
        template = jinja_env.get_template("templates/form.html")
        self.response.write(template.render(template_vars))

class choosePage(webapp2.RequestHandler):
    def get(self):
        template = jinja_env.get_template("templates/choose.html")
        self.response.write(template.render())

class searchPage(webapp2.RequestHandler):
    def get(self):
        template_vars = {
            "post_location" : "/search"
        }
        template = jinja_env.get_template("templates/form.html")
        self.response.write(template.render(template_vars))
    def post(self):
        input_location = [self.request.get("Country"),self.request.get("City"),self.request.get("Zip")]
        people = Person.query().fetch()
        test = False
        for person in people:
            locations = person.location.split(":")
            for place in input_location:
                if place in locations:
                    test = True
                    touse = person
        if test:
            self.response.write(handleEmergency(touse))
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
    ('/addContacts',addContactsPage),
    ('/test',testPage),
    ('/editInformation',editInformationPage),
    ('/choose',choosePage),
    ],debug=True
)
