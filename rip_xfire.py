import os,sys,time,shutil
from datetime import datetime
from natsort import natsorted

games_list = "games.txt"
playtimes_db = "playtimes.txt"
refresh_interval = 5
make_backups = True

if not os.path.isfile(games_list):
	print(games_list,"not found")
	sys.exit(1)
else:
	games_db = []
	f = open(games_list,"r")
	lines = f.readlines()
	f.close()
	for line in lines: # add exe names to games_db
		games_db.append(line.split("=")[1].rstrip())

print("Tracking", len(games_db), "games.")
#print(games_db)

def get_running_exes(): # https://www.geeksforgeeks.org/python-get-list-of-running-processes/
	wmic_output = os.popen('wmic process get description, processid').read().strip()
	items = wmic_output.split("\n")
	exes = []
	for line in items:
		if ".exe" in line.strip():
			exe = line.split("   ")[0].rstrip()
			#print(exe)
			exes.append(exe)
	return exes

def update_playtimes(exe,added_playtime):
	secs = added_playtime.total_seconds()

	db_games = []
	db_playtimes = []

	if os.path.isfile(playtimes_db):

		if make_backups: # make backup
			if not os.path.isdir("./backups"): 
				os.makedirs("./backups")
			backup_path = "./backups/playtimes_db_" + time.strftime("%Y%m%d-%H%M%S") + ".txt"
			shutil.copy(playtimes_db, backup_path)

		f = open(playtimes_db,"r")
		lines = f.readlines()
		f.close()

		for line in lines:
			db_games.append(line.split("=")[0].rstrip())
			db_playtimes.append(line.split("=")[1].rstrip())

	if exe in db_games:
		index = db_games.index(exe)
		previous_playtime = float(db_playtimes[index])
		print("? previous playtime:",previous_playtime)
		print("+ adding",secs)
		new_playtime = previous_playtime + secs
		print("= new playtime:", new_playtime)
		db_playtimes[index] = new_playtime
	else:
		db_games.append(exe)
		db_playtimes.append(secs)

	# write db_games and db_playtimes to file
	f = open(playtimes_db,"w")
	for game in db_games:
		secs = db_playtimes[db_games.index(game)]
		f.write(game + "=" + str(secs) + "\n")
	f.close()
	print("updated",playtimes_db)

	return True

def make_stats_file():
	# read and associate pretty names
	pretty_names = []
	f = open(games_list,"r")
	lines = f.readlines()
	f.close()

	for line in lines:
		name = line.split("=")[0].rstrip()
		exe = line.split("=")[1].rstrip()
		pretty_names.append( {"exe": exe, "name": name} )

	# now read playtimes and match pretty names
	if os.path.isfile(playtimes_db):
		f = open(playtimes_db,"r")
		lines = f.readlines()
		f.close()

		db = []
		for line in lines:
			game_exe = line.split("=")[0].rstrip()
			name = game_exe # in case we dont find pretty name... shouldnt happen though
			for entry in pretty_names:
				if game_exe == entry["exe"]:
					name = entry["name"]
					break
			playtime = float(line.split("=")[1].rstrip())
			db.append( {"name": name, "seconds_played": playtime } )

		#print(db)

		# sort by most played (most seconds)
		d = natsorted(db, key = lambda i: i['seconds_played'])
		#print(d)

		# CSV stats
		stats_file = "Stats.csv"
		f = open(stats_file,"w")
		f.write("Game,Hours\n") # top row (column names)
		for game in reversed(d): # reverse to get most on top
			name = game['name']
			hours = round( game['seconds_played'] / 3600 )
			if hours < 1:
				hours = "<1"
			f.write(name + "," + str(hours) + "\n")
		f.close()
		print("updated",stats_file)

		# HTML stats
		stats_file = "Stats.html"
		f = open(stats_file,"w")
		f.write('<html><head><meta charset="utf8"></head><body>')
		for game in reversed(d): # reverse to get most on top
			name = game['name']
			hours = round( game['seconds_played'] / 3600 )
			if hours < 1:
				f.write("<li><b>" + name + "</b>: <1 hour</li>")
			elif hours == 1:
				f.write("<li><b>" + name + "</b>: 1 hour</li>")
			else:
				f.write("<li><b>" + name + "</b>: " + str(hours) + " hours</li>")
		f.write("</body></html>")
		f.close()
		print("updated",stats_file)

# main
games_running = []
games_started = []
print("OK, go play games. I'll keep track.")
while True:
	#print("loop")
	#print("games running:",games_running)
	#print("games started:",games_started)

	exes = get_running_exes()
	for game in games_db:
		if game in exes and game not in games_running:

			time_started = datetime.now()
			print("started playing",game,time_started)
			print()

			games_running.append(game)
			games_started.append(time_started)

		elif game in games_running and game not in exes:

			time_stopped = datetime.now()
			print("stopped playing",game,time_stopped)

			index = games_running.index(game)

			time_started = games_started[index]
			time_played = time_stopped - time_started
			print(game,"played for",time_played)

			games_running.pop(index)
			games_started.pop(index)

			if update_playtimes(game,time_played):
				make_stats_file()
				print()

	time.sleep(refresh_interval)