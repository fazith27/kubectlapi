import os
import logging
import json
import requests
from flask import abort
from threading import Thread
from flask import request, Flask
from time import time

app = Flask(__name__)
logging.basicConfig(filename='/var/log/kubectlapi.log',level=logging.DEBUG,format='%(asctime)s %(message)s', filemode='w')
logger=logging.getLogger()
TOKEN=os.environ['TOKEN']
CHANNEL=os.environ['CHANNEL']
COMMAND=os.environ['COMMAND']

@app.route('/', methods=['GET'],)
def home():
    print('HEALTH CHECK')
    logger.info('HEALTH CHECK')
    return respond({'response_type': 'in_channel', 'text':'I am OK!'})

@app.route('/kubectl', methods=['POST'],)
def kubectl():
    try:      
        pref_list = ['kubectl get', 'kubectl version','kubectl describe']
        block_list = ['>','<','&','kubectl get log']
        slack_webhook_url_regex='https://hooks.slack.com/'
        token = request.form['token']
        channel = request.form['channel_name']
        command = request.form['command']
        query = request.form['text']        
        response_url = request.form['response_url']
        print('Request details : Channel = ',channel,' Command = ',command,' Query = ',query,', Response URL = ',response_url)
        logger.info('Request details : Channel = %s, Command =%s, Query = %s, Response URL = %s',channel,command,query,response_url)
        if token != TOKEN:
            print('Invalid Token : ',token)
            logger.info('Invalid Token : %s',token)
            return respond({'response_type': 'in_channel', 'text':'Invalid Token'})
        if channel != CHANNEL:
            print('Invalid Channel : ',channel)
            logger.info('Invalid Channel : %s',channel)
            return respond({'response_type': 'in_channel', 'text':'Invalid Channel'})        
        if command != COMMAND:
            print('Invalid Slash Command : ',command)
            logger.info('Invalid Slash Command : %s',command)
            return respond({'response_type': 'in_channel', 'text':'Invalid Slash Command'})            
        if not query.startswith(tuple(pref_list)) or any([x in query for x in block_list]) :
            print('Invalid Kubectl query : ',query)
            logger.info('Invalid Kubectl query : %s',query)
            return respond({'response_type': 'in_channel', 'text':'Invalid Kubectl query'})
        if not response_url.startswith(slack_webhook_url_regex):
            print('Invalid slack response url : ',slack_webhook_url_regex)
            logger.info('Invalid slack response url query : %s',slack_webhook_url_regex)
            return respond({'response_type': 'in_channel', 'text':'Invalid slack response url'})
        thread = Thread(target=querykubectl, args=[query,response_url])
        thread.start()                        
    except RuntimeError as err:
        print('XXXXXXXX RuntimeError XXXXXXXX = ',err)
        logger.info('XXXXXXXX RuntimeError XXXXXXXX : %s',err)
        return respond({'response_type': 'in_channel', 'text':'Runtime Error'})
    return respond()

def querykubectl(query,response_url):
    try:
        stream = os.popen(query+" 2>&1", "r")
        output = stream.read()
        print('Kubectl query response = ',output)
        logger.info('Kubectl query response : %s',output)
    except RuntimeError as err:
        print('XXXXXXXX RuntimeError XXXXXXXX = ',err)
        logger.info('XXXXXXXX RuntimeError XXXXXXXX : %s',err)
        return respond({'response_type': 'in_channel', 'text':'Runtime Error'})
    post2slack(output,response_url)    

def post2slack(output,response_url):
    formattedoutput='```'+output+'```'
    data = {
        'text': formattedoutput,
        'channel': CHANNEL
    }
    response = requests.post(response_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    print('Slack post response =  ',str(response.text),' , response code =  ',str(response.status_code))
    logger.info('Slack post response =  %s , response code =  %s',str(response.text),str(response.status_code))

def respond(response=None):
    return {
        'statusCode': 200,
        'body': json.dumps(response),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def handle_bad_request(e):
    return respond({'response_type': 'in_channel', 'text':'Bad Request'})

def handle_method_notallowed_request(e):
    return respond({'response_type': 'in_channel', 'text':'Method Not Allowed'})
    
app.register_error_handler(400, handle_bad_request)
app.register_error_handler(405, handle_method_notallowed_request)

if __name__ == '__main__':
    app.run(port=5000)
