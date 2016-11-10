import re
import sys
import requests
import time
import json
import string
import Cookie
from datetime import datetime

# reload(sys)
# sys.setdefaultencoding('utf-8')

cookie = '<your-cookie-string>'

c = Cookie.SimpleCookie()
c.load(cookie)
cookieDict = {}

for key, morsel in c.items():
    cookieDict[key] = morsel.value

headers = {    
    'Host': 'www.linkedin.com',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': 1,
    'Accept': 'application/json',
    'DNT': 1,
    'Accept-Encoding': 'gzip, deflate, sdch, br',
    'Avail-Dictionary': 'YFA7RCTS',
    'Accept-Language': 'id-ID,id;q=0.8,en-US;q=0.6,en;q=0.4,ms;q=0.2',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/53.0.2785.143 Chrome/53.0.2785.143 Safari/537.36',
    'Cookie': cookie,
}

if __name__ == '__main__':

    if sys.argv.__len__() > 0:
        c_link = sys.argv[1]

        loop = True

	loop_count = 0

        while loop:
            
            if loop_count > 0:
                time.sleep(2)

            print 'Requesting...'
            session = requests.session()

            res = session.get(c_link, headers=headers, allow_redirects=True, cookies=cookieDict)
            loop_count += 1

            timestamp = int(time.mktime(datetime.now().timetuple()))
            filename = 'emails-{}.txt'.format(timestamp)
            
            with open(filename, 'w') as jsonfile:

                print 'Create file {} to store emails'.format(filename)
                
                printable = set(string.printable)
                clear_text =filter(lambda x: x in printable, res.text)
                
                try:
                    json_result = json.loads(clear_text)

                    print 'Grab successfully'
                    print 'Request successful, now extracting emails...'

		    regex_mail = '[a-zA-Z0-9_.+-]+@'
                    regex_domain = '[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+\.?(?:[a-zA-Z0-9-]+)?'

                    email_storage = []
                
                    blocks = json_result.get('blocks')
                    if blocks:
                        for content_block in blocks:
                            content_block = content_block.get('blocks')
                            comment_block = content_block[0]
                            comment_values = comment_block.get('blocks')
  
                            email = None
                            email_first_part = None
                            email_last_part = None
                            for comment_text in comment_values[2].get('wads'):
                                text_to_search = comment_text.get('text')

                                try:
                                    found_mail = re.findall(regex_mail, text_to_search)
                                    found_domain = re.findall(regex_domain, text_to_search)

                                    if found_mail.__len__() > 0:
                                        email_first_part = '+'.join(found_mail)

                                    if found_domain.__len__() > 0:
                                         email_last_part = '+'.join(found_domain)

                                except Exception as e:
                                    pass

                            if email_first_part is not None and email_last_part is not None:
                                if found_mail.__len__() > 1 or found_domain.__len__() > 1:
                                    # Contains multiple email. merge them
                                    email = '{}|{}'.format(email_first_part, email_last_part)
                                else:
                                    email = '{}{}'.format(email_first_part, email_last_part)

                            if email:
                                print 'Got email: {}'.format(email)
                                email_storage.append(email)
                
                    jsonfile.write(','.join(email_storage)) 
                except Exception as e:
                    print "Grab failed:"
                    print(e)
                    print(clear_text)

            paginationUrl = json_result.get('paginationUrl')
            if paginationUrl:
                c_link = 'http://www.linkedin.com{path}'.format(path=paginationUrl)
                print 'next: grab on {}'.format(c_link)
            else:
                break
