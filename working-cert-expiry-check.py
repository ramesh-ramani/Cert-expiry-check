import ssl
import socket
import boto3
import slackweb
import datetime
from datetime import date

##Slack Call##

def slack_call(v,s,account): 
         slack = slackweb.Slack(url="")
         slack.notify(text="Cert for "+str(v)+" is going to expire in 90 days. The Expiry Date is: "+str(s))

##SSL Call##

def ssl_call(elb_dict,alb_dict,account,region_name): 
  context = ssl.create_default_context()
  dict_2={}

  ##Check Certs on ELBs##
  slack.notify(text="Certs for ELBs, The Account is: "+str(account)+" and the Region is: "+str(region_name))
  slack.notify(text="==============================================")
  for k,v in elb_dict.items():
     try:
        ssl.match_hostname = lambda cert, hostname: True
        conn = context.wrap_socket(socket.socket(socket.AF_INET),server_hostname=v)
        conn.settimeout(3.0)
        conn.connect((v, 443))
        ssl_info = conn.getpeercert()
        t = ssl_info.get("notAfter").split(' ')
        s = (t[0]+" "+t[1]+" "+t[3])
        parsed = datetime.datetime.strptime(s, '%b %d %Y').date()
        EndDate = parsed-datetime.timedelta(days=90)
        #print(EndDate)
        if EndDate < datetime.date.today(): 
                    s=ssl_info.get("notAfter")
#                   print("Cert for "f'"{v}"' " is going to expire in 90 Days. The Expiry Date is: ",ssl_info.get("notAfter"))
                    slack_call(v,s,account)      
        else: continue
     except: 
        print(v," timed out for connection test")
        continue
  
  ##Check Certs on ALBs##
  slack.notify(text="*us-west-2 ALBs, and the account is: *"+str(account))
  slack.notify(text="==============================================")
  for k,v in alb_dict.items():
     try:
        ssl.match_hostname = lambda cert, hostname: True
        conn = context.wrap_socket(socket.socket(socket.AF_INET),server_hostname=v)
        conn.settimeout(3.0)
        conn.connect((v, 443))
        ssl_info = conn.getpeercert()
        t = ssl_info.get("notAfter").split(' ')
        s = (t[0]+" "+t[1]+" "+t[3])
        parsed = datetime.datetime.strptime(s, '%b %d %Y').date()
        EndDate = parsed-datetime.timedelta(days=90)
        #print(EndDate)
        if EndDate < datetime.date.today(): 
                    s=ssl_info.get("notAfter")
#                   print("Cert for "f'"{v}"' " is going to expire in 90 Days. The Expiry Date is: ",ssl_info.get("notAfter"))
                    slack_call(v,s,account)      
        else: continue
     except: 
        print(v," timed out for connection test")
        continue


##LB Check##

def LB_Check(account,client,region_name):
  print(account)
  elb_dict={}
  alb_dict={}
  l_lst=list()
  e_lst=list()
  elbList = session.client('elbv2')
  elbList_1 = session.client('elb')
  ec2 = session.resource('ec2')
  bals = elbList.describe_load_balancers()
  bals1 = elbList_1.describe_load_balancers()
  
  ##ELBs##
  for i in bals['LoadBalancers']:
      alb_dict[i['LoadBalancerName']]=i['DNSName']
  ##ALBs##
  for i in bals1['LoadBalancerDescriptions']:
      elb_dict[i['LoadBalancerName']]=i['DNSName']
  ssl_call(elb_dict,alb_dict,account,region_name)


##Main###

today = date.today()
account_lst = [""] ##List all accounts that you have configured in your AWS creds file
region_name="us-west-2"
for i in account_lst:
   session = boto3.Session(profile_name=i,region_name='us-west-2')
   client = session.client('ec2')
   LB_Check(i,client,region_name)

region_name="eu-central-1"
for i in account_lst:
   session = boto3.Session(profile_name=i,region_name='us-west-2')
   client = session.client('ec2')
   LB_Check(i,client,region_name)
