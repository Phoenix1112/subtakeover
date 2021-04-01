import re
import os
import sys
import json
import requests
import argparse
import threading
import tldextract
import dns.resolver
from colorama import *
from concurrent.futures import ThreadPoolExecutor

requests.packages.urllib3.disable_warnings()

class SubdomainTakeover():

    def __init__(self):

        init(autoreset=True)
        self.subdomains = []
        self.blacklist = []
        self.print_lock = threading.Lock()
        self.posting_webhook = ""
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}


        self.regex = "(.*\.trafficmanager\.net*.|.*\.cloudapp\.net*.|.*\.azure\.com*.|.*\.azurewebsites\.net*.|.*\.windows\.net*.|.*\.azure-api\.net*.|.*\.azurehdinsight\.net*.|.*\.azureedge\.net*.|.*\.azurecontainer\.io*.|.*\.azuredatalakestore\.net*.|.*\.azurecr\.io*.|.*\.visualstudio\.com*.|.*\.elasticbeanstalk\.com*.)"

        if args.list and not args.stdin:

            if not os.path.exists(args.list):

                print(Fore.RED + "Subdomain List Not Found:", args.list)

                sys.exit()

            file = open(args.list, "r", encoding="utf-8").read().replace("*.","").replace(".-","").replace("-.","").split("\n")

            subs = list(set(filter(None, file)))

            self.subdomains.extend(subs)

            if not len(self.subdomains) > 0:

                print(Fore.RED + "Your Subdomain List Is Empty")

                sys.exit()

            del file
            del subs


        elif args.stdin and not args.list:

            [self.subdomains.append(x) for x in sys.stdin.read().replace("*.","").replace(".-","").replace("-.","").split("\n") if x]

            self.subdomains = list(set(self.subdomains))

            if not len(self.subdomains) > 0:

                print(Fore.RED + "Subdomains Could Not Be Read From Stdin")

                sys.exit()


        else:

            print(Fore.RED + "You Used The Wrong Parameters")

            sys.exit()

        self.finger_print = [("There isn't a GitHub Pages site here.","Github"),
        ("The specified bucket does not exist","S3BUCKET"),
        ("Fastly error: unknown domain","Fastly"),
        ("Repository not found","Bitbucket"),
        ("Trying to access your account?","Campaign Monitor"),
	("subdomain.cargo.site","Cargo Collective"),
	("404: This page could not be found.","Gemfury"),
        ("Domain uses DO name serves with no records in DO.","Digitalocean"),
	("But if you're looking to build your own website","Strikingly"),
        ("The feed has not been found.","Feedpress"),
        ("The thing you were looking for is no longer here, or never was","Ghost"),
        ("404 Blog is not found","HatenaBlog"),
        ("We could not find what you're looking for.","Help Juice"),
        ("No settings were found for this company:","Help Scout"),
        ("No such app","Heroku"),
	("Non-hub domain, The URL you've accessed does not provide a hub.","uberflip"),
        ("Uh oh. That page doesn't exist.","Intercom"),
        ("is not a registered InCloud YouTrack","JetBrains"),
        ("No Site For Domain","Kinsta"),
	("Sorry, this page is no longer available","Agile CRM"),
        ("It looks like you may have taken a wrong turn somewhere. Don't worry...","LaunchRock"),
        ("If this is your website and you've just created it, try refreshing in a minute","Anima"),
        ("Unrecognized domain","Mashery"),
        ("404 error unknown site!","Pantheon"),
        ("Project doesnt exist... yet!","Readme.io"),
        ("Sorry, this shop is currently unavailable.","Shopify"),
        ("Visiting the subdomain will redirect users to","Statuspage"),
        ("project not found","Surge.sh"),
        ("Whatever you were looking for doesn't currently exist at this address","Tumblr"),
        ("Please renew your subscription","Tilda"),
        ("This UserVoice subdomain is currently available!","UserVoice"),
        ("Do you want to register *.wordpress.com?","Wordpress")]

        resolvers_ips = ['1.1.1.1','1.0.0.1','8.8.8.8','8.8.4.4','77.88.8.8','77.88.8.1']
        self.Dnspython_Resolver = dns.resolver.Resolver()
        self.Dnspython_Resolver.timeout = 10
        self.Dnspython_Resolver.nameservers = resolvers_ips

        if self.posting_webhook:

            self.slack_status_sender("Attack Started")

        with ThreadPoolExecutor(max_workers=args.thread) as executor:
            executor.map(self.Nxdomain_Query, self.subdomains)
        
        if self.posting_webhook:

            self.slack_status_sender("Attack Finished")

    def Nxdomain_Query(self,target):

        try:

            dns_query = self.Dnspython_Resolver.resolve(target, "A")

            self.request_sender(target)

        except dns.resolver.NXDOMAIN as nx:

            cname = nx.canonical_name.to_text()

            if not target in cname:

                if cname.endswith("."):

                    cname = cname[:-1]
                
                regex_results = re.findall(self.regex, cname)

                service = None

                if regex_results:

                    if "elasticbeanstalk.com" in regex_results[0]:

                        service = "AWS"
                    
                    else:

                        service = "AZURE"

                else:

                    parse = tldextract.extract(cname).registered_domain

                    try:

                        response = requests.get(f"https://www.onlydomains.com/whois/whoisengine/request/whoisinfo.php?domain_name={parse}", verify=False, timeout=13, headers=self.header)

                        if "Not found" in response.text or "No match for" in response.text:

                            service = "AVAILABLE DOMAIN"
                    
                    except:

                        pass

                if service != None:

                    self.printer(target,service)
        
        except:
            
            pass
    
    def print_output(self,service,subdomain):

        with open(args.output, "a+", encoding="utf-8") as f:

            f.write(f"[{service}] {subdomain}\n")



    def slack_status_sender(self,information):

        try:

            slack_data = {'text':f'Status: {information}'}
            slack_send = requests.post(self.posting_webhook, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})

        except:

            pass

    def slack_takeover_sender(self,service,subdomain):

        try:

            slack_data = {'text':f'Subdomain Takeover Found[{str(service)}]: {str(subdomain)}'}
            slack_send = requests.post(self.posting_webhook, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})

        except:

            pass
    
    def request_sender(self,subdomain):

        try:

            website = "http://"+str(subdomain)
            response = requests.get(website,verify=False,headers=self.header,timeout=15).text
            self.takeover_checker(response,subdomain)

        except requests.exceptions.ConnectionError:

            website = "https://"+str(subdomain)
            response = requests.get(website,verify=False,headers=self.header,timeout=15).text
            self.takeover_checker(response,subdomain)
        
        except:

            pass
    
    def takeover_checker(self,req,target):

        for find_takeover_from_response in self.finger_print:

            if find_takeover_from_response[0] in req:

                if find_takeover_from_response[1] == "Github":
                    
                    if not target.endswith((".github.com",".githubapp.com",".github.io")):

                        self.printer(target,find_takeover_from_response[1])
                        break
                    
                    else:
                        break
                
                elif find_takeover_from_response[1] == "Fastly":
                    
                    if self.fasty_tester(target):

                        self.printer(target,find_takeover_from_response[1])
                        break

                    else:
                        break
                
                elif find_takeover_from_response[1] == "Shopify":

                    if not target.endswith(".shopify.com"):

                        self.printer(target,find_takeover_from_response[1])
                        break

                    else:
                        break
                
                elif find_takeover_from_response[1] == "Tumblr":

                    if not target.endswith((".tumblr.com",".txmblr.com")):

                        self.printer(target,find_takeover_from_response[1])
                        break

                    else:
                        break
                
                else:

                    self.printer(target,find_takeover_from_response[1])
                    break
                
    

    def printer(self,target,service):

        if args.print:

            with self.print_lock:

                print(Fore.MAGENTA + f"[{service}]",Fore.GREEN + str(target))
            
        if args.output:

            self.print_output(service,target)
            
        if self.posting_webhook:

            self.posting_webhook(service,target)

    
    def fasty_tester(self,target):

        parse = tldextract.extract(target).registered_domain

        if parse in self.blacklist:

            return False
        
        else:

            try:

                website = "http://" + "ajskkkskskjajsja." + parse
                response = requests.get(website,verify=False,headers=self.header,timeout=15).text

                if "Fastly error: unknown domain" in response:

                    self.blacklist.append(parse)

                    return False

                else:

                    return True

            except requests.exceptions.ConnectionError:

                website ="https://" + "ajskkkskskjajsja." + parse
                response = requests.get(website,verify=False,headers=self.header,timeout=15).text

                if "Fastly error: unknown domain" in response:

                     self.blacklist.append(parse)

                     return False

                else:

                    return True

            except:

                return False


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-l", "--list", required=False, metavar="", help="Subdomain List Path")
    ap.add_argument("-s", "--stdin", required=False, action="store_true", help="Read Subdomains From Stdin")
    ap.add_argument("-p", "--print", required=False, action="store_true", help="Print output(Default-Disable)")
    ap.add_argument("-t", "--thread", required=False, default=20, type=int, metavar="", help="Thread Number(Default-20)")
    ap.add_argument("-o", "--output", required=False, metavar="", help="Save Output")
    args = ap.parse_args()

    Attack_Running = SubdomainTakeover()
