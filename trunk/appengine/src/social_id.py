

# Gets JSONP output, with two params
# 1. profile url
# 2. callback fn


import wsgiref.handlers
import re

from google.appengine.ext import webapp
from google.appengine.api import urlfetch

class MainPage(webapp.RequestHandler):
  def get(self):
    profile_url = self.request.get("p");
    callback = self.request.get("c");
    
    self.response.headers['Content-Type'] = 'text/plain'
    
    profile_json = self.getProfileJson(profile_url);
    self.response.out.write('%s(%s);' % (callback, profile_json));
    
    
    #self.response.headers['Content-Type'] = 'text/plain'
    #self.response.out.write('Hello, webapp World!')

  def getProfileJson(self, profile_url):
    result = urlfetch.fetch(profile_url)
    if result.status_code == 200:
      return self.jsonify(result.content)
    return '{}';

  def jsonify(self, content):
    g = '' #debugging
    pphoto = None
    pname = None
    # <div class="ll_name fn">Noah Fiedel</div>
    
    lines = content.split('\n')
    for line in lines:
      #if line.contains('ll_profilephoto photo')
      photo_match = re.search('<img class="ll_profilephoto photo".*>', line)
      
      if photo_match:
        start = photo_match.span()[0]
        end = photo_match.span()[1]
        imgtag = line[start:end]
        photo_src_match = re.search('http://[\w/\.]*', imgtag)
        imgsrc = ''
        if photo_src_match:
          pphoto = imgtag[photo_src_match.span()[0]: photo_src_match.span()[1]]
        
      nametag_match = re.search('<div class="ll_name fn">.*</div>', line)
      if nametag_match:
        start = nametag_match.span()[0]
        end = nametag_match.span()[1]
        nametag = line[start:end]
        nametag_open_length = len('<div class="ll_name fn">')
        nametag_content_and_end = nametag[nametag_open_length:]
        name_text_match = re.search('[\w ]*', nametag_content_and_end)
        if name_text_match:
          pname = nametag_content_and_end[name_text_match.span()[0]: name_text_match.span()[1]]
        
        
        #g += 'start %s end %s' % (start, end)
        #g += '\n match=%s\n' % line[start:end]
      #g += '\n <img src="%s">\n' % pphoto
      #g += '\n pname = %s\n' % pname
      
      #g += '\n\'line:%s' % line
    return '{ "pname": "%s", "pphoto": "%s" }' % (pname, pphoto)
    #return '{\'profile\': \'%s\',}' % g;

def main():
  application = webapp.WSGIApplication(
                                       [('/', MainPage)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()