import lxml.etree
import requests
import os
import codecs
import locale
import sys
from optparse import OptionParser

# Wrap sys.stdout into a StreamWriter to allow writing unicode.
# From http://stackoverflow.com/questions/4545661/unicodedecodeerror-when-redirecting-to-file
#sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)


parser = OptionParser()

parser.add_option("-u", "--username", dest="username", action="store", help = "Google Account (email address) to log into google", default=None)
parser.add_option("-p", "--password", dest="password", action="store", help = "Password for Google Account to log into google", default=None)
parser.add_option("-b", "--basedir", dest="basedir", action="store", help = "Base Directory in which to store download, default feeds", default="feeds")
parser.add_option("-i", "--input", dest="inputOpml", action="store", help = "OPML subscriptions file to read, default subscriptions.xml", default="subscriptions.xml")
parser.add_option("-o", "--output", dest="outputOpml", action="store", help = "Where to store modified OPML subscription file, default subscriptions-with-ids.xml", default="feeds/subscriptions-with-ids.xml")
#parser.add_option("-d", "--debug", dest="debug", action="store_true", help = "Turn on debugging", default=False)

(options, args) = parser.parse_args()

basefeeddir = options.basedir


#opmlfile = codecs.open(options.inputOpml, "r", "utf-8")
opmlfile = open(options.inputOpml, "r")
opml = opmlfile.read()

# 
# We're looking for entries that actually have a feed associated with them
# and not just entries that are folders
#
tree = lxml.etree.fromstring(opml)
elements = tree.xpath('//outline[@xmlUrl]')


# We need to connect to Google to get an authorization
# token
auth_url = 'https://www.google.com/accounts/ClientLogin'
auth_req_data = {
    'Email': options.username,
    'Passwd': options.password,
    'service': 'reader'
    }

auth_resp = requests.get(auth_url, params=auth_req_data)

#print auth
auth_resp_dict = dict(x.split('=') for x in auth_resp.text.split('\n') if x)
token = auth_resp_dict["Auth"]
#print auth.headers

# Scan through each feed and store the results
for i in range(0,len(elements)):
  try:
    #print elements[i].attrib['title']
    elements[i].attrib['id'] = str(i)
  except UnicodeEncodeError as e:
    print "Failed on element %d" % (i)
  feeddir = "%s/feed_%d" % (basefeeddir, i)
  print "Processing feed: %s" % elements[i].attrib['title'].encode('ascii', 'ignore')

  if not os.path.exists(feeddir):
    os.makedirs(feeddir)


  # There are probably other thigns that need to be URL encoded, but all I hit was the question mark
  url = "http://www.google.com/reader/atom/feed/%s?n=250" % (elements[i].attrib['xmlUrl'].replace("?", "%3f"))
  print "Url is %s" % (url)

  headers = {'Authorization': 'GoogleLogin auth=%s' % token}

  # cont_params are for a 'continuation' token from the reader api
  # basically, you can keep looping over a URL. By changing the
  # continuation token, you advance through the loop. For the first
  # pass, we don't ask for one. 
  cont_params = ""
  counter = 0
  remaining = True
  while remaining:
    r = requests.get(url+cont_params, headers=headers)
    if r.status_code != 200:
      print "Load failed with code %s" % (str(r.status_code))
      # I've got at least one feed in my subscriptions that Google apparently 
      # doesn't have anymore for whatever reason, so treat anything other than
      # a successful download as an error with this feed only. 
      # (Yeah, probably not a great idea but works for today)
      remaining = False
      continue

    #
    # OK, we've downloaded a chunk of this feed, let's save it
    #
    output_filename = feeddir + "/feed_%d.xml" % (counter) 
    with codecs.open(output_filename,'w','utf-8') as output_file:
      output_file.write(r.text)
      output_file.close()

    #
    # Take a look in the feed, and find out how many entries there are
    # and if we have a contiuation, ie we need to download more entries
    #
    counter = counter + 1
    results = lxml.etree.fromstring(r.text)
    posts = results.xpath('/ns:feed/ns:entry', namespaces={'ns': 'http://www.w3.org/2005/Atom'})
    continuations = results.xpath('//gr:continuation', namespaces={'gr': "http://www.google.com/schemas/reader/atom/"})
    print "Found %d entries" % (len(posts))
    if(len(continuations) > 0):
      print "Found continuation token %s, will fetch more results" % (continuations[0].text)
      cont_params="&c=%s" % (continuations[0].text)
    else:
      # no continuation, so we're done with this feed. Move on to the next feed
      # by looping back up to the 'for in range' part
      remaining = False

# We modified the OPML file to add an ID to each entry
# dump the modified file. 
# According to the spec, OPML readers are to ignore any tag they don't understand
# so this file should still be valid OPML 
with codecs.open(options.outputOpml, "w", 'utf-8') as output_opml_file:
  output_opml_file.write(lxml.etree.tostring(tree))
  output_opml_file.close()
