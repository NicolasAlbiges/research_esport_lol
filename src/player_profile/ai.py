import pandas as pd
import ast
import statistics
import matplotlib.pyplot as plt
from scipy.stats import norm
import numpy as np
import seaborn as sb

class Ai():
	def __init__(self):
		self.players = pd.read_csv("players.csv")
		self.matches = pd.read_csv("matches_v4.csv")
		self.bad_matches = []
		self.tmp_clean_dataset()
		self.timeline = pd.read_csv("matches_timeline_v4.csv")
		self.all_totalDamageTaken = []
		self.all_longestTimeSpentLiving = []
		self.all_visionScore = []
		self.all_kpa = []
		self.all_gameDuration = []
		self.all_objectivePlayerScore = []
		self.all_combatPlayerScore = []
		self.all_teamObjective = []
		self.players_kpa = {}
		self.player_play_styles = {}
		self.timeline_kpa()
		self.create_dataset()
		self.assigned_play_style_player()

	def define_mean_stats(self, participants_stats, participantIdentities, gameDuration, matchId):
		for participants in participants_stats:
			participantId = participants["participantId"]
			teamId = participants["teamId"]
			summonerId = self.find_summonerId(participantId, participantIdentities)
			self.all_totalDamageTaken.append(participants['stats']["totalDamageTaken"])
			self.all_longestTimeSpentLiving.append(participants['stats']["longestTimeSpentLiving"])
			self.all_visionScore.append(participants['stats']["visionScore"])
			self.all_kpa.append(self.players_kpa[str(matchId)][str(teamId)][str(participantId)])
			self.all_gameDuration.append(gameDuration)
			if summonerId not in self.player_play_styles:
				self.player_play_styles[summonerId] = {
					"totalDamageTaken": [participants['stats']["totalDamageTaken"]],
					"longestTimeSpentLiving": [participants['stats']["longestTimeSpentLiving"]],
					"visionScore": [participants['stats']["visionScore"]],
					"gameDuration": [gameDuration],
					"kpa": [self.players_kpa[str(matchId)][str(teamId)][str(participantId)]]
				}
			else:
				self.player_play_styles[summonerId]["totalDamageTaken"].append(participants['stats']["totalDamageTaken"])
				self.player_play_styles[summonerId]["longestTimeSpentLiving"].append(participants['stats']["longestTimeSpentLiving"])
				self.player_play_styles[summonerId]["visionScore"].append(participants['stats']["visionScore"])
				self.player_play_styles[summonerId]["gameDuration"].append(gameDuration)
				self.player_play_styles[summonerId]["kpa"].append(self.players_kpa[str(matchId)][str(teamId)][str(participantId)])
		return

	def timeline_kpa(self):
		for i in range(0, len(self.timeline['metadata'])):
			if self.timeline['match_id'][i] not in self.bad_matches:
				teams_100, teams_200 = self.init_timeline(i)
				self.players_kpa[str(self.timeline['match_id'][i])] = {"100": teams_100, "200": teams_200}

	def make_kpa(self, team, creator, assist):
		team[str(creator)] += 1
		for player_id in assist:
			team[str(player_id)] += 1
		return team

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

	def init_timeline(self, frame_ct):
		team_kpa_100 = {
			"0": 0,
			"1": 0,
			"2": 0,
			"3": 0,
			"4": 0,
			"5": 0,
			"6": 0,
			"7": 0,
			"8": 0,
			"9": 0,
			"10": 0
		}
		team_kpa_200 = {
			"0": 0,
			"1": 0,
			"2": 0,
			"3": 0,
			"4": 0,
			"5": 0,
			"6": 0,
			"7": 0,
			"8": 0,
			"9": 0,
			"10": 0
		}
		#TODO Game 10 Aram ?
		frames = ast.literal_eval(self.timeline['metadata'][frame_ct])
		frames = frames['frames']
		team_100_kills = 0
		team_200_kills = 0
		teams_100, teams_200 = self.make_teams(frames)
		for i in range(0, len(frames)):
			for ct in range(0, len(frames[i]['events'])):
				event = frames[i]['events'][ct]
				if event['type'] == 'CHAMPION_KILL' or event['type'] == 'BUILDING_KILL':
					if event['killerId'] in teams_100:
						team_kpa_100 = self.make_kpa(team_kpa_100, event["killerId"], event["assistingParticipantIds"])
						team_100_kills += 1
					else:
						team_kpa_200 = self.make_kpa(team_kpa_200, event["killerId"], event["assistingParticipantIds"])
						team_200_kills += 1
		for player_100 in team_kpa_100:
			if team_100_kills != 0:
				team_kpa_100[player_100] = team_kpa_100[player_100] / team_100_kills
		for player_200 in team_kpa_200:
			if team_200_kills != 0:
				team_kpa_200[player_200] = team_kpa_200[player_200] / team_200_kills
		return team_kpa_100, team_kpa_200

	def tmp_clean_dataset(self):
		for i in range(0, len(self.matches.index)):
			if self.matches['gameMode'][i] != "CLASSIC":
				self.bad_matches.append(self.matches['gameId'][i])
		self.bad_matches.append(5269853477)
		self.bad_matches.append(5263714859)
		self.bad_matches.append(5069066283)

	def get_probabilities(self, data, player_data, min):
		mean = statistics.mean(data)
		std = np.std(data)
		pdf = norm.pdf(data, loc=mean, scale=std)

		if min is True:
			proba = norm(loc=mean, scale=std).cdf(player_data)
		else:
			proba = 1 - norm(loc=mean, scale=std).cdf(player_data)

		my_data = pd.Series(data)
		my_data.plot.hist()
		plt.show()

		sb.set_style('whitegrid')
		sb.lineplot(data, pdf, color='black')
		plt.xlabel('kpa')
		plt.ylabel('Probability Density')
		plt.show()


		#print("PROBAS", player_data, proba)
		return proba

	def get_aggressive_player(self, player_id):
		sum_proba = (self.get_probabilities(self.all_totalDamageTaken, statistics.mean(self.player_play_styles[player_id]["totalDamageTaken"]), False) + \
		self.get_probabilities(self.all_longestTimeSpentLiving, statistics.mean(self.player_play_styles[player_id]["longestTimeSpentLiving"]), True)) / 2
		'''

		print("SATS : ", statistics.mean(self.player_play_styles[player_id]["totalDamageTaken"]), statistics.median(self.all_totalDamageTaken),
			statistics.mean(self.player_play_styles[player_id]["longestTimeSpentLiving"]), statistics.median(
			self.all_longestTimeSpentLiving), sum_proba)
					'''
		return sum_proba
		if sum_proba > 0.50:
			return True
		else:
			return False
		if statistics.mean(self.player_play_styles[player_id]["totalDamageTaken"]) > statistics.median(self.all_totalDamageTaken) and \
			statistics.mean(self.player_play_styles[player_id]["longestTimeSpentLiving"]) < statistics.median(
			self.all_longestTimeSpentLiving):
			return True
		return False

	def get_teamplayer_player(self, player_id):
		sum_proba = self.get_probabilities(self.all_visionScore, statistics.mean(self.player_play_styles[player_id]["visionScore"]),False)
		return sum_proba
		if sum_proba > 0.50:
			return True
		else:
			return False
		if statistics.mean(self.player_play_styles[player_id]["visionScore"]) >= statistics.median(self.all_visionScore):
			return True
		return False

	def get_leader_player(self, player_id):
		sum_proba = (self.get_probabilities(self.all_kpa,
		                                    statistics.mean(self.player_play_styles[player_id]["kpa"]),
		                                    False) + \
		             self.get_probabilities(self.all_visionScore, statistics.mean(
			             self.player_play_styles[player_id]["visionScore"]), False)) / 2
		return sum_proba
		if sum_proba > 0.50:
			return True
		else:
			return False
		if statistics.mean(self.player_play_styles[player_id]["kpa"]) > statistics.median(self.all_kpa) and \
			statistics.mean(self.player_play_styles[player_id]["visionScore"]) >= statistics.median(
			self.all_visionScore):
			return True
		return False

	def get_resilient_player(self, player_id):
		sum_proba = self.get_probabilities(self.all_gameDuration,
		                                   statistics.mean(self.player_play_styles[player_id]["gameDuration"]), False)
		return sum_proba
		if sum_proba > 0.50:
			return True
		else:
			return False
		if statistics.mean(self.player_play_styles[player_id]["gameDuration"]) >= statistics.median(self.all_gameDuration):
			return True
		return False

	def make_autopct(self, values):
		def my_autopct(pct):
			total = sum(values)
			val = int(round(pct * total / 100.0))
			return '{p:.2f}%  ({v:d})'.format(p=pct, v=val)
		return my_autopct

	def make_plot(self, labels, sizes):
		fig1, ax1 = plt.subplots()
		ax1.pie(sizes, labels=labels, autopct=self.make_autopct(sizes), shadow=True, startangle=90)
		ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
		plt.show()

	def debug_distribution(self, player_play_styles):
		aggressive = 0
		teamplayer = 0
		leader = 0
		resilient = 0
		for player in player_play_styles:
			aggressive += int(player_play_styles[player]["aggressive"])
			teamplayer += int(player_play_styles[player]["teamplayer"])
			leader += int(player_play_styles[player]["leader"])
			resilient += int(player_play_styles[player]["resilient"])

		self.make_plot(['Aggressive', 'Passive'], [aggressive, len(player_play_styles) - aggressive])
		self.make_plot(['Teamplayer', 'Lonely player'], [teamplayer, len(player_play_styles) - teamplayer])
		self.make_plot(['Leader', 'Follower'], [leader, len(player_play_styles) - leader])
		self.make_plot(['Determined', 'Yielding'], [resilient, len(player_play_styles) - resilient])

		print("Show stats about the distribution for playstyle, plots ?")

	def find_summonerId(self, participantId, participantIdentities):
		summonerId = ""
		for participant in participantIdentities:
			if participant["participantId"] == participantId and 'player' in participant:
				summonerId = participant["player"]["summonerId"]
				return summonerId
		return summonerId

	def create_dataset(self):
		for i in range(0, len(self.matches.index)):
			participantIdentities = ast.literal_eval(self.matches['participantIdentities'][i])
			participants_stats = ast.literal_eval(self.matches['participants'][i])
			gameDuration = self.matches['gameDuration'][i]
			if 'player' in participantIdentities[0] and self.matches['gameId'][i] not in self.bad_matches:
				self.define_mean_stats(participants_stats, participantIdentities, gameDuration, self.matches['gameId'][i])

	def assigned_play_style_player(self):
		player_play_styles = {}
		print("all_kpa")

		self.get_probabilities(self.all_kpa, 1, False)

		print("all_gameDuration")
		self.get_probabilities(self.all_gameDuration, 1, False)
		print("all_objectivePlayerScore")
		self.get_probabilities(self.all_objectivePlayerScore, 1, False)
		print("all_combatPlayerScore")
		self.get_probabilities(self.all_combatPlayerScore, 1, False)
		print("all_teamObjective")
		self.get_probabilities(self.all_teamObjective, 1, False)
		exit()

		for summonerId in self.player_play_styles:
				player_play_styles[summonerId] = {
					"aggressive": self.get_aggressive_player(summonerId),
					"teamplayer": self.get_teamplayer_player(summonerId),
					"leader": self.get_leader_player(summonerId),
					"resilient": self.get_resilient_player(summonerId)
				}


		self.debug_distribution(player_play_styles)
		df_player_play_styles = pd.DataFrame(player_play_styles)
		#df_player_play_styles.to_csv("player_playstyle_proba.csv")

if __name__ == "__main__":
    # Creating the distribution
    data = np.arange(1, 10, 0.01)
    mean = statistics.mean(data)
    std = np.std(data)

    pdf = norm.pdf(data, loc=5.3, scale=1)

    prob_1 = norm(loc=5.3, scale=1).cdf(10)
    print(prob_1)

    cdf_upper_limit = norm(loc=5.3, scale=1).cdf(6.5)
    cdf_lower_limit = norm(loc=5.3, scale=1).cdf(6.4)

    prob_2 = cdf_upper_limit - cdf_lower_limit
    print(prob_2)

    cdf_value = norm(loc=5.3, scale=1).cdf(6.5)
    prob_3 = 1 - cdf_value
    print(prob_3)


    Ai = Ai()
