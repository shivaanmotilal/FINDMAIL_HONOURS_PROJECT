#Shivaan Motilal
#Programme that parses MBOX Mailboxes with to create indices

import mailbox
import argparse
import os
import errno
import webbrowser #for testing purposes
import email.utils #REDUNDANT
import time

"""imports for JSON Conversion"""
import sys, urllib2, email, re, csv, StringIO, base64, json, datetime, pprint
from optparse import OptionParser

class FINDMAILMbox:
    def __init__(self, content = None):
        self.data = {}
        self.raw_parts = []
        self.encoding = "utf-8" # output encoding 
    
    def create_mbox(self,path):
        from_addr = email.utils.formataddr(('Author', 'author@example.com'))
        to_addr = email.utils.formataddr(('Recipient', 'recipient@example.com'))
        
        #Note ReRunning this programm adds more mails to the existing mbox file
        mbox = mailbox.mbox(path)
        """Prepare messages to be removed from existing mbox file"""
        to_remove = []
        for key, msg in mbox.iteritems():
            if not msg['subject'] == None: #Tag every existing message with subject in mbox
                print 'Removing:', key
                to_remove.append(key)
                
        mbox.lock()
        try:
            """-Delete items pre-specified to be removed"""
            for key in to_remove:
                mbox.remove(key)
                
            msg = mailbox.mboxMessage()
            msg.set_unixfrom('author Sat Feb  7 01:05:34 2009')
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Subject'] = 'Sample message 1'
            msg.set_payload('This is the body.\nFrom (should be escaped).\nThere are 3 lines in this body.\n')
            mbox.add(msg)
            mbox.flush()
        
            msg = mailbox.mboxMessage()
            msg.set_unixfrom('author')
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Subject'] = 'Sample message 2'
            msg.set_payload('This is the second body.\n')
            mbox.add(msg)
            mbox.flush()
        finally:
            mbox.unlock()
        
        print (open('FINDMAIL/mailboxes/mbox/example.mbox', 'r').read())
        
    '''-Specifically gets message body for each mail in mbox'''
    def getbody(self,message): #getting plain text 'email body'
        body = None
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
    def getAttachment(self,message): 
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
    
    def printToTextFiles(self,mbox):
        count1=1;
        for message in mbox:
            #if message.is_multipart():
                #content = ''.join(part.get_payload(decode=True) for part in message.get_payload())
            #else:
                #content = message.get_payload(decode=True)
            #print content
            
            
            """File paths"""
            filename = "FINDMAIL/Plain text indices/"+ str(count1)+".txt"
            body= "FINDMAIL/Plain text indices/body/"+ str(count1)+".txt"
            #print filename
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
                    print exc        
            if not os.path.exists(os.path.dirname(body)):
                try:
                    os.makedirs(os.path.dirname(body))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
                    print exc
            
            with open(filename, "w") as f: #Write message to single file
                f.write(str(message) )   
            f.close()
            
            with open(body, "w") as b: #Write body to single file
                #print message.get_content_type()
                #if message.is_multipart():
                    #content = ''.join(part.get_payload(decode=True) for part in message.get_payload())
                #else:
                    #content = message.get_payload(decode=True)            
                b.write(str(self.getbody(message) ))         
            b.close()
            #print getbody(message)
            count1=count1+1    
    
    def printToHTMLFiles(self,mbox):
        count2=1;
        for message in mbox:  
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
            
            strBody = str(self.getbody(message)) 
            
            
            """Derive attachment part of HTML File"""
            
            msgATT=""""""
            for att in self.getAttachment(message):
                strAttach= str(att)
                msgATT=msgATT+ """<p id= ATTACHMENT>"""+strAttach+"""</p>"""
                
            
            """Create html message"""
            msgHTML = """<html>
            <head> FINDMAIL</head>
            <body>
            <p id=FROM>"""+msgFrom +""" </p>
            <p id= SUBJECT> """+msgSubject+"""</p>
            <p id= TO> """+msgTo+"""</p>
            <p id=MESSAGE-ID> """+msgID+"""</p>
            <p id= DATE-TIME> """+msgTime+"""</p>
            <p id= BODY>"""+ strBody+"""</p>
            """+msgATT+"""</body>
            </html>"""   
            
            """File paths"""
            filename = "FINDMAIL/HTML indices/"+ str(count2)+".html"
            
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
    def printToJSONFiles(self,mbox):
        
        self.data['from'] 
        json_data = json.dumps(data)
        count2=1;
        for message in mbox:  
            """Get from, to and subject field from email"""
            msgFrom= message["from"]
            msgTo= message["to"]
            msgSubject= message["subject"]
            msgID= message["message-id"]
            msgTime= message["date"]        
    
    @staticmethod
    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("format", help="specify format of inputted archive")
        parser.add_argument("path", help="specify path to archive from home directory")
        args = parser.parse_args()    
        print args.format 
        print args.path 
        print
            
        """FINDMAIL/mailboxes/mbox/test.mbox"""
        mbox = mailbox.mbox(args.path)
        #printToTextFiles(mbox)        
        #printToTextFiles(mbox)
        self.printToHTMLFiles(mbox)
            #with open('/index/'+ str(count)+'.txt', 'w') as f:
                #print >> f, 'Filename:', filename  # Python 2.x 
            #count=count +1

if __name__ == '__main__':
    mbox=FINDMAILMbox()
    #mbox.create_mbox('FINDMAIL/mailboxes/mbox/example.mbox')
    mbox.main(mbox)


