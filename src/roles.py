import random


def compute_kpis(frames, player_id):
	pos_x = []
	pos_y = []
	minionsKilled = 0
	max_iter = 12
	if len(frames) < 12:
		max_iter = len(frames)
	for i in range(3, max_iter):
		#print(len(frames[i]['participantFrames']))
		if i > len(frames[i]['participantFrames']):
			break;
		for ct in range(0, len(frames[i]['participantFrames'])):
			participantFrames = frames[i]['participantFrames']
			for parcipitant in range(1, 11):
				# print(participantFrames[str(parcipitant)]['position']['x'])
				if 'position' in participantFrames[str(parcipitant)] and int(
					participantFrames[str(parcipitant)]['participantId']) == int(player_id):
					pos_x.append(participantFrames[str(parcipitant)]['position']['x'])
					pos_y.append(participantFrames[str(parcipitant)]['position']['y'])
					minionsKilled = participantFrames[str(parcipitant)]['minionsKilled']
	return pos_x, pos_y, minionsKilled


def make_teams(frames):
	teams_100 = []
	teams_200 = []
	for ct in range(0, len(frames[0]['participantFrames'])):
		participantFrames = frames[0]['participantFrames']
		for parcipitant in range(1, 11):
			# print(participantFrames[str(parcipitant)]['position']['x'])
			if str(parcipitant) not in participantFrames:
				print("NOT IN THE TEAM", parcipitant)
				exit()
			if participantFrames[str(parcipitant)]['position']['x'] > 10000 and \
				participantFrames[str(parcipitant)]['position']['y'] > 10000 and participantFrames[str(parcipitant)][
				'participantId'] not in teams_100:
				teams_100.append(participantFrames[str(parcipitant)]['participantId'])
			elif participantFrames[str(parcipitant)]['participantId'] not in teams_200 and \
				participantFrames[str(parcipitant)]['participantId'] not in teams_100:
				print(participantFrames[str(parcipitant)]['position']['x'])
				teams_200.append(participantFrames[str(parcipitant)]['participantId'])
	return teams_100, teams_200


def define_top(frames, player_id):
	pos_x, pos_y, minionsKilled = compute_kpis(frames, player_id)
	if len(pos_x) == 0:
		return False
	mean_x = sum(pos_x) / len(pos_x)
	mean_y = sum(pos_y) / len(pos_y)
	#print("TOP", mean_x, mean_y)
	if mean_y > 9000:
		return True
	return False


def missing_top(frames, players):
	best_pos = 0
	toplaner = ''
	for player_id in players:
		pos_x, pos_y, minionsKilled = compute_kpis(frames, player_id)
		mean_y = sum(pos_y) / len(pos_y)
		if mean_y > best_pos:
			toplaner = player_id
	return toplaner


def sup_or_adc(frames, players):
	minionsKilled = 0
	adc = ''
	for player_id in players:
		pos_x, pos_y, tmp_minionsKilled = compute_kpis(frames, player_id)
		if tmp_minionsKilled > minionsKilled:
			adc = player_id
	return adc


def define_mid(frames, player_id):
	pos_x, pos_y, minionsKilled = compute_kpis(frames, player_id)
	if len(pos_x) == 0:
		return False
	mean_x = sum(pos_x) / len(pos_x)
	mean_y = sum(pos_y) / len(pos_y)
	# print("MID X Y", mean_x, mean_y, minionsKilled)
	if mean_y < 10000 and mean_y > 4000 and mean_x > 4000 and mean_x < 10000 and minionsKilled > 30:
		return True
	return False


def define_adc(frames, player_id):
	pos_x, pos_y, minionsKilled = compute_kpis(frames, player_id)
	if len(pos_x) == 0:
		return False
	mean_x = sum(pos_x) / len(pos_x)
	mean_y = sum(pos_y) / len(pos_y)
	#print("ADC player_id X Y MINIONS", player_id, mean_x, mean_y, minionsKilled)
	if mean_y < 8000 and minionsKilled > 30:
		return True
	return False


def random_roles(roles, players, player_roles):
	if len(players) != len(roles):
		#print('FF', players, roles)
		exit()
	for i in range(0, len(roles)):
		if len(players) == 1:
			playerID = players[0]
			#print(" RANDOM : The participant ans his role", playerID, roles[0])
			players.remove(playerID)
			player_roles[str(playerID)] = roles[0]
		else:
			#print("RANDOM : ", len(players) - 1)
			playerID = players[random.randint(0, len(players) - 1)]
			#print(" RANDOM : The participant ans his role", playerID, roles[i])
			players.remove(playerID)
			player_roles[str(playerID)] = roles[0]
	return player_roles
