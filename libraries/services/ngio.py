import webbrowser
import sys
import platform
import secrets

from pathlib import Path

from libraries.constants import *
from libraries.services.asyncRequests import RequestHandler

from json import *
from base64 import b64decode, b64encode
from typing import Literal


# Function to pad the data to a multiple of 16 bytes
def pad(data):
    padding_length = (16 - len(data) % 16) % 16
    padding = bytes([padding_length] * padding_length)
    return data + padding

def encryptWeb(data:str, key):
    return platform.window.encryptData(key, data)

class NGIO:
    def __init__(self):
        self.userID = None
        self.userName = ''
        self.sessionID = None
        self.progress = 0
        self.loggedIn = False
        self.waiting = 0
        self.execute = []
        self.request = RequestHandler()
        self.openPassport = False
        self.sleeping = False
        self.passportURL = None

        # Scoreboards
        self.loadScores = True
        self.classicStartIndex = 0
        self.classicPeriod = 'A'
        self.classicBoard = []

        self.reduxStartIndex = 0
        self.reduxPeriod = 'A'
        self.reduxBoard = []

        is_web: bool = sys.platform in ("emscripten", "wasi")
        if is_web:
            jsCode = Path('libraries/services/aes.js').read_text()
            platform.window.eval(jsCode)

            platform.window.eval("""
                                function getIframeVariable(varName) {
                                    const urlParams = new URLSearchParams(window.location.search);
                                    return urlParams.get(varName);
                                }
            """)
            self.sessionID = platform.window.getIframeVariable('ngio_session_id')

    async def login(self):
        if self.passportURL is None:
            return
        
        # Open NG Passport
        webbrowser.open(self.passportURL)
        await self.checkSessionLogin()

        self.sleeping = True

    async def checkSessionLogin(self):

        if self.sessionID is None:
            return
        
        # Check a Session and Login
        obj = {
                'app_id': '58698:0SXtVsBf',
                'session_id': self.sessionID,
                'execute': {
                    'component': 'App.checkSession',
                    'echo': 'checkSessionLogin'
                }
            }
        
        req = {
            'url':f'https://www.newgrounds.io/gateway_v3.php?request={dumps(obj)}',
            'headers': {'Content-Type': 'application/json'}
            }

        self.execute.append(req)

    async def update(self, game:dict):

        if self.sleeping:
            self.progress += game['frametime'] / 1000
            if self.progress >= 5:
                self.sleeping = False
                self.progress = 0
            return
        
        if self.loadScores and self.loggedIn and self.sessionID is not None:
            await game['NGIO'].getScores('classic')
            await game['NGIO'].getScores('redux')
            self.loadScores = False
        
        if self.waiting > 0:
            if response := self.request.response():
                try:
                    result = loads(response)['result']
                    print(result)
                except Exception as e:
                    print(e, response)
                    result = response['result']

                try:
                    match result['echo']:
                        case 'newSession':
                            self.sessionID = result['data']['session']['id']
                            self.passportURL = result['data']['session']['passport_url']

                            self.waiting -= 1

                        case 'checkSession':
                            user = result['data']['session']['user']
                            # Set up user details
                            if user is not None:
                                self.userID = result['data']['session']['user']['id']
                                self.userName = result['data']['session']['user']['name']
                                self.sessionID = result['data']['session']['id']
                                self.loggedIn = True
                                self.waiting -= 1

                        case 'checkSessionLogin':
                            user = result['data']['session']['user']
                            # Set up user details
                            if user is not None:
                                self.userID = result['data']['session']['user']['id']
                                self.userName = result['data']['session']['user']['name']
                                self.sessionID = result['data']['session']['id']
                                self.loggedIn = True
                                self.waiting -= 1
                                return
                            
                            # Check again for login
                            await self.checkSessionLogin()
                            self.sleeping = True

                        case 'getBoards':
                            self.boards = result['data']['scoreboards']
                            self.waiting -= 1
                        
                        case 'getScores':
                            match result['data']['scoreboard']['name']:
                                case 'Classic':
                                    self.classicBoard = result['data']['scores']
                                    self.classicPeriod = result['data']['period']
                                    self.classicStartIndex = result['data']['limit']
                                
                                case 'Redux':
                                    self.reduxBoard = result['data']['scores']
                                    self.reduxPeriod = result['data']['period']
                                    self.reduxStartIndex = result['data']['limit']
                    self.waiting = 0
                    
                except Exception as e:
                    print(e, response)
                    self.waiting -= 1
        else:
            if len(self.execute) > 0 and self.waiting == 0:
                print(self.execute)
                req = self.execute[0]
                self.execute.pop(0)
                await self.request.post(**req)
                self.waiting += 1

    async def newSession(self):
        # Create a Session
        obj = {
                'app_id': '58698:0SXtVsBf',
                'execute': {
                    'component': 'App.startSession',
                    'parameters': {
                        'force': False
                    },
                    'echo': 'newSession'
                }
            }
        
        req = {
            'url':f'https://www.newgrounds.io/gateway_v3.php?request={dumps(obj)}',
            'headers': {'Content-Type': 'application/json'}
            }

        self.execute.append(req)

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
            'url':f'https://www.newgrounds.io/gateway_v3.php?request={dumps(obj)}',
            'headers': {'Content-Type': 'application/json'}
            }

        self.execute.append(req)

    def postScore(self, board_id:str, score:int):
        print('posting score...')
        platform.window.Call(APP_ID, self.sessionID, APP_KEY, board_id, score)

    async def getScores(self, mode:Literal['classic', 'redux'], limit:int=10, period:Literal['D', 'W', 'M', 'Y', 'A']='A', skip:int=0, social:bool=False, user:str=None):
        if self.sessionID is None or not self.loggedIn:
            return
        
        boardID = {'classic': CLASSIC_ID, 'redux': REDUX_ID}[mode]
        
        # Check a Session
        obj = {
                'app_id': '58698:0SXtVsBf',
                'session_id': self.sessionID,
                'execute': {
                    'component': 'ScoreBoard.getScores',
                    'parameters': {
                        'id': f'{boardID}',
                        'limit': f'{limit}',
                        'period': f'{period}',
                        'skip': f'{skip}',
                        'social': f'{social}'
                    },
                    'echo': 'getScores'
                }
            }
        
        if user is not None:
            obj['execute']['parameters']['user'] = f'{user}'
        
        req = {
            'url':f'https://www.newgrounds.io/gateway_v3.php?request={dumps(obj)}',
            'headers': {'Content-Type': 'application/json'}
            }

        self.execute.append(req)

    async def getBoards(self):
        obj = {
                'app_id': '58698:0SXtVsBf',
                'execute': {
                    'component': 'ScoreBoard.getBoards',
                    'echo': 'getBoards'
                }
            }
        
        req = {
            'url':f'https://www.newgrounds.io/gateway_v3.php?request={dumps(obj)}',
            'headers': {'Content-Type': 'application/json'}
            }
        
        self.execute.append(req)
