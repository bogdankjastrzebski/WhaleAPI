import requests
import time
import discord
from discord import Webhook, RequestsWebhookAdapter

# Class WhaleAlertMessenger
class WhaleAlertMessenger():
    """
    WhaleAlertMessenger
    
    This class gets data from Whale Alert
    and in case of update, posts data to a
    discord server.
    """
    
    def __init__(self,
                 api_key='fQnt27Rzvml1Ibh5u5ZDU2LZ3Z5QP8jo',
                 min_value=500000,
                 sec=60,
                 path_transactions="https://api.whale-alert.io/v1/transactions",
                 webhook="https://discordapp.com/api/webhooks/809567816814428170/MAl1ToluFM1yBk0tww0_alVrx4G86cCAKSQ6t7OC8sWqJDf2qDX3Cjap70C0YBhHsKwo"):
        """
        WhaleAlertMessenger(api_key, min_value, sec)
        
        Arguments:
        * api_key - api key to whale alert 
        * min_value - minimal value of transaction in USD
        * sec - number of past seconds to check
        """
        
        # transations app
        self.path_transactions = path_transactions
        
        # set of parameters used in requesting
        self.api_key = api_key,
        self.min_value = str(min_value),
        self.sec = sec
        
        # discord hook for posting
        self.webhook = Webhook.from_url(
            webhook,
            adapter=RequestsWebhookAdapter()
        )
        
        # Data repository
        self.data = []
        
    def get(self):
        """
        get()
        
        get method gets all data from last self.sec seconds from WhaleAlert.
        """
        # parameters
        params = {
            'api_key':self.api_key,
            'min_value':self.min_value,
            'start':str(int(time.time())-self.sec)
        }
        request = requests.get(self.path_transactions, params=params).json()
        
        try:
            # get transactions
            data = request['transactions']
            
            # transform and filter transactions
            data_new = []
            for i in range(len(data)):
                if not data[i]['from'].get('owner', None) and data[i]['to'].get('owner', None) and 'unknown' not in data[i]['to']['owner']:
                    data[i]['from'] = 'unknown wallet'
                    data[i]['to']   = data[i]['to']['owner']
                    if data[i]['symbol'] == 'usdc':
                        data[i]['symbol'] = 'USDC :printer:'
                    else:
                        data[i]['symbol'] = data[i]['symbol'].upper()
                    data_new.append(data[i])
                    
            # update data
            self.data = data_new
            
        except Exception as e:
            if 'error' in request.values():
                print(request['message'])
            self.data = []
        
    def post(self):
        """
        post()
        
        post method posts data to discord.
        """
        # check if any data exists
        if not self.data:
            return 
        
        # build message
        s = ''
        for d in self.data:
            amount = float(d['amount_usd'])
            s += "{light_1} {light_2} {light_3} {warning} ```{amount: >12_} {unit: <5} {amount_usd: <20} {f: >15} -> {t: <15}\n```".format(
                light_1=':rotating_light:' if amount >          0 else '      ',
                light_2=':rotating_light:' if amount >  1_000_000 else '      ',
                light_3=':rotating_light:' if amount >  5_000_000 else '      ',
                warning=':warning:'        if amount > 10_000_000 else '      ',
                amount =round(float(d['amount']),1),
                unit   =d['symbol'],
                amount_usd = '({:_} USD)'.format(round(float(d['amount_usd']),1)),
                f = str(d['from']),
                t = str(d['to'])
            )
            
        # send to discord
        self.webhook.send(s)