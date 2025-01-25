from functions import *

# Your Riot Games API key
api_key = 'RGAPI-00e1b621-616a-4696-bb6c-ec797c25fbe3' # Ensure this is correct and up-to-date

# Region (account-v1 endpoints don't require specific regional routing, using the common routing endpoint)
region = 'europe'  # This can be 'americas', 'asia', or 'europe' based on your account region
region2 = 'euw1'


riot = RiotAPI(api_key, region, region2)
challengers = riot.get_all_challengers()    
classement_décroissant_challengers = sorted(challengers['entries'], key=lambda x: x['leaguePoints'], reverse=True)
"""classer les challengers par league points"""
# for i, entry in enumerate(classement_décroissant_challengers):
#     print(f"Rank {i+1}: Summoner ID: {entry['summonerId']}, League Points: {entry['leaguePoints']}, Wins: {entry['wins']}, Losses: {entry['losses']}")
rank1=classement_décroissant_challengers[0]
print(f"Rank 1: Summoner ID: {rank1['summonerId']}, League Points: {rank1['leaguePoints']}, Wins: {rank1['wins']}, Losses: {rank1['losses']}")
puuid = riot.get_puuid_by_summoner_id(rank1['summonerId'])['puuid']
match_ids = riot.get_summoners_ranked_matches(puuid)
data=riot.get_summoners_general_stats(match_ids[0],rank1['summonerId'])