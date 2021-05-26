import argparse
import sys
import re
import threading
import  requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import random
import ssl
import urllib3
import codecs
import os
import pprint
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings()
lock = threading.Lock()
def parse_args():
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython ' + sys.argv[0] + " -u http://www.baidu.com")
    parser.add_argument("-u", "--url", help="The website")
    parser.add_argument("-d", "--deep",help="Deep find", action="store_true")
    parser.add_argument("-l","--limit", help="limit subdomain")
    parser.add_argument("--proxy", help="proxy")
    parser.add_argument("-t", "--thread", help="thread")
    parser.add_argument("-b", "--black list", help="black list")
    return parser.parse_args()

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
    "UCWEB7.0.2.37/28/999",
    "NOKIA5700/ UCWEB7.0.2.37/28/999",
    "Openwave/ UCWEB7.0.2.37/28/999",
    "Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
    "Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25",
]
 pattern_raw = r"""
		  #(?:"|')                               # Start newline delimiter
		  (?:
		    (?:(?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
		    [^"'/]{1,}\.                        # Match a domainname (any character + dot)
		    [a-zA-Z0-9]{2,}[^"']{0,})              # The domainextension and/or path
		    |
		    (?:(?:/|\.\./|\./)                    # Start with /,../,./
		    [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
		    [^"'><,;|()]{1,})                   # Rest of the characters can't be
		    |
		    (?:[a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
		    [a-zA-Z0-9_\-/]{1,}                 # Resource name
		    \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
		    (?:[\?|/][^"|']{0,}|))              # ? mark with parameters
		    |
		    (?:[a-zA-Z0-9_\-]{1,}                 # filename
		    \.(?:php|asp|aspx|jsp|json|
		         action|html|js|txt|xml|
		         shtml|htm|asa|php3|php4|
		         php5|do|jspx)                      # . + extension
		    (?:\?[^"|']{0,}|))                  # ? mark with parameters
		  )
		  #(?:"|')                               # End newline delimiter
		"""

find = {
        "a": ["href"],
        "img": ["src", "data-src", "data-link"],
        "link": ["href"],
        "script": ["src"]
    }
