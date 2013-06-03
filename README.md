stash-greader-posts
===================
A Python script to download all of the posts in the RSS feeds from Google Reader to which you're subscribed.

Erik Paulson
epaulson@unit1127.com
2013-06-02

#### Motivation
I've been using Google Reader to keep track of RSS feeds for many years now, and I've collected and stored fair amount of information in it that I'd be hard-pressed to replace. 

Google helpfully makes it easy to export an OPML file with a list of which feeds you are subscribed. You can take this OPML file and easily migrate to a new RSS Reader, and you'll start getting all the new content from your subscriptions. 

The dilemma is what about old feeds that aren't updating? If the site is still online, there's no problem, but for several of my feeds, the site is long gone. In some instances, it's the author has abandoned the site and the blog is deleted or the domain hijacked, and in a sadder situation for at least a few of my feeds, the author has passed away and the site no longer has anyone to keep it online. 

One of the great things about Google Reader is that it keeps cached copies of these old feeds as an Atom feed, so they've still been available. However, with the impending shutdown of Google Reader, I'm about to lose them, so I wanted to get a local copy of this data. 

#### stash-greader-posts.py
This script uses the [Unofficial Google Reader API](https://code.google.com/p/google-reader-api/) to download the complete Atom feed of every feed to which you're subscribed. 

At the moment, that's all it does. I haven't written any tools to upload the data anywhere, and I'm not even sure I'm going to have to - I've switched to feedly to read RSS, but in case something goes wrong after Google Reader shuts down I wanted to have a local copy of the data, just in case. 

#### Getting started
This script uses [lxml](http://lxml.de/) for processing the Atom feed and the excellent [Python Requests](http://docs.python-requests.org/en/latest/) for accessing the API. 

First, you'll need the OPML file of your subscriptions. The easiest way to get it is to go to [Google Takeout](https://www.google.com/takeout/), select Reader, and click on 'Create Archive'. This will give you back a zip file with your subscriptions, shared items, starred items, and a few other things. Download and unzip that file - it will give you back something like epaulson-takeout. You want to find epaulson-takeout/Reader/subscriptions.xml - that's the OPML file. 

Now, remember - you're going to be downloading **every single post** in each feed, so think hard about which feeds you want to keep. I went through and cut out some of the blogs that post the most from my OPML file (I don't need every single Daily Kos and Techcrunch article.) 

Here's the usage:

```python
Usage: stash-greader-posts.py [options]

Options:
  -h, --help            show this help message and exit
  -u USERNAME, --username=USERNAME
                        Google Account (email address) to log into google
  -p PASSWORD, --password=PASSWORD
                        Password for Google Account to log into google
  -b BASEDIR, --basedir=BASEDIR
                        Base Directory in which to store download, default
                        feeds
  -i INPUTOPML, --input=INPUTOPML
                        OPML subscriptions file to read, default
                        subscriptions.xml
  -o OUTPUTOPML, --output=OUTPUTOPML
                        Where to store modified OPML subscription file,
                        default subscriptions-with-ids.xml
                        
```

Frustratingly, Google requires an authenticated access to its cached copy of the RSS feeds, so we have to log in to be able to read them. Username and Password should be self-explanatory. We use the ClientLogin authentication method, so that's why we need a password instead of there being some sort of OAuth workflow with a browser.

INPUTOPML is hopefully also self-explanatory.

OUTPUTOPML is the (slightly) transformed OPML. Rather than trying to figure out a name for every feed that escaped properly into the file system, I add an 'ID' element to each element of the OPML file. (Per the OPML docs, any tag an OPML reader doesn't understand should be ignored, so it is still a valid OPML file). This is the id with which you can find the posts - the OPML entry with ID 0 will have its posts stored in a directory called feed_0/

BASEDIR is the directory in which the feeds are stored overall, so you wind up with a directory structure that looks like
`feeds/feed_10/feed_0.xml`

Inside each `feed_$ID` directory are a number of `feed_$i.xml` files, number from 0 to N. The script downloads each feed in up to 250-post chunks (with the last chunk being smaller, if necessary.) You can't actually concatenate each file together, but you should be able to post-process them and extract all of the `<entry>…</entry>` data from `feed_1.xml` through `feed_$N.xml`, adjust a few headers, and have a single feed file. 

The OPML from Google Reader has the original feed source available, so you can use that to combine the old feed with new feed data.

#### Now what?
Well, I'm not sure. After running this you'll have all the posts, so they're safe, and they're already nicely formatted into an Atom feed, so they're easy to process.

Depending on the APIs of other RSS readers, you should be able to stand these up on a web server with some minimal transformation, import them into your new RSS reader, and have all of the old posts available while getting new posts from the 'alternate' URL in the OPML. **This script does not do any of that for you nor do I even know if any RSS reader can do that.**

Someday I hope there will be a good distributed RSS reader, running on some kind of digital storage locker like Thinkup or camlistore so I always have a copy of an RSS feed, and never have to worry about my RSS reader vendor pulling the plug.

#### Bugs
There are probably plenty, I'm a crappy programmer and not very pythonic in my code. 

There's not a lot of error checking, and you probably have to start over if you hit a transient error.

Unicode and Python 2.x drives me bonkers. There are undoubtably bugs there. URL encoding is also incomplete, but handled every feed I was subscribed to so I couldn't work out what other problems might be lurking.

#### License
This isn't interesting enough to license. Do with it as you please, though I make no warranty or guarantees. 
