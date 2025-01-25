import requests

class RiotAPI:
    def __init__(self, api_key, region, region2):
        self.api_key = api_key
        self.region = region
        self.region2 = region2
        self.headers = {
            "X-Riot-Token": self.api_key
        }

    def _make_request(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.json().get('status', {}).get('message', 'Unknown error')}")
            return None
        
    def _get_general_match_infos_(self, match_id):
        url = f'https://{self.region}.api.riotgames.com/lol/match/v5/matches/{match_id}'
        return self._make_request(url)
    
    def __sort_by_position__(self, list_summoners_stats):
        role_priority = {
            'TOP': 1,
            'JUNGLE': 2,
            'MIDDLE': 3,
            'BOTTOM': 4,
            'UTILITY': 5
        }
        list_summoners_stats.sort(key=lambda x: role_priority.get(x[6], float('inf')))
        return list_summoners_stats

    def _give_winrate_(self, wins, losses):
        if wins + losses == 0:
            return "0%"  # Pour éviter la division par zéro
        winrate = (wins / (wins + losses)) * 100
        return f"{winrate:.2f}%"
    
    def _get_bans_(self, match_infos):
        teams = match_infos['info']['teams']
        bans = []
        for team in teams:
            # Accédez aux bans de chaque équipe
            bans.extend(team['bans'])
        return bans
    
    def get_runes_and_stat_perks_and_summoners(self, match_data):
        runes_per_player = []
        for participant in match_data['info']['participants']:
            summoner_name = participant['summonerName']
            runes = participant['perks']['styles']
            stat_perks = participant['perks']['statPerks'] #adaptative_force
            summonersId = participant['summoner1Id'], participant['summoner2Id']
            player_runes = {
                'summoner_name': summoner_name,
                'runes': [],
                'stat_perks': stat_perks,
                'summonersId': summonersId
            }
            for style in runes:
                for selection in style['selections']:
                    rune_id = selection['perk']
                    player_runes['runes'].append(rune_id)
            runes_per_player.append(player_runes)
        return runes_per_player

    def get_puuid_byname(self, game_name, tag_line):
        url = f'https://{self.region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}'
        return self._make_request(url)

    def get_puuid_by_summoner_id(self, Id):
        url = f'https://{self.region2}.api.riotgames.com/lol/summoner/v4/summoners/{Id}'
        return self._make_request(url)

    def id_summonerid(self, puuid):
        url = f'https://{self.region2}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}'
        return self._make_request(url)

    def get_summoners_ranked_matches(self, puuid):
        url = f'https://{self.region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&type=ranked&start=0&count=20'
        return self._make_request(url)

    def get_all_challengers(self):
        url = f'https://{self.region2}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5'
        return self._make_request(url)

    def get_summoner_infos(self, summonerId):
        url = f'https://{self.region2}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerId}'
        return self._make_request(url)
    
    def get_summoners_general_stats(self,match_id,rank1):
        list_summoners_stats = []
        match_infos = self._get_general_match_infos_(match_id)
        bans = self._get_bans_(match_infos)
        summoner_ids = [participant['summonerId'] for participant in match_infos['info']['participants']]
        for j,summoner_id in enumerate(summoner_ids):
            i=0
            summoner_infos = self.get_summoner_infos(summoner_id)
            wins = summoner_infos[i]
            while wins['queueType'] != "RANKED_SOLO_5x5":
                i+=1
                wins = summoner_infos[i]
            #tier, leaguePoints, wins, losses,palcement, nom
            
            list_summoners_stats.append([
                match_infos['info']['participants'][j]['riotIdGameName'],
                wins['tier'],
                #PLACEMENT MAIS FAUT ALLER SUR LEAGUE-V4 PLUS TARD
                wins['leaguePoints'],
                wins['wins'],
                wins['losses'],
                self._give_winrate_(wins['wins'], wins['losses']),
                #lane, champion, equipe, (dans quelle team il joue) PAS ENCORE FAIT
                match_infos['info']['participants'][j]['individualPosition'],
                match_infos['info']['participants'][j]['teamId'],
                match_infos['info']['participants'][j]['championName'],
                match_infos['info']['participants'][j]['summoner1Id'],
                match_infos['info']['participants'][j]['summoner2Id'],
                #rajouter les runes et stat_perks et summoners
                match_infos['info']['participants'][j]['perks']['styles'][0]['selections'][0]['perk'],
                match_infos['info']['participants'][j]['perks']['styles'][0]['selections'][1]['perk'],
                match_infos['info']['participants'][j]['perks']['styles'][0]['selections'][2]['perk'],
                match_infos['info']['participants'][j]['perks']['styles'][0]['selections'][3]['perk'],
                match_infos['info']['participants'][j]['perks']['styles'][1]['selections'][0]['perk'],
                match_infos['info']['participants'][j]['perks']['styles'][1]['selections'][1]['perk'],
                match_infos['info']['participants'][j]['perks']['statPerks']['offense'],
                match_infos['info']['participants'][j]['perks']['statPerks']['flex'],
                match_infos['info']['participants'][j]['perks']['statPerks']['defense']
                
            ])
            if match_infos['info']['participants'][j]['summonerName'] == "":
                list_summoners_stats[j].append(1)
            else:
                list_summoners_stats[j].append(0)
            if summoner_id == rank1:
                list_summoners_stats[j].append("gold")
            else:
                list_summoners_stats[j].append("black")
        self.__sort_by_position__(list_summoners_stats)
        return list_summoners_stats, bans
