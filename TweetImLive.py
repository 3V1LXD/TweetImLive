import os
import requests, tweepy
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import *

class TweetImLive(App):
    def build(self):
        self.app_layout = GridLayout(cols=1,rows=2)
        self.menu_layout = GridLayout(cols=3, rows=1, size_hint = (1,0.1))

        self.setting_btn = Button(text="Settings")
        self.setting_btn.bind(on_press=self.open_settings)

        self.get_btn = Button(text="Refresh")
        self.get_btn.bind(on_press=self.refresh)

        self.tweet_btn = Button(text="Tweet")
        self.tweet_btn.bind(on_press=self.tweet)

        self.menu_layout.add_widget(self.setting_btn)
        self.menu_layout.add_widget(self.get_btn)
        self.menu_layout.add_widget(self.tweet_btn)

        self.thumbnail_layout = GridLayout(cols=1,rows=4, size_hint = (1,0.9))

        self.app_layout.add_widget(self.menu_layout)
        self.app_layout.add_widget(self.thumbnail_layout)

        Config.read('config.ini')
        if os.path.isfile('config.ini') == False:
            Config.adddefaultsection('twitch')
            Config.adddefaultsection('twitter')
            Config.set('twitch', 'client_id', 'YOUR_CLIENT_ID')
            Config.set('twitch', 'client_secret', 'YOUR_CLIENT_SECRET')
            Config.set('twitter', 'message', 'YOUR_MESSAGE')
            Config.set('twitter', 'api_key', 'YOUR_API_KEY')
            Config.set('twitter', 'api_key_secret', 'YOUR_API_KEY_SECRET')
            Config.set('twitter', 'access_token', 'YOUR_ACCESS_TOKEN')
            Config.set('twitter', 'access_token_secret', 'YOUR_ACCESS_TOKEN_SECRET')
            Config.set('twitch', 'username', 'I\'m #live #streaming stream_game on #Twitch! \n stream_title \n https://www.twitch.tv/username')
            Config.write()

        self.read_settings(self)
        if self.username != '' and self.client_id != '' and self.client_secret != '':
            self.refresh(self)

        return self.app_layout

    def get_access_token(self, instance):
        access_token_url = 'https://id.twitch.tv/oauth2/token?client_id=' + self.client_id + '&client_secret=' + self.client_secret + '&grant_type=client_credentials'
        access_token_response = requests.post(access_token_url)
        access_token = access_token_response.json()['access_token']
        return access_token

    def get_stream_info(self, instance):
        access_token = self.get_access_token(self)
        stream_url = 'https://api.twitch.tv/helix/streams?user_login=' + self.username
        stream_response = requests.get(stream_url, headers={'Authorization': 'Bearer ' + access_token, 'Client-ID': self.client_id})
        stream_json = stream_response.json()

        if stream_json['data'] != []:
            live = True
            stream_title = stream_json['data'][0]['title']
            stream_game = stream_json['data'][0]['game_name']
            stream_thumbnail = stream_json['data'][0]['thumbnail_url']
            stream_thumbnail = stream_thumbnail.replace('{width}', '1920').replace('{height}', '1080')
            stream_thumbnail_response = requests.get(stream_thumbnail)
            stream_thumbnail_file = open('stream_thumbnail.jpg', 'wb')
            stream_thumbnail_file.write(stream_thumbnail_response.content)
            stream_thumbnail_file.close()
            return live, stream_title, stream_game
        else:
            live = False
            return live, '', ''

    def tweet(self, instance):
        if self.live:
            auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            api = tweepy.API(auth)
            message = self.message.replace('stream_game', self.stream_game).replace('stream_title', self.stream_title).replace('username', self.username)
            api.update_status_with_media(message,'stream_thumbnail.jpg')
            self.popup = Popup(title='Alert', content=GridLayout(cols=1, rows=2), size_hint=(None, None), size=(400, 150))
            self.popup.content.add_widget(Label(text='Tweet sent!'))
            self.popup.content.add_widget(Button(text='Ok', on_press=self.popup.dismiss))
            self.popup.open()
        else:
            self.popup = Popup(title='Alert', content=GridLayout(cols=1, rows=2), size_hint=(None, None), size=(400, 150))
            self.popup.content.add_widget(Label(text='Stream is offline'))
            self.popup.content.add_widget(Button(text='Cancel', on_press=self.popup.dismiss))
            self.popup.open()

    def open_settings(self, instance):
        self.read_settings(self)
        self.popup = Popup(title='Settings', content=GridLayout(cols=2, rows=9), size_hint=(0.8, 0.8))
        self.popup.open()
        self.popup.content.add_widget(Label(text='Twitch Username'))
        self.username_input = TextInput(text=self.username, multiline=False, size=(400, 40))
        self.popup.content.add_widget(self.username_input)
        self.popup.content.add_widget(Label(text='Twitch Client ID'))
        self.client_id_input = TextInput(text=self.client_id, multiline=False, password=True)
        self.popup.content.add_widget(self.client_id_input)
        self.popup.content.add_widget(Label(text='Twitch Client Secret'))
        self.client_secret_input = TextInput(text=self.client_secret, multiline=False, password=True)
        self.popup.content.add_widget(self.client_secret_input)
        self.popup.content.add_widget(Label(text='Tweet Message'))
        self.message_input = TextInput(text=self.message, multiline=True)
        self.popup.content.add_widget(self.message_input)
        self.popup.content.add_widget(Label(text='Twitter API Key'))
        self.api_key_input = TextInput(text=self.api_key, multiline=False, password=True)
        self.popup.content.add_widget(self.api_key_input)
        self.popup.content.add_widget(Label(text='Twitter API Key Secret'))
        self.api_key_secret_input = TextInput(text=self.api_key_secret, multiline=False, password=True)
        self.popup.content.add_widget(self.api_key_secret_input)
        self.popup.content.add_widget(Label(text='Twitter Access Token'))
        self.access_token_input = TextInput(text=self.access_token, multiline=False, password=True)
        self.popup.content.add_widget(self.access_token_input)
        self.popup.content.add_widget(Label(text='Twitter Access Token Secret'))
        self.access_token_secret_input = TextInput(text=self.access_token_secret, multiline=False, password=True)
        self.popup.content.add_widget(self.access_token_secret_input)
        self.popup.content.add_widget(Button(text='Cancel', on_press=self.popup.dismiss))
        self.popup.content.add_widget(Button(text='Save', on_press=self.save_settings))

    def save_settings(self, instance):
        self.message = self.message_input.text
        self.username = self.username_input.text
        self.client_id = self.client_id_input.text
        self.client_secret = self.client_secret_input.text
        self.api_key = self.api_key_input.text
        self.api_key_secret = self.api_key_secret_input.text
        self.access_token = self.access_token_input.text
        self.access_token_secret = self.access_token_secret_input.text
        Config.set('twitter', 'message', self.message)
        Config.set('twitch', 'username', self.username)
        Config.set('twitch', 'client_id', self.client_id)
        Config.set('twitch', 'client_secret', self.client_secret)
        Config.set('twitter', 'api_key', self.api_key)
        Config.set('twitter', 'api_key_secret', self.api_key_secret)
        Config.set('twitter', 'access_token', self.access_token)
        Config.set('twitter', 'access_token_secret', self.access_token_secret)
        
        Config.write()
        self.popup.dismiss()
        print('Settings saved')

    def read_settings(self, instance):
        Config.read('config.ini')
        self.message = Config.get('twitter', 'message')
        self.username = Config.get('twitch', 'username')
        self.client_id = Config.get('twitch', 'client_id')
        self.client_secret = Config.get('twitch', 'client_secret')
        self.api_key = Config.get('twitter', 'api_key')
        self.api_key_secret = Config.get('twitter', 'api_key_secret')
        self.access_token = Config.get('twitter', 'access_token')
        self.access_token_secret = Config.get('twitter', 'access_token_secret')
        print('Settings read')

    def refresh(self, instance):
        self.thumbnail_layout.clear_widgets()
        self.live, self.stream_title, self.stream_game = self.get_stream_info(self)
        if self.live:
            self.stream_title_label = Label(text=self.stream_title, font_size=16, bold = True, text_size = (Window.width,None), halign = 'left', padding = (10,0))
            self.stream_game_label = Label(text=self.stream_game, font_size=16, text_size = (Window.width,None), halign = 'left', padding = (10,0))
            self.stream_thumbnail = Image(source='stream_thumbnail.jpg', size_hint_y=10)
            self.stream_thumbnail.reload()
            self.thumbnail_layout.add_widget(self.stream_thumbnail)
            self.thumbnail_layout.add_widget(self.stream_title_label)
            self.thumbnail_layout.add_widget(self.stream_game_label)
        else:
            self.offline_label = Label(text='Stream is offline', size_hint_y=0.1, size_hint_x=1)
            self.thumbnail_layout.add_widget(self.offline_label)

if __name__ == '__main__':
    TweetImLive().run()