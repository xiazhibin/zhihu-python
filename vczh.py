#-*- coding:utf-8 -*-
import requests
import urllib
import urllib2
from bs4 import BeautifulSoup
import sys
import random
import platform
import cookielib
import os
import json
from getpass import getpass
import time
import threading

class Vczh_wheel_stroll(object):
    def __init__(self):
        self.basic_url = 'http://www.zhihu.com'
        self.cookies = None
        self.soup = None
        self.session = None
        self.xsrf = None
        self.headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
            'Host': "www.zhihu.com",
            'Origin': self.basic_url,
            'Pragma': "no-cache",
            'Referer': self.basic_url,
            'X-Requested-With': "XMLHttpRequest"
        }
        self.requests = requests.Session()
        self.requests.cookies = cookielib.LWPCookieJar('cookies')
        try:
            self.requests.cookies.load(ignore_discard=True)
        except:
            pass
    
    def get_xsrf(self):
        r = self.requests.get(self.basic_url, verify=False, headers=self.headers)
        if int(r.status_code) != 200:
            raise Exception(u'get xsrf failed')
        soup = BeautifulSoup(r.text, 'lxml')
        return soup.find('input', attrs={'name': '_xsrf'})['value']
    
    def get_captcha(self):
        captcha_url = 'http://www.zhihu.com/captcha.gif'
        r = self.requests.get(captcha_url, params={"r": random.random(), "type": "login"}, verify=False, headers=self.headers)
        if int(r.status_code) != 200:
            raise Exception(u"验证码请求失败")
        img_name = u"verify." + r.headers['content-type'].split("/")[1]
        with open( img_name, "wb") as f:
            f.write(r.content)
        if platform.system() == "Linux":
            os.system("xdg-open %s &" % img_name )
        elif platform.system() == "Darwin":
            os.system("open %s &" % img_name )
        elif platform.system() in ("SunOS", "FreeBSD", "Unix", "OpenBSD", "NetBSD"):
            os.system("open %s &" % img_name )
        elif platform.system() == "Windows":
            os.system("%s" % img_name )
        else:
            print u'自行打开文件'
        captcha_code = raw_input("input you code:")
        return captcha_code

    def login(self, user, passwd):
        check_url = "https://www.zhihu.com/settings/profile"
        r = self.requests.get(check_url, allow_redirects=False, verify=False, headers=self.headers)
        status_code = int(r.status_code)
        print 'status_code is:', status_code
        if status_code == 301 or status_code == 302:
            pass
        elif status_code == 200:
            print 'logined already'
            return
        else:
            raise Exception('network error')
        self.xsrf = self.get_xsrf()
        form = {
            'email': user,
            'password': passwd,
            '_xsrf': self.xsrf,
            'captcha': self.get_captcha(),
            'rememberme': True
        }
        url = 'https://www.zhihu.com/login/email'
        r = self.requests.post(url, data=form, headers=self.headers, verify=False)
        try:
            res = r.json()
        except:
            print 'can not encode to json'
        else:
            if res[u'r'] == 0:
                print 'login successfully'
                print r.cookies
                self.requests.cookies.save()
                self.cookies = r.cookies
            else:
                print 'error occurred, msg: %s' % res[u'msg'].encode('UTF-8')
    
    @staticmethod
    def save_img(pic_url):
        try:
            stream = urllib2.urlopen(pic_url)
            data = stream.read()
            split_path = pic_url.split('/')
            file_name = split_path.pop()
            print pic_url, '---', file_name
            return
            with open(file_name, 'wb') as f:
                f.write(data)
        except Exception, e:
            print "Cant't download %s: %s" % (file_name, e)
        finally:
            time.sleep(1)
    
    def main_task(self):
        main_url = 'https://www.zhihu.com/people/excited-vczh/followees'
        r = self.requests.get(main_url, verify=False, headers=self.headers)
        if int(r.status_code) != 200:
            raise Exception(u'error get main_url')
        soup = BeautifulSoup(r.text, 'lxml')
        for irl in soup.find_all("img"):
            t = threading.Thread(target=Vczh_wheel_stroll.save_img, args=(irl.get('src'), ))
            t.start()
            #print irl.get('src')
        json_str = soup.select("#zh-profile-follows-list div[data-init]")[0]['data-init']
        json_data = json.loads(json_str)
        #print type(json_data)
        #print json_data
        #print '============================'
        more_url = 'https://www.zhihu.com/node/' + json_data[u'nodename']
        print 'more_url is', more_url
        del json_data[u'nodename']
        json_data['_xsrf'] = soup.find('input', attrs={'name': '_xsrf'})['value']
        json_data['method'] = "next"
        json_data[u'params'][u'offset'] += 20
        json_data[u'params'] = json.dumps(json_data[u'params'])
        #headers = self.headers
        #headers['Referer'] = main_url
        header = {
            'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
            'Host': "www.zhihu.com",
            'Referer': main_url
        }
        #headers['X-Xsrftoken'] = soup.find('input', attrs={'name': '_xsrf'})['value']
        #headers['Cookie'] = self.cookies
        while True:
            r = self.requests.post(more_url, data=json_data, headers=header, verify=False)
            print r.status_code
            try:
                text = r.json()
            except:
                print 'cannot get json'
            else:
                if int(r.status_code) != 200:
                    return
                print '********************'
                #print text[u'msg'][0]
                #return
                soup = BeautifulSoup(text[u'msg'][0], 'lxml')
                for irl in soup.find_all("img"):
                    t = threading.Thread(target=Vczh_wheel_stroll.save_img, args=(irl.get('src'), ))
                    t.start()
                    #print irl.get('src')
                break

if __name__ == '__main__':
    s = Vczh_wheel_stroll()
    #user = raw_input("account")
    #passwd = raw_input("password")
    user = 'l2009091@qq.com'
    passwd = 'litaohaha123456'
    s.login(user, passwd)
    s.main_task()
