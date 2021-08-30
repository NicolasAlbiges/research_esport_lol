import pandas as pd
import requests
import time
import ast


API_KEY = "RGAPI-d01cd747-a405-4009-a642-4289e7745752"


def merge_list(first_list, second_list):
	for element in first_list:
		if element not in second_list:
			second_list.append(element)
	return second_list


class Data:
	def __init__(self):
		self.ct = 0
		self.ct_all = 0

	def request_api(self, url, add):
		try:
			url = url + add + "api_key=" + API_KEY
			r = requests.get(url=url)
			r.raise_for_status()
			data = r.json()
			return data
		except requests.exceptions.HTTPError as e:  # This is the correct syntax
			print(e)
			return []

	def get_infos_of_user_by_summonerId(self, summonerId):
		url = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/" + summonerId
		data = self.request_api(url, "?")
		print(data)
		return data

	def get_all_players_id(self, ):
		url = "https://euw1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
		data = self.request_api(url, "?")
		print(data)
		return data

	def get_match_ids_from_uuid(self, uuid):
		all_matches = []
		for i in range(0, 19):
			if self.ct == 19:
				time.sleep(2)
				self.ct = 0
			if self.ct_all == 98:
				time.sleep(121)
				self.ct_all = 0
			url = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + uuid + "/ids?start=" + str(
				len(all_matches)) + "&count=99"
			matches = self.request_api(url, "&")
			if matches != []:
				all_matches = merge_list(matches, all_matches)
				print(matches)
			else:
				return all_matches
			self.ct_all = self.ct_all + 1
			self.ct = self.ct + 1
		return all_matches

	def get_matchs_infos(self, matchid):
		url = "https://euw1.api.riotgames.com/lol/match/v4/matches/" + matchid
		data = self.request_api(url, "?")
		print(data)
		return data

	def get_matchs_timeline(self, matchid):
		url = "https://euw1.api.riotgames.com/lol/match/v4/timelines/by-match/" + matchid
		data = self.request_api(url, "?")
		return data

	def create_dataset_players(self):
		players = self.get_all_players_id()
		for i in range(0, len(players["entries"])):
			if self.ct >= 19:
				time.sleep(2)
				self.ct = 0
			if self.ct_all >= 98:
				time.sleep(121)
				self.ct_all = 0
			print("PLAYER \n")
			print(players["entries"][i])
			print(players["entries"][i]["summonerId"])
			player_infos = self.get_infos_of_user_by_summonerId(players["entries"][i]["summonerId"])
			if player_infos == []:
				print("Problem from player")
				pass
			else:
				print("INFOS \n")
				print(player_infos)
				player_matches = self.get_match_ids_from_uuid(player_infos['puuid'])
				players["entries"][i]["player_matches"] = player_matches
				print(players["entries"][i])
			self.ct = self.ct + 1
			self.ct_all = self.ct_all + 1
		df = pd.DataFrame(players["entries"])
		df.to_csv("players.csv")

	def create_dataset_matches(self):
		df_players = pd.read_csv("players.csv")
		print(df_players)
		all_matches = []
		for matches in df_players["player_matches"]:
			matches = ast.literal_eval(matches)
			all_matches = merge_list(matches, all_matches)
		df_all_matches = pd.DataFrame(all_matches)
		print(df_all_matches[0].value_counts())
		all_matches_infos = []
		for match in matches:
			if self.ct >= 19:
				time.sleep(2)
				self.ct = 0
			if self.ct_all >= 98:
				time.sleep(121)
				self.ct_all = 0
			match_id = match.replace("EUW1_", "")
			match_info = self.get_matchs_infos(match_id)
			if match_info:
				all_matches_infos.append(match_info)
			self.ct = self.ct + 1
			self.ct_all = self.ct_all + 1
		df = pd.DataFrame(all_matches_infos)
		df.to_csv("matches_v4.csv")

	def create_dataset_matches_timeline(self):
		df_players = pd.read_csv("players.csv")
		print(df_players)
		all_matches = []
		for matches in df_players["player_matches"]:
			matches = ast.literal_eval(matches)
			all_matches = merge_list(matches, all_matches)
		df_all_matches = pd.DataFrame(all_matches)
		print(df_all_matches[0].value_counts())
		all_matches_infos = []
		for match in matches:
			if self.ct >= 19:
				time.sleep(2)
				self.ct = 0
			if self.ct_all >= 98:
				time.sleep(121)
				self.ct_all = 0
			match_id = match.replace("EUW1_", "")
			match_info = self.get_matchs_timeline(match_id)
			if match_info:
				all_matches_infos.append({"match_id": match_id,  "metadata": match_info})
			self.ct = self.ct + 1
			self.ct_all = self.ct_all + 1
		df = pd.DataFrame(all_matches_infos)
		df.to_csv("matches_timeline_v4.csv")


def temp_url():
	url = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/676YeM-9oo2Lz5lcb6ktX6lhC2Djppwbn2nBdgWOKrLVwFzuMui-1IN_3dM3fzh1obSelMqByvqlpQ/ids?start=0&count=20&api_key=RGAPI-a1a8a03b-52d6-4aea-b295-7f93cf894dcd"
	r = requests.get(url=url)
	data = r.json()
	print(data)


def temp_get_match_ids_from_uuid(uuid):
	all_matches = []
	for i in range(0, 19):
		if ct == 19:
			time.sleep(2)
			ct = 0
		if ct_all == 98:
			time.sleep(121)
			ct_all = 0
		url = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + uuid + "/ids?start=" + str(
			len(all_matches)) + "&count=99"
		matches = request_api(url, "&")
		if matches != []:
			all_matches = merge_list(matches, all_matches)
			print(matches)
		else:
			return all_matches
		ct_all = ct_all + 1
		ct = ct + 1
	return all_matches


if __name__ == "__main__":
	data = Data()
	#summonerId = "oDRymeQ5gp4T3L1UmVTyVeZHQkIAM4T1pNxpwcH3vCpSzR_m"
	#player_infos = get_infos_of_user_by_summonerId(summonerId)
	#all_matches = temp_get_match_ids_from_uuid(player_infos["puuid"])
	#print(len(all_matches))
	#get_infos_of_user_by_name("Kotei")
	#get_all_players_id()
	#data.create_dataset_players()
	#data.create_dataset_matches()
	data.create_dataset_matches_timeline()

