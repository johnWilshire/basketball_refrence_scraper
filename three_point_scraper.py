#!/bin/usr/python


import requests
from bs4 import BeautifulSoup
import re
from game import Game
from player import Player
from players import Players
from event import Event


def main():
    pbp_url = 'http://www.basketball-reference.com/boxscores/pbp/201510270GSW.html'
    player_url = 'http://www.basketball-reference.com/players/c/curryst01.html'
    players = Players()
    urls = player_url_to_seasons(player_url)

    games = player_season_to_game_url(urls[0])
    for game in games:
        print pbp_url_to_game(pbp_url,players)
    return 0

#TODO given a player find pbp urls of all games

def player_url_to_seasons(url):
    urls = list()
    soup = extract_soup(url)
    links = soup.find_all('a')
    for link in links:
        if re.search('gamelog',link['href']):
            urls.append('http://www.basketball-reference.com' + link['href'])
    return list(set(urls))

def player_season_to_game_url(url):
    games = list()
    soup = extract_soup(url)
    links = soup.find_all('a')
    for link in links:
        if re.search('boxscores.*\.html',link['href']):
            games.append('http://www.basketball-reference.com'+link['href'])
    return list(set(games))

# takes a url for a games play by play and extracts information from it
def pbp_url_to_game(url,players):
    game_id = re.search('/pbp/(\d+[\w]{3})\.html',url)
    game_id = game_id.group(1)
    soup = extract_soup(url)
    # make game object for this game
    (visiting, home, date) = re.split(' at | Play-By-Play, ', soup.h1.text)
    game = Game(visiting=visiting, home= home, date=date,game_id=game_id)
    divs = soup.find_all('div', {"class": 'clear_both width100'})
    table = divs[0].find_all('table')[-1]
    quater = '0'
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        if 'id' in tr.attrs:
            quater = tr.attrs['id'][-1]
        if len(tds) == 6:
            time = tds[0].text
            if type(tds[5].string) == type(None):
                event_data = tds[5]
                score = tds[3].text.split('-')
                score_diff = str(int(score[1]) - int(score[0]))
                score = score[1]
                team = game.home
            else:
                team = game.visiting
                score = re.sub('\s','',tds[3].text)
                score = score.split('-')
                score_diff = str(int(score[0]) - int(score[1]))
                score = score[0]
                event_data = tds[1]
            # currently it only looks for point-score events
            match = re.search('[\d]-pt',event_data.text)
            if match:
                event_type = match.group()
                makes_shot = re.search('makes|misses',event_data.text).group() == 'makes'
                player_links = event_data.find_all('a')
                # find existing player or make new player
                player = players.getPlayer(player_links[0])
                event = Event(game, time, quater, team, player, event_type, makes_shot,score, score_diff)
                game.add_to_events(event)
                player.add_to_events(event)

                print event.to_str()


def extract_soup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    return soup


if __name__ == '__main__':
    main()