import pandas as pd
import roles as roles_lib
import requests
import time
import ast
import matplotlib.pyplot as plt
import numpy as np
from copy import copy
import random


class Ai():
	def __init__(self):
		self._tmp_game_played_by_player = []
		self.ct = 0
		self.ct_all = 0
		self.players = pd.read_csv("players.csv")
		self.matches = pd.read_csv("matches_v4.csv")
		self.players_playstyle = pd.read_csv("player_playstyle_proba.csv")
		self.bad_matches = []
		self.tmp_clean_dataset()
		self.timeline = pd.read_csv("matches_timeline_v4.csv")
		self.players_roles = {}
		self.tmp_start_all_frames()
		self.roles = ["MIDDLE", "TOP", "JUNGLE", "ADC", "SUPPORT"]
		self.players_stats_columns = ['summonerId', 'avr_goldEarned', 'avr_kill',
		                              'avr_death', 'avr_assists', 'avr_trueDamageDealtToChampions',
		                              'avr_damageDealtToTurrets', 'avr_goldSpent',
		                              'avr_visionScore', 'avr_physicalDamageDealt', 'avr_totalHeal', 'avr_champLevel',
		                              "avr_magicDamageDealtToChampions", "avr_wardsPlaced", 'avr_goldSpent']
		self.player_playstyle_columns = ["aggressive", "teamplayer", "leader", "resilient"]
		#self.players_stats = pd.DataFrame(columns=[self.players_stats_columns])
		self.players_stats = {}
		self.compute_stats()
		self.columns_in_game, self.columns_hybrid, self.columns_player_playstyle = self.create_columns()
		self.data_in_game = dict.fromkeys(self.columns_in_game)
		self.data_player_playstyle = dict.fromkeys(self.columns_player_playstyle)
		self.data_hybrid = dict.fromkeys(self.columns_hybrid)
		self.dataset_in_game = pd.DataFrame(columns=self.columns_in_game)
		self.dataset_hybrid = pd.DataFrame(columns=self.columns_hybrid)
		self.dataset_player_playstyle = pd.DataFrame(columns=self.columns_player_playstyle)
		self.create_dataset()

	def tmp_clean_dataset(self):
		for i in range(0, len(self.matches.index)):
			if self.matches['gameMode'][i] != "CLASSIC":
				self.bad_matches.append(self.matches['gameId'][i])
		self.bad_matches.append(5269853477)
		self.bad_matches.append(5263714859)
		self.bad_matches.append(5069066283)

	def tmp_start_all_frames(self):
		for i in range(0, len(self.timeline['metadata'])):
			if self.timeline['match_id'][i] not in self.bad_matches:
				teams_100, teams_200 = self.init_timeline(i)
				self.players_roles[str(self.timeline['match_id'][i])] = {"100": teams_100, "200": teams_200}

	def tmp_graph_colors(self, i):
		if i > 15:
			return 'r'
		elif i >= 5:
			return 'm'
		else:
			return 'y'

	def make_teams(self, frames):
		teams_100 = []
		teams_200 = []
		for ct in range(0, len(frames[0]['participantFrames'])):
			participantFrames = frames[0]['participantFrames']
			for parcipitant in range(1, 11):
				#print(participantFrames[str(parcipitant)]['position']['x'])
				if str(parcipitant) not in participantFrames:
					print("NOT IN THE TEAM", parcipitant)
					exit()
				if participantFrames[str(parcipitant)]['position']['x'] > 10000 and participantFrames[str(parcipitant)]['position']['y'] > 10000 and participantFrames[str(parcipitant)]['participantId'] not in teams_200:
					teams_200.append(participantFrames[str(parcipitant)]['participantId'])
				elif participantFrames[str(parcipitant)]['participantId'] not in teams_200 and participantFrames[str(parcipitant)]['participantId'] not in teams_100:
					teams_100.append(participantFrames[str(parcipitant)]['participantId'])
		return teams_100, teams_200

	def define_roles(self, frames, teams, jglMinionsKills, ct_frames):
		player_roles = {}
		roles = ["JUNGLE", "MIDDLE", "TOP", "ADC", "SUPPORT"]
		tmp_roles = ["MIDDLE", "TOP", "ADC", "SUPPORT"]
		tmp_min_jglMinionsKills = 0
		playerID = None
		for player_id in teams:
			#print("JUNGLEMINIION / ID :", jglMinionsKills[str(player_id)], player_id)
			if jglMinionsKills[str(player_id)] > tmp_min_jglMinionsKills:
				playerID = player_id
				tmp_min_jglMinionsKills = jglMinionsKills[str(player_id)]
		#print("The JUNGLE for this player ", playerID)
		player_roles[str(playerID)] = "JUNGLE"
		teams.remove(playerID)
		playerID = None
		for role in roles:
			playerID = None
			for player_id in teams:
				if role == "TOP" and roles_lib.define_top(frames, player_id) == True and role in tmp_roles:
					playerID = player_id
					teams.remove(playerID)
					#print(" TOP The participant ans his role", playerID, role)
					tmp_roles.remove(role)
					player_roles[str(player_id)] = role
				if role == "MIDDLE" and roles_lib.define_mid(frames, player_id) == True and role in tmp_roles:
					playerID = player_id
					teams.remove(playerID)
					#print(" MIDDLE The participant ans his role", playerID, role)
					tmp_roles.remove(role)
					player_roles[str(player_id)] = role
				if role == "ADC" and roles_lib.define_adc(frames, player_id) == True and role in tmp_roles:
					playerID = player_id
					teams.remove(playerID)
					#print(" ADC The participant ans his role", playerID, role)
					tmp_roles.remove(role)
					player_roles[str(player_id)] = role
			#print("\n")
			if role == 'TOP' and role in tmp_roles:
				tmp_roles.remove(role)
				teams.remove(roles_lib.missing_top(frames, teams))
				player_roles[str(player_id)] = role
		if len(teams) == 1 and "SUPPORT" in tmp_roles:
			#print("The Support for this player ", teams[0])
			teams.remove(teams[0])
			tmp_roles.remove("SUPPORT")
			player_roles[str(player_id)] = role
		if len(teams) == 2 and "SUPPORT" in tmp_roles:
			tmp_roles.pop(0)
			player_id = roles_lib.sup_or_adc(frames, teams)
			player_roles[str(player_id)] = "ADC"
			player_roles[str(teams[0])] = "SUPPORT"
			teams.remove(player_id)
			teams.remove(teams[0])
			tmp_roles.remove("SUPPORT")
		if len(teams) != 0:
			print("KATA OOPS Something went wrong and FRAMES", teams, tmp_roles, ct_frames)
			#exit()
		player_roles = roles_lib.random_roles(tmp_roles, teams, player_roles)
		return player_roles

	def init_timeline(self, frame_ct):
		pos_x = {
			"1": [],
			"2": [],
			"3": [],
			"4": [],
			"5": [],
			"6": [],
			"7": [],
			"8": [],
			"9": [],
			"10": []
		}
		pos_y = {
			"1": [],
			"2": [],
			"3": [],
			"4": [],
			"5": [],
			"6": [],
			"7": [],
			"8": [],
			"9": [],
			"10": []
		}
		jglMinionsKills = {
			"1": [],
			"2": [],
			"3": [],
			"4": [],
			"5": [],
			"6": [],
			"7": [],
			"8": [],
			"9": [],
			"10": []
		}
		colors = []
		#TODO Game 10 Aram ?
		frames = ast.literal_eval(self.timeline['metadata'][frame_ct])
		frames = frames['frames']
		#print("FRAME : ", frame_ct)
		teams_100, teams_200 = self.make_teams(frames)
		#print("\nTEAMS", teams_100, teams_200)
		for i in range(0, len(frames)):
			for ct in range(0, len(frames[i]['participantFrames'])):
				participantFrames = frames[i]['participantFrames']
				for parcipitant in range(1, 11):
					if "position" in participantFrames[str(parcipitant)]:
						pos_x[str(participantFrames[str(parcipitant)]['participantId'])].append(participantFrames[str(parcipitant)]['position']['x'])
						pos_y[str(participantFrames[str(parcipitant)]['participantId'])].append(participantFrames[str(parcipitant)]['position']['y'])
						jglMinionsKills[str(participantFrames[str(parcipitant)]['participantId'])] = int(participantFrames[str(parcipitant)]['jungleMinionsKilled'])
						if participantFrames[str(parcipitant)]['participantId'] == 7:
							colors.append(self.tmp_graph_colors(i))
			for ct in range(0, len(frames[i]['events'])):
				event = frames[i]['events'][ct]
		means_x = []
		means_y = []
		for parcipitant in range(1, 11):
			pos_x[str(parcipitant)]
			mean_x = sum(pos_x[str(parcipitant)]) / len(pos_x[str(parcipitant)])
			means_x.append(mean_x)
			pos_y[str(parcipitant)]
			mean_y = sum(pos_y[str(parcipitant)]) / len(pos_y[str(parcipitant)])
			means_y.append(mean_x)
			#print("Mean of the value, x and y for player", mean_x, mean_y, parcipitant)
		#print("\nTEAMS", teams_100, teams_200)
		teams_100 = self.define_roles(frames, teams_100, jglMinionsKills, frame_ct)
		#print("\n\nTEAM 2\n\n")
		teams_200 = self.define_roles(frames, teams_200, jglMinionsKills, frame_ct)
		#plt.scatter(pos_x["3"], pos_y["3"], c=colors)
		#plt.show()
		return teams_100, teams_200

	def create_columns(self):
		columns_in_game = []
		columns_player_playstyle = []
		columns_hybrid = []
		team = '100_'
		role_ct = 0
		for i in range(1, 11):
			if i == 6:
				team = '200_'
			if i == 6:
				role_ct = 0
			role = self.roles[role_ct]
			for ct in range(1, len(self.players_stats_columns)):
				columns_in_game.append(str(team + role + "_" + self.players_stats_columns[ct]))
				columns_hybrid.append(str(team + role + "_" + self.players_stats_columns[ct]))
			for ct in range(0, len(self.player_playstyle_columns)):
				columns_hybrid.append(str(team + role + "_" + self.player_playstyle_columns[ct]))
				columns_player_playstyle.append(str(team + role + "_" + self.player_playstyle_columns[ct]))
			role_ct = role_ct + 1
		columns_in_game.append('win')
		columns_player_playstyle.append('win')
		columns_hybrid.append('win')
		return columns_in_game, columns_hybrid, columns_player_playstyle

	def define_role_riot(self, participants_timeline):
		role = participants_timeline['role']
		lane_role = participants_timeline['lane']
		print("ROLES ", role, lane_role)
		if lane_role == "BOTTOM" and role == "DUO_SUPPORT" or lane_role == "NONE" and role == "DUO_SUPPORT":
			return "SUPPORT"
		if lane_role == "BOTTOM" and role == "DUO_CARRY" or lane_role == "NONE" and role == "DUO":
			return "ADC"
		if role == "SOLO" and lane_role == "JUNGLE" or role == "NONE" and lane_role == "JUNGLE":
			return "JUNGLE"
		if role == "SOLO" and lane_role == "TOP":
			return "TOP"
		if role == "SOLO" and lane_role == "MIDDLE":
			return "MIDDLE"
		if lane_role == "NONE" or role == "NONE" or lane_role == "BOT":
			print(role, lane_role)
			exit()
		return lane_role

	def debug_roles_riot(self, teamId, participants_stats):
		tmp_role = self.roles
		for i in range(0, 10):
			if str(teamId) == str(participants_stats[i]["teamId"]):
				role = self.define_role_riot(participants_stats[i]["timeline"])
				if role in tmp_role:
					tmp_role.remove(role)
		if len(tmp_role) != 0:
			print("\nRole restants : ", tmp_role)
			exit()

	def get_stats_player(self, participantIdentities, participants_stats, matchId):
		#self.debug_roles_riot(100, participants_stats)
		#self.debug_roles_riot(200, participants_stats)
		for i in range(0, 10):
			#TODO Check participantId
			if 'player' in participantIdentities[i]:
				summoner_id = participantIdentities[i]['player']['summonerId']
				participant_id = participantIdentities[i]['participantId']
				teamId = str(participants_stats[i]["teamId"])
				#participants_stats[i]['stats']['role'] = self.define_role_riot(participants_stats[i]["timeline"])
				player_role = self.players_roles[str(matchId)][str(teamId)][str(participant_id)]
				#participants_stats[i]['stats']['role'] = self.players_roles[str(matchId)][str(teamId)][str(participant_id)]
				participants_stats[i]['stats']['role'] = player_role
				#print(participants_stats[i]['stats'])
				#TODO WArning voir le DF
				if summoner_id in self.players_stats:
					self._tmp_game_played_by_player.append(1)
					self.players_stats[summoner_id][player_role] = self.TODO_ADD_STATS_PLAYER(self.players_stats[summoner_id][player_role], player_role, participants_stats[i]['stats'])
				else:
					data = {
						'summonerId': summoner_id,
						'MIDDLE': self.TODO_ADD_STATS_PLAYER({}, 'MIDDLE', participants_stats[i]['stats']),
						'TOP': self.TODO_ADD_STATS_PLAYER({}, 'TOP', participants_stats[i]['stats']),
						'JUNGLE': self.TODO_ADD_STATS_PLAYER({}, 'JUNGLE', participants_stats[i]['stats']),
						'ADC': self.TODO_ADD_STATS_PLAYER({}, 'ADC', participants_stats[i]['stats']),
						'SUPPORT': self.TODO_ADD_STATS_PLAYER({}, 'SUPPORT', participants_stats[i]['stats']),
						'NONE': self.TODO_ADD_STATS_PLAYER({}, 'NONE', participants_stats[i]['stats'])
					}
					self.players_stats[summoner_id] = data
		return participants_stats

	def TODO_ADD_STATS_PLAYER(self, data, role, stats):
		if stats['role'] != role:
			return data
		#TODO What happens when its empty ?
		if 'goldEarned' not in data:
			data = {
					'avr_goldEarned': [stats['goldEarned']],
					'avr_kill': [stats['kills']],
					'avr_death': [stats['deaths']],
					'avr_assists': [stats['assists']],
					'avr_trueDamageDealtToChampions': [stats['trueDamageDealtToChampions']],
					'avr_visionScore': [stats['visionScore']],
					'avr_physicalDamageDealt': [stats['visionScore']],
					'avr_totalHeal': [stats['totalHeal']],
					'avr_champLevel': [stats['champLevel']],
					'avr_goldSpent': [stats['goldSpent']],
					'avr_damageDealtToTurrets': [stats['damageDealtToTurrets']],
					'avr_magicDamageDealtToChampions': [stats['magicDamageDealtToChampions']],
					'avr_wardsPlaced': [stats['wardsPlaced']],
					'avr_goldSpent': [stats['goldSpent']],
				}
		else:
			data['avr_goldEarned'].append(stats['goldEarned'])
			data['avr_kill'].append(stats['kills'])
			data['avr_death'].append(stats['deaths'])
			data['avr_assists'].append(stats['assists'])
			data['avr_trueDamageDealtToChampions'].append(stats['trueDamageDealtToChampions'])
			data['avr_visionScore'].append(stats['visionScore'])
			data['avr_physicalDamageDealt'].append(stats['physicalDamageDealt'])
			data['avr_totalHeal'].append(stats['totalHeal'])
			data['avr_champLevel'].append(stats['champLevel'])
			data['avr_goldSpent'].append(stats['goldSpent'])
			data['avr_damageDealtToTurrets'].append(stats['damageDealtToTurrets'])
			data['avr_magicDamageDealtToChampions'].append(stats['magicDamageDealtToChampions'])
			data['avr_wardsPlaced'].append(stats['wardsPlaced'])
			data['avr_goldSpent'].append(stats['goldSpent'])
		#print(data)
		return data

	def compute_rols_stats(self, data):
		if 'goldEarned' not in data or len(data['goldEarned']) == 0:
			return data
		data['avr_goldEarned'] = sum(data['avr_goldEarned']) / len(data['avr_goldEarned'])
		data['avr_kill'] = sum(data['avr_kill']) / len(data['avr_kill'])
		data['avr_death'] = sum(data['avr_death']) / len(data['avr_death'])
		data['avr_assists'] = sum(data['avr_assists']) / len(data['avr_assists'])
		data['avr_trueDamageDealtToChampions'] = sum(data['avr_trueDamageDealtToChampions']) / len(data['avr_trueDamageDealtToChampions'])
		data['avr_visionScore'] = sum(data['avr_visionScore']) / len(data['avr_visionScore'])
		data['avr_physicalDamageDealt'] = sum(data['avr_physicalDamageDealt']) / len(data['avr_physicalDamageDealt'])
		data['avr_totalHeal'] = sum(data['avr_totalHeal']) / len(data['avr_totalHeal'])
		data['avr_champLevel'] = sum(data['avr_champLevel']) / len(data['avr_champLevel'])
		data['avr_goldSpent'] = sum(data['avr_goldSpent']) / len(data['avr_goldSpent'])
		data['avr_damageDealtToTurrets'] = sum(data['avr_damageDealtToTurrets']) / len(data['avr_damageDealtToTurrets'])
		data['avr_magicDamageDealtToChampions'] = sum(data['avr_magicDamageDealtToChampions']) / len(data['avr_magicDamageDealtToChampions'])
		data['avr_wardsPlaced'] = sum(data['avr_wardsPlaced']) / len(data['avr_wardsPlaced'])
		data['avr_goldSpent'] = sum(data['avr_goldSpent']) / len(data['avr_goldSpent'])
		return data

	#TODO Add the handle of position roles and catgeorical data and boolean
	def compute_stats(self):
		for i in range(0, len(self.matches.index)):
			participantIdentities = ast.literal_eval(self.matches['participantIdentities'][i])
			participants_stats = ast.literal_eval(self.matches['participants'][i])
			if 'player' in participantIdentities[0] and self.matches['gameId'][i] not in self.bad_matches:
				self.matches['participants'][i] = str(self.get_stats_player(participantIdentities, participants_stats, self.matches['gameId'][i]))
		#TODO Faire la mean de toutes les valeurs pour chaque roles sur chaqe joueurs
		for player in self.players_stats:
			for role in self.players_stats[player]:
				if role != "summonerId":
					self.players_stats[player][role] = self.compute_rols_stats(self.players_stats[player][role])
		#self.players_stats.to_csv("player_stats.csv")

	def find_summonerId(self, participantId, participantIdentities):
		summonerId = ""
		for participant in participantIdentities:
			# TODO Verifier par le role et non l'id
			if participant["participantId"] == participantId and 'player' in participant:
				summonerId = participant["player"]["summonerId"]
				#print("\nPLAYER FOUND : ", summonerId)
				return summonerId
		#print("\nPLAYER NOT FOUND FOR THIS PARTICIPANTID  : ", participantId)
		return summonerId

	def create_stat_player(self, teamId, player_stats, player_playstyle, role):
		#TODO Add playerstylfe
		for ctb in range(1, len(self.players_stats_columns)):
			stat_name = teamId + "_" + role + "_" + self.players_stats_columns[ctb]
			#print(player_stats[role][self.players_stats_columns[ctb]])
			#data[stat_name] = player_stats[role][self.players_stats_columns[ctb]]
			self.data_in_game[stat_name] = player_stats[role][self.players_stats_columns[ctb]][0]
			self.data_hybrid[stat_name] = player_stats[role][self.players_stats_columns[ctb]][0]
		for ctb in range(0, len(self.player_playstyle_columns)):
			stat_name = teamId + "_" + role + "_" + self.player_playstyle_columns[ctb]
			#print(player_stats[role][self.players_stats_columns[ctb]])
			#data[stat_name] = player_playstyle[playstyle]
			self.data_hybrid[stat_name] = player_playstyle[ctb]
			self.data_player_playstyle[stat_name] = player_playstyle[ctb]
		return

	def create_subset_team(self, teamId, participants_stats, participantIdentities, role):
		for players_stats in participants_stats:
			#print("roLEs", participants_stats[players_stats]["stats"]['role'])
			player_role = players_stats["stats"]['role']
			if role == player_role and int(players_stats["teamId"]) == int(teamId):
				participantId = players_stats["participantId"]
				summonerId = self.find_summonerId(participantId, participantIdentities)
				player_stats = self.players_stats[summonerId]
				player_playstyle = self.players_playstyle[summonerId]
				return self.create_stat_player(teamId, player_stats, player_playstyle, player_role)
		print("NOT MATCHING ROLE ", role, teamId)
		return

	def create_stats_team(self, teamId, participants_stats, participantIdentities):
		#TODO What to do when missing roles ?
		#TODO Verify the teamID
		for i in range (0, 5):
			print(self.roles[i], teamId)
			self.create_subset_team(teamId, participants_stats, participantIdentities, self.roles[i])
		return

	def define_win(self, teams):
		if (teams[0]['teamId'] == 100 and teams[0]['win'] == "Win") or \
			(teams[0]['teamId'] == 200 and teams[0]['win'] == "Fail"):
			# win
			self.data_in_game['win'] = 1
			self.data_player_playstyle['win'] = 1
			self.data_hybrid['win'] = 1

		else:
			# lose
			self.data_in_game['win'] = 0
			self.data_player_playstyle['win'] = 0
			self.data_hybrid['win'] = 0

	def create_dataset(self):
		mean = sum(self._tmp_game_played_by_player) / len(self._tmp_game_played_by_player)
		print("The mean of game per players : \n", mean, max(self._tmp_game_played_by_player))
		for i in range(0, len(self.matches.index)):
			participantIdentities = ast.literal_eval(self.matches['participantIdentities'][i])
			participants_stats = ast.literal_eval(self.matches['participants'][i])
			if 'player' in participantIdentities[0] and self.matches['gameId'][i] not in self.bad_matches:
				teams = ast.literal_eval(self.matches['teams'][i])
				self.define_win(teams)
				#TODO Make two tams stats
				teamId = str(participants_stats[0]["teamId"])
				self.create_stats_team(teamId, participants_stats, participantIdentities)
				teamId = str(participants_stats[5]["teamId"])
				self.create_stats_team(teamId, participants_stats, participantIdentities)
				self.dataset_in_game = self.dataset_in_game.append(self.data_in_game, ignore_index=True)
				self.data_in_game = dict.fromkeys(self.columns_in_game)
				self.dataset_player_playstyle = self.dataset_player_playstyle.append(self.data_player_playstyle, ignore_index=True)
				self.data_player_playstyle = dict.fromkeys(self.columns_player_playstyle)
				self.dataset_hybrid = self.dataset_hybrid.append(self.data_hybrid, ignore_index=True)
				self.data_hybrid = dict.fromkeys(self.columns_hybrid)
		print(self.dataset_in_game)
		print("\n\n", self.dataset_player_playstyle)
		print("\n\n", self.dataset_hybrid)
		#self.dataset_in_game.to_csv("dataset_in_game.csv")
		self.dataset_player_playstyle.to_csv("dataset_player_playstyle_v2.csv")
		self.dataset_hybrid.to_csv("dataset_hybrid_v2.csv")


if __name__ == "__main__":
	ai = Ai()