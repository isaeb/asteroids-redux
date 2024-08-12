import webbrowser
import time
import asyncio

import libraries.constants as constants
from libraries.services.asyncRequests import RequestHandler

from json import *
from base64 import b64decode, b64encode


key = b64decode('Xiv8RJa+6fg9RavikRqFpw==')
IV = ''
cipher = ''# Cipher(algorithms.AES(key), modes.CBC(IV))


class NGIO:
    def __init__(self):
        self.userID = None
        self.userName = ''
        self.sessionID = None
        self.progress = 0
        self.loggedIn = False
        self.waiting = False
        self.request = RequestHandler()
        self.openPassport = False
        self.sleeping = False
        self.boards = []

    async def update(self, game:dict):

        if self.sleeping:
            self.progress += game['frametime'] / 1000
            if self.progress >= 5:
                self.sleeping = False
                self.progress = 0
            return
        
        if self.waiting:
            if response := self.request.response():
                try:
                    result = loads(response)['result']
                except:
                    result = dict(response)
                    print(response)

                match result['echo']:
                    case 'newSession':
                        self.sessionID = result['data']['session']['id']

                        # Open NG Passport
                        url = result['data']['session']['passport_url']
                        webbrowser.open(url)

                        await self.checkSession()
                        self.sleeping = True

                    case 'checkSession':
                        user = result['data']['session']['user']
                        if user is not None:
                            self.userID = result['data']['session']['user']['id']
                            self.userName = result['data']['session']['user']['name']
                            self.sessionID = result['data']['session']['id']
                            self.loggedIn = True
                            self.waiting = False
                            return
                        
                        await self.checkSession()
                        self.sleeping = True

                    case 'getBoards':
                        self.boards = result['data']['scoreboards']
                        print(self.boards)
                        self.waiting = False


    async def newSession(self):
        # Create a Session
        obj = {
                'app_id': '58698:0SXtVsBf',
                'execute': {
                    'component': 'App.startSession',
                    'echo': 'newSession'
                }
            }
        
        req = {
            'url':f'http://www.newgrounds.io/gateway_v3.php?request={dumps(obj)}',
            'headers': {'Content-Type': 'application/json'}
            }

        await self.request.post(**req)
        self.waiting = True

    async def checkSession(self):
        # Check a Session
        obj = {
                'app_id': '58698:0SXtVsBf',
                'session_id': self.sessionID,
                'execute': {
                    'component': 'App.checkSession',
                    'echo': 'checkSession'
                }
            }
        
        req = {
            'url':f'http://www.newgrounds.io/gateway_v3.php?request={dumps(obj)}',
            'headers': {'Content-Type': 'application/json'}
            }

        await self.request.post(**req)
        self.waiting = True

    def postScore(self, session_id:str, board_id:str, score:int):
        '''
        json_str = dumps({
                'component': 'ScoreBoard.postScore',
                'parameters': {'id':board_id, 'value':str(score)}
            })
        
        # Convert string to bytes
        data_bytes = json_str.encode('utf-8')
        
        # Pad the data to be a multiple of 16 bytes
        padded_data = pad(data_bytes, AES.block_size)

        # Encrypt the data
        encrypted_data = cipher.encrypt(padded_data)

        # Concatenate IV and encrypted data
        encrypted_data_with_iv = IV + encrypted_data

        # Encode the encrypted data with IV to Base64
        base64_encoded_data = b64encode(encrypted_data_with_iv).decode('utf-8')

        input =  {'app_id': constants.APP_ID, 'session_id':session_id,
            'execute': {
                'secure': base64_encoded_data}
        }

        r = post("http://www.newgrounds.io/gateway_v3.php", data={"input":dumps(input)})
        return r.text
        '''
        pass

    async def getBoards(self):
        obj = {
                'app_id': '58698:0SXtVsBf',
                'execute': {
                    'component': 'ScoreBoard.getBoards',
                    'echo': 'getBoards'
                }
            }
        
        req = {
            'url':f'http://www.newgrounds.io/gateway_v3.php?request={dumps(obj)}',
            'headers': {'Content-Type': 'application/json'}
            }
        
        await self.request.post(**req)
        self.waiting = True