ruleDatas = [
    ['Shiro', 'headers', '(=deleteMe|rememberMe=)'],
    ['Portainer(Docker管理)', 'code',
     '(portainer.updatePassword|portainer.init.admin)'],
    ['Gogs简易Git服务', 'cookie', '(i_like_gogs)'],
    ['Gitea简易Git服务', 'cookie', '(i_like_gitea)'],
    ['宝塔-BT.cn', 'code', '(app.bt.cn/static/app.png|安全入口校验失败)'],
    ['Nexus', 'code', '(Nexus Repository Manager)'],
    ['Nexus', 'cookie', '(NX-ANTI-CSRF-TOKEN)'],
    ['Harbor', 'code', '(<title>Harbor</title>)'],
    ['Harbor', 'cookie', '(harbor-lang)'],
    ['禅道', 'code', '(/theme/default/images/main/zt-logo.png)'],
    ['禅道', 'cookie', '(zentaosid)'],
    ['协众OA', 'code', '(Powered by 协众OA)'],
    ['协众OA', 'cookie', '(CNOAOASESSID)'],
    ['xxl-job', 'code', '(分布式任务调度平台XXL-JOB)'],
    ['atmail-WebMail', 'cookie', '(atmail6)'],
    ['atmail-WebMail', 'code', '(Powered by Atmail)'],
    ['atmail-WebMail', 'code', '(/index.php/mail/auth/processlogin)'],
    ['weblogic', 'code',
        '(/console/framework/skins/wlsconsole/images/login_WebLogic_branding.png|Welcome to Weblogic Application Server|<i>Hypertext Transfer Protocol -- HTTP/1.1</i>)'],
    ['用友致远oa', 'code', '(/seeyon/USER-DATA/IMAGES/LOGIN/login.gif)'],
    ['Typecho', 'code', '(Typecho</a>)'],
    ['金蝶EAS', 'code', '(easSessionId)'],
    ['phpMyAdmin', 'cookie', '(pma_lang|phpMyAdmin)'],
    ['phpMyAdmin', 'code', '(/themes/pmahomme/img/logo_right.png)'],
    ['H3C-AM8000', 'code', '(AM8000)'],
    ['360企业版', 'code', '(360EntWebAdminMD5Secret)'],
    ['H3C公司产品', 'code', '(service@h3c.com)'],
    ['H3C ICG 1000', 'code', '(ICG 1000系统管理)'],
    ['Citrix-Metaframe', 'code', '(window.location=\\"/Citrix/MetaFrame)'],
    ['H3C ER5100', 'code', '(ER5100系统管理)'],
    ['阿里云CDN', 'code', '(cdn.aliyuncs.com)'],
    ['CISCO_EPC3925', 'code', '(Docsis_system)'],
    ['CISCO ASR', 'code', '(CISCO ASR)'],
    ['H3C ER3200', 'code', '(ER3200系统管理)'],
    ['万户ezOFFICE', 'headers', '(LocLan)'],
    ['万户网络', 'code', '(css/css_whir.css)'],
    ['Spark_Master', 'code', '(Spark Master at)'],
    ['华为_HUAWEI_SRG2220', 'code', '(HUAWEI SRG2220)'],
    ['蓝凌EIS智慧协同平台', 'code', '(/scripts/jquery.landray.common.js)'],
    ['深信服ssl-vpn', 'code', '(login_psw.csp)'],
    ['华为 NetOpen', 'code', '(/netopen/theme/css/inFrame.css)'],
    ['Citrix-Web-PN-Server', 'code', '(Citrix Web PN Server)'],
    ['juniper_vpn', 'code',
        '(welcome.cgi\\?p=logo|/images/logo_juniper_reversed.gif)'],
    ['360主机卫士', 'headers', '(zhuji.360.cn)'],
    ['Nagios', 'headers', '(Nagios Access)'],
    ['H3C ER8300', 'code', '(ER8300系统管理)'],
    ['Citrix-Access-Gateway', 'code', '(Citrix Access Gateway)'],
    ['华为 MCU', 'code', '(McuR5-min.js)'],
    ['TP-LINK Wireless WDR3600', 'code', '(TP-LINK Wireless WDR3600)'],
    ['泛微协同办公OA', 'headers', '(ecology_JSessionid)'],
    ['华为_HUAWEI_ASG2050', 'code', '(HUAWEI ASG2050)'],
    ['360网站卫士', 'code', '(360wzb)'],
    ['Citrix-XenServer', 'code', '(Citrix Systems, Inc. XenServer)'],
    ['H3C ER2100V2', 'code', '(ER2100V2系统管理)'],
    ['zabbix', 'cookie', '(zbx_sessionid)'],
    ['zabbix', 'code', '(images/general/zabbix.ico|Zabbix SIA)'],
    ['CISCO_VPN', 'headers', '(webvpn)'],
    ['360站长平台', 'code', '(360-site-verification)'],
    ['H3C ER3108GW', 'code', '(ER3108GW系统管理)'],
    ['o2security_vpn', 'headers', '(client_param=install_active)'],
    ['H3C ER3260G2', 'code', '(ER3260G2系统管理)'],
    ['H3C ICG1000', 'code', '(ICG1000系统管理)'],
    ['CISCO-CX20', 'code', '(CISCO-CX20)'],
    ['H3C ER5200', 'code', '(ER5200系统管理)'],
    ['linksys-vpn-bragap14-parintins', 'code',
        '(linksys-vpn-bragap14-parintins)'],
    ['360网站卫士常用前端公共库', 'code', '(libs.useso.com)'],
    ['H3C ER3100', 'code', '(ER3100系统管理)'],
    ['H3C-SecBlade-FireWall', 'code', '(js/MulPlatAPI.js)'],
    ['360webfacil_360WebManager', 'code', '(publico/template/)'],
    ['Citrix_Netscaler', 'code', '(ns_af)'],
    ['H3C ER6300G2', 'code', '(ER6300G2系统管理)'],
    ['H3C ER3260', 'code', '(ER3260系统管理)'],
    ['华为_HUAWEI_SRG3250', 'code', '(HUAWEI SRG3250)'],
    ['exchange', 'code', '(/owa/auth.owa)'],
    ['Spark_Worker', 'code', '(Spark Worker at)'],
    ['H3C ER3108G', 'code', '(ER3108G系统管理)'],
    ['深信服防火墙类产品', 'code', '(SANGFOR FW)'],
    ['Citrix-ConfProxy', 'code', '(confproxy)'],
    ['360网站安全检测', 'code', '(webscan.360.cn/status/pai/hash)'],
    ['H3C ER5200G2', 'code', '(ER5200G2系统管理)'],
    ['华为（HUAWEI）安全设备', 'code', '(sweb-lib/resource/)'],
    ['H3C ER6300', 'code', '(ER6300系统管理)'],
    ['华为_HUAWEI_ASG2100', 'code', '(HUAWEI ASG2100)'],
    ['TP-Link 3600 DD-WRT', 'code', '(TP-Link 3600 DD-WRT)'],
    ['NETGEAR WNDR3600', 'code', '(NETGEAR WNDR3600)'],
    ['H3C ER2100', 'code', '(ER2100系统管理)'],
    ['绿盟下一代防火墙', 'code', '(NSFOCUS NF)'],
    ['jira', 'code', '(jira.webresources)'],
    ['金和协同管理平台', 'code', '(金和协同管理平台)'],
    ['Citrix-NetScaler', 'code', '(NS-CACHE)'],
    ['linksys-vpn', 'headers', '(linksys-vpn)'],
    ['通达OA', 'code', '(/static/images/tongda.ico)'],
    ['华为（HUAWEI）Secoway设备', 'code', '(Secoway)'],
    ['华为_HUAWEI_SRG1220', 'code', '(HUAWEI SRG1220)'],
    ['H3C ER2100n', 'code', '(ER2100n系统管理)'],
    ['H3C ER8300G2', 'code', '(ER8300G2系统管理)'],
    ['金蝶政务GSiS', 'code', '(/kdgs/script/kdgs.js)'],
    ['Jboss', 'code', '(Welcome to JBoss|jboss.css)'],
    ['Jboss', 'headers', '(JBoss)'],
]
pyVersion = str(sys.version_info.major)+"."+str(sys.version_info.minor)+"."+str(sys.version_info.micro)
WebInfoDict = []
old_URL_List = list()
new_URL_List = list()
def check_url(url,urlList):
    _ = []
    for i in urlList:
        try:
            i = urlparse(i)
            if not i.scheme and not i.netloc and i.path:
                i = urlparse(url + i.path)
            if i.scheme:
                if i.path[0:1] == '/':

                    i = i.scheme + '://' + i.netloc + i.path + '?' + i.query
                else:
                    i = i.scheme + '://' + i.netloc + '/' + i.path + '?' + i.query

            elif i.netloc:
                if i.path[0:1] == '/':

                    i = 'http://' + i.netloc + i.path + '?' + i.query
                else:
                    i = 'http://' + i.netloc + '/' + i.path + '?' + i.query
            else:
                if i.path[0:1] == '/':
                    i = 'http://' + url + i.path + '?' + i.query
                else:
                    # print(i)
                    i = 'http://' + url + '/' + i.path + '?' + i.query
                    # print(i)
        except Exception as e:
            continue
        if '///' in i:
            i = i.replace('///', '//')
        if i[-1] == '?':
            i = i.replace('?', '')
        _.append(i)
    return list(set(_))

class requestWeb(threading.Thread):
    def __init__(self, url, sem):
        super(requestWeb, self).__init__()
        self.headers = {
            "User-Agent": random.choice(USER_AGENTS),
        }
        self.url = url
        self.sem = sem

    def run(self):
        s = requests.Session()
        s.keep_alive = False
        s.headers = self.headers
        s.verify = False
        shiroCookie = {'rememberMe': '1'}
        if args.proxy:
            scheme = urlparse(self.url).scheme
            if pyVersion < "3.8":
                s.proxies = {scheme:"{0}".format(args.proxy) }
            else:
                s.proxies = {scheme :args.proxy}
        s.cookies.update(shiroCookie)
        try:
            response = s.get(self.url, timeout=5)
            try:
                html = response.content.decode('utf-8')
            except UnicodeDecodeError:
                html = response.content.decode('gbk', 'ignore')
            lock.acquire()
            WebInfo = {
                'domain':urlparse(self.url).netloc,
                "url":[self.url],
                "headers": response.headers,
                "status_code": response.status_code,
                "cookie": response.cookies,
                "html": html,
                "fingerprint": [],
                "title": [],
                "server": []
            }
            fingerprint(WebInfo).run()
            find_by_url(self.url,html)
            response.close()
            lock.release()

        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.ChunkedEncodingError:
            pass
        except KeyboardInterrupt:
            lock.release()
            pass
        self.sem.release()


