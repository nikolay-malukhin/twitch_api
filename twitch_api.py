import requests
import json

# I suppose that we don't need two instance of TwitchApi class in application.


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TwitchApi(metaclass=Singleton):
    data = {}
    api_call_headers = {}

    def __init__(self):
        # @todo move credentials to .env
        api_auth = 'https://id.twitch.tv/oauth2/token'
        TwitchApi.data = {
            'client_id': '',
            'client_secret': '',
            'grant_type': 'client_credentials'
        }

        response = requests.post(api_auth, data=TwitchApi.data)
        tokens = json.loads(response.text)
        TwitchApi.api_call_headers = {'Authorization': 'Bearer ' + tokens['access_token'],
                                      'client-id': TwitchApi.data["client_id"]}

    def get_user_info(self, *args, **kwargs):
        login = kwargs.get('login', None)
        user_id = kwargs.get('user_id', None)
        if login:
            api_call_response = requests.get('https://api.twitch.tv/helix/users?login=' + login,
                                             headers=TwitchApi.api_call_headers, verify=False)
        elif user_id:
            api_call_response = requests.get('https://api.twitch.tv/helix/users?user_id=' + user_id,
                                             headers=TwitchApi.api_call_headers, verify=False)
        else:
            return None
        response = json.loads(api_call_response.text)
        return response

    def get_followers(self, user_id):
        api_call_response = requests.get('https://api.twitch.tv/helix/users/follows?to_id=' + user_id,
                                         headers=TwitchApi.api_call_headers, verify=False)
        return json.loads(api_call_response.text)

    def get_is_subscribed(self, broadcaster_id, user_id):
        api_call_response = requests.get('https://api.twitch.tv/helix/users/follows?from_id=' + user_id,
                                         headers=TwitchApi.api_call_headers, verify=False)
        users = json.loads(api_call_response.text)
        for follow in users['data']:
            if follow['to_id'] == broadcaster_id:
                return True
        return False

    # I don't found api method for this. I can suppose, we can get list of videos
    # and after that get comments for each video.
    # It is not proper way, but I don't know hot do it better.
    def get_chats_list(self, user_id):

        api_call_response = requests.get("https://api.twitch.tv/helix/videos?user_id="  + user_id,
                                         headers=TwitchApi.api_call_headers, verify=False)
        videos = json.loads(api_call_response.text)
        print(videos['data'][0])
        comments = {}
        for video in videos['data']:
            api_call_response = requests.get("https://api.twitch.tv/v5/videos/" + video["id"] + "/comments",
                                         headers=TwitchApi.api_call_headers, verify=False)
            comments[video["id"]] = json.loads(api_call_response.text)
        return comments


api = TwitchApi()

user_info = api.get_user_info(login='liza_longhair')

followers = api.get_followers(user_id='558927772')

is_subscribed = api.get_is_subscribed(broadcaster_id='558927772', user_id='677082017')

chats = api.get_chats_list(user_id='558927772')