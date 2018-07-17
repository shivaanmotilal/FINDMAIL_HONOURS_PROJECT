#Shivaan Motilal
#Programme that parses Maildir Mailboxes with MIME Messages to create indices

#!/usr/bin/env python

## Open Sourced by - FINDMAIL App, UCT
## (c) 2018 FINDMAIL (UCT)
## https://github.com/FINDMAIL

import mailbox
import argparse
import os
import errno
import email.utils

"""imports for JSON Conversion"""
import sys, urllib2, email, re, csv, StringIO, base64, json, datetime, pprint
from optparse import OptionParser

#class parseMDIR()
'''-Specifically gets message body for each mail in mbox'''
def getbody(message): #getting plain text 'email body'
    body = None
    #print message #Does not comply with RFC 2822 is rfc 822
    if message.is_multipart():
        for part in message.walk():
            #print part.get_content_type()
            if part.is_multipart():
                for subpart in part.walk():
                    #print subpart.get_content_type()
                    if subpart.get_content_type() == 'text/plain':
                        body = subpart.get_payload(decode=True)
            elif part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)
    elif message.get_content_type() == 'text/plain':
        body = message.get_payload(decode=True)
    return body

'''-Gets attachment from an email of html and png types'''
def getAttachment(message): 
    #What if there are multiple attachments?
    attach = []
    print len(message.get_payload())
    if message.is_multipart():
        for part in message.walk():
            if part.is_multipart():
                for subpart in part.walk():
                    if subpart.get_content_type() == 'text/html': #can also use .get_filename() to get ...
                        attach.append(subpart.get_payload(decode=True))
                    if subpart.get_content_type() == 'image/png':
                        attach.append(subpart.get_payload(decode=True))                   
            elif part.get_content_type() == 'text/plain':
                continue
    elif message.get_content_type() == 'text/plain':
        #Do nothing
        print "no attachment"
    return attach   
    
    #attachments = []
    #parts = []
    #for part in self.msg.walk():
        #if part.is_multipart():
            #continue

        #content_disposition = part.get("Content-Disposition", None)
        #if content_disposition:
            ## we have attachment
            #r = filename_re.findall(content_disposition)
            #if r:
                #filename = sorted(r[0])[1]
            #else:
                #filename = "undefined"

            #a = { "filename": filename, "content": base64.b64encode(part.get_payload(decode = True)), "content_type": part.get_content_type() }
            #attachments.append(a)
        #else:
            #try:
                #p = { "content_type": part.get_content_type(), "content": unicode(part.get_payload(decode = 1), self._get_content_charset(part, "utf-8"), "ignore").encode(self.encoding), "headers": self._get_part_headers(part) }
                #parts.append(p)
                #self.raw_parts.append(part)
            #except LookupError:
                ## Sometimes an encoding isn't recognised - not much to be done
                #pass


"""For emails that comply with RFC 2822"""
def printToHTMLfiles(count2,file):
    """-Is it over-writing files of same name eg 1,2?"""
    mailbox.Maildir.colon = '!' #Another character to use as colon in mdir files
    mdir =mailbox.Maildir(file, factory=None)
    #print file
    for message in mdir:
        #message = mailbox.mboxMessage(file) # has to comply with RFC 2822
        #print message
        """Get from, to and subject field from email"""
        msgFrom= message["from"]
        msgTo= message["to"]
        msgSubject= message["subject"]
        msgID= message["message-id"]
        msgTime= message["date"]
        
        """Convert date-time to usable time format"""
        
        #print "From: ", msgFrom
        #print "To: ", msgTo
        #print "Subject: ", msgSubject
        #print "Message-ID: ", msgID
        #print "Date-time: ", msgTime 
        
        #REMOTE_TIME_ZONE_OFFSET = -2 * 60 * 60  #Take into account local time difference
        #varTime= (time.mktime(email.utils.parsedate(msgTime)) +time.timezone - REMOTE_TIME_ZONE_OFFSET)            
        #print "Time: ", time.strftime('%Y/%m/%d --- Time %H:%M:%S', time.localtime(varTime))
        
        strBody = str(getbody(message)) 
        
        
        """Derive attachment part of HTML File"""
        
        msgATT=""""""
        for att in getAttachment(message):
            strAttach= str(att)
            msgATT=msgATT+ """<p>"""+strAttach+"""</p>"""
        #print getAttachment(message)
        
        if msgATT=="""""":
            msgATT="""<p> NO ATTACHMENTS</p>"""
        
        #print msgATT
        
        """Create html message"""
        msgHTML = """<html>
        <head> FINDMAIL</head>
        <body>
        <h1> FROM: """+msgFrom +""" </h1>
        <h1> SUBJECT: """+msgSubject+"""</h1>
        <h2> TO: """+msgTo+"""</h2>
        <h3> MESSAGE-ID: """+msgID+"""</h3>
        <h4> DATE-TIME: """+msgTime+"""</h4>
        <p>"""+ strBody+"""</p>
        """+msgATT+"""</body> 
        
        </html>"""        
        
        """File paths"""
        filename = "FINDMAIL/MDIR HTML indices/"+ str(count2)+".html"
        
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
                print exc 
                
        with open(filename, "w") as f: #Write message to single file
            f.write(msgHTML )   
        f.close()  
        count2= count2+1
        
"""TO-DO: Prints to JSON files and stores all mails as a list"""
def printToJSONfiles(count2,file):
    data = {}
    data['key'] = 'value'
    json_data = json.dumps(data)    
    """-Is it over-writing files of same name eg 1,2?"""
    mailbox.Maildir.colon = '!' #Another character to use as colon in mdir files
    mdir =mailbox.Maildir(file, factory=None)
    #print file
    for message in mdir:
        #message = mailbox.mboxMessage(file) # has to comply with RFC 2822
        #print message
        """Get from, to and subject field from email"""
        msgFrom= message["from"]
        msgTo= message["to"]
        msgSubject= message["subject"]
        msgID= message["message-id"]
        msgTime= message["date"]
        
def main():
    #for dirname, subdirs, files in os.walk('FINDMAIL/mailboxes/maildir/test1'):
        #print (dirname)
        #print ('\tDirectories:', subdirs)
        #count=1
        #for name in files:
            #fullname = os.path.join(dirname, name)
            #print ()
            #print ('***', fullname)
            ##print (open(fullname).read())
            #printToHTMLfiles(count,fullname)
            #count=count+1
            #print ('*' * 40)  
    printToHTMLfiles(1,"FINDMAIL/mailboxes/maildir/test1")

if __name__ == '__main__':
    main()