class fingerprint():
    def __init__(self,WebInfo):
        self.rex = re.compile('<title>(.*?)</title>')
        self.WebInfo = WebInfo

    def check(self,rulesRegex, fingerprint,string):
        resHeads = re.findall(rulesRegex,str(string))
        if resHeads:
            return fingerprint

    def run(self):
        if 'server' in self.WebInfo.get('headers'):
            webServer = self.WebInfo.get("headers").get('server')
        else:
            webServer = "None"
        webTitles = re.findall(self.rex, self.WebInfo.get('html'))
        if webTitles:
            webTitle = webTitles[0]
        else:
            webTitle = "None"
        self.WebInfo.get('server').append(webServer)
        self.WebInfo.get('title').append(webTitle)
        for rule in ruleDatas:
            fingerprint = rule[0]
            rulesRegex = rule[2]
            if "headers" == rule[1]:
                fingerprint = self.check(rulesRegex, fingerprint,self.WebInfo.get('headers'))
            if "cookie" == rule[1]:
                fingerprint = self.check(rulesRegex, fingerprint,self.WebInfo.get("cookie"))
            else:
                fingerprint = self.check(rulesRegex, fingerprint,self.WebInfo.get("html"))
            self.WebInfo.get("fingerprint").append(fingerprint)

        self.WebInfo.pop("html")
        self.WebInfo.pop("status_code")
        self.WebInfo.pop("cookie")
        self.WebInfo.pop("headers")
        self.WebInfo["fingerprint"]=list(set(self.WebInfo.get("fingerprint")))
        global WebInfoDict
        WebInfoDict.append(self.WebInfo)



def runwebs(urlList,threadNum=1):
    threads = []
    sem = threading.Semaphore(threadNum)
    try:
        for url in urlList:
            sem.acquire()
            t = requestWeb(url, sem)
            t.setDaemon(True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        exit()

def find_by_url(url,html):
    _ = []
    __ = []
    soup = BeautifulSoup(html, features="lxml")
    blacklist=[None,"/","javascript:","javascript:;","javascript:void(0);","javascript:void();"]
    global find
    for i in find:
        tags = soup.find_all(i)
        for tag in tags:
            for j in find[i]:
                _.append(tag.get(j))
    tags = soup.find_all('style')
    for tag in tags:
        _ += (re.findall(r'url[(](.*?)[)]', str(tag)))
    scripts = soup.find_all('script')
    global pattern_raw
    for script in scripts:
        pattern = re.compile(pattern_raw, re.VERBOSE)
        _.extend(re.findall(pattern, str(script)))

    for j in blacklist:
        if j in _:
            _.remove(j)
    static = ['jpg', 'png', 'gif', 'jpeg', 'bmp', 'css', 'pdf', 'svg', 'psd', 'pdd']
    for i in _:
        try:
            j = urlparse(i)
            if str(j.path.split('.')[-1].lower()) in static:
                _.remove(i)
        except TypeError:
            continue

    global new_url
    global old_url
    new_url = check_url(url, urlList=_)
    old_url.add(url)



def time():
    import time
    localtime = time.localtime(time.time())
    j = 1
    _ = ''
    for i in localtime:
        if len(str(i)) < 2:
            i = "0" + str(i)
        _ = _ + str(i)+ "_"
        j += 1
        if j > 6:
            return _


def exit():
    global WebInfoDict
    if WebInfoDict:
        _ = []
        for j in WebInfoDict:
            _.append(j.get('domain'))
        _=set(_)
        ___=[]
        for i in _:
            __ = {'domain': i,"url": [],"fingerprint": [],"title": [],"server": []}
            for j in WebInfoDict:
                if j.get('domain') == i:
                    for k in j:
                        if k == "domain":
                            continue
                        else:
                            a = set(__.get(k))
                            a.update(j.get(k))
                            __[k] = a
                else:
                    pass
            ___.append(__)
    pprint.pprint(___)
    filename = time()[0:-1] +".txt"
    path = urlparse(args.url).netloc.split(":")[0]
    if not  os.path.isdir(path):
        os.mkdir(path)
    f=codecs.open(path +"/"+filename,"w","utf-8")
    f.write(str(___))
    f.flush()
    f.close()
    sys.exit(1)

if __name__=="__main__":
    try:
        args = parse_args()
        new_url = []
        old_url = set()
        new_url.extend([args.url])
        if args.thread:
            thread = args.thread
        else:
            thread =10
        if args.deep is not True:
            while True:
                for i in new_url:
                    if i in old_url:
                        new_url.remove(i)
                runwebs(new_url,thread)
                if not new_url:
                    exit()
            else:
                for i in range(args.deep * 2):
                    for i in new_url:
                        if i in old_url:
                            new_url.remove(i)
                    runwebs(new_url,thread)
                    if not new_url:
                        exit()


    except KeyboardInterrupt:
        exit()
