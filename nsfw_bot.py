# A Tweetbot rating the NSFW-ness of photos w/ several public detectors.
import requests
import os
import tweepy
from secrets import *

from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
from sightengine.client import SightengineClient


def check_clarifai(pic_url):
    # Check a pic's NSFW rating in Clarifai.com
    try:
        app = ClarifaiApp(api_key=clarifai_api_key)
        model = app.models.get('nsfw-v1.0')
        image = ClImage(url=pic_url)
        output = model.predict([image])
        score = (output['outputs'][0]['data']['concepts'][0]['value'])
        issafe = output['outputs'][0]['data']['concepts'][0]['name']
        if issafe == 'sfw':
            score = 1-score
        else:
            pass
        score = 'Clarifai: '+str(round(100*score))+'% NSFW\n'
    except:
        score = ''

    return score


def check_deepai(pic_url):
    # Check a pic's NSFW rating in DeepAI.org
    try:
        r = requests.post(
            "https://api.deepai.org/api/nsfw-detector",
            data={
                'image': pic_url, },
            headers={'api-key': deepai_api_key}
        )
        score = 'DeepAI: ' + \
            str(round(100*r.json()['output']['nsfw_score']))+'% NSFW\n'
    except:
        score = ''
    return score


def check_sightengine(pic_url):
    try:
        client = SightengineClient(sightengine_user, sightengine_secret)
        output = client.check('nudity').set_url(pic_url)
        score = 'Sightengine: ' + \
            str(round(100*output['nudity']['raw']))+'% NSFW'
    except:
        score = ''
    return score


def tweet_image_ratings(pic_url, username, status_id):
    # Take the pic url and tweet the various NSFW ratings
    clarifai_score = check_clarifai(pic_url)
    deepai_score = check_deepai(pic_url)
    sightengine_score = check_sightengine(pic_url)
    filename = 'temp.jpg'
    request = requests.get(pic_url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)
    api.update_with_media(filename, status='Is it NSFW, @'+username+'?\n' +
                          clarifai_score+deepai_score+sightengine_score, in_reply_to_status_id=status_id)


class BotStreamer(tweepy.StreamListener):
    # Called when a new status arrives which is passed down from the on_data method of the StreamListener
    def on_status(self, status):
        username = status.user.screen_name
        status_id = status.id
        if 'media' in status.entities:
            for image in status.entities['media']:
                tweet_image_ratings(image['media_url'], username, status_id)
                
auth=tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api=tweepy.API(auth)  # create an API object

# Construct the Stream instance
myStreamListener=BotStreamer()
stream=tweepy.Stream(auth, myStreamListener)
stream.filter(track=['@IsItNSFW'])