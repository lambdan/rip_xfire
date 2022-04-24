import os,sys,time,shutil
from datetime import datetime, timedelta
from natsort import natsorted

games_list = "games.txt"
playtimes_db = "playtimes.txt"
refresh_interval = 5
make_backups = True

print("Running in", os.getcwd())

if not os.path.isfile(games_list):
	print(games_list,"not found")
	sys.exit(1)
else:
	games_db = []
	names_db = []
	f = open(games_list,"r")
	lines = f.readlines()
	f.close()
	for line in lines: # add exe names to games_db
		for exe in line.split("=")[1].rstrip().split(","):
			games_db.append(exe)
			names_db.append(line.split("=")[0].rstrip())

print("Tracking " + str(len(lines)) + " games (" + str(len(games_db)) + " executables)")
#print(games_db)
#print(names_db)

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

def name_from_exe(exe):
	return names_db[games_db.index(exe)]

def secs_to_hhmmss(secs):
	# https://stackoverflow.com/a/1384465
	return str(timedelta(seconds=round(secs)))

def update_playtimes(game_name,added_playtime):
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

	if game_name in db_games:
		index = db_games.index(game_name)
		previous_playtime = float(db_playtimes[index])
		print("? previous playtime:", secs_to_hhmmss(previous_playtime))
		print("+ adding", secs_to_hhmmss(secs))
		new_playtime = int(previous_playtime + secs)
		print("= new playtime:", secs_to_hhmmss(new_playtime))
		db_playtimes[index] = new_playtime
	else:
		db_games.append(game_name)
		db_playtimes.append(secs)

	# write db_games and db_playtimes to file
	f = open(playtimes_db,"w")
	for game in sorted(db_games):
		secs = db_playtimes[db_games.index(game)]
		f.write(game + "=" + str(secs) + "\n")
	f.close()
	print("updated",playtimes_db)

	return True

def make_stats_file():
	if os.path.isfile(playtimes_db):
		f = open(playtimes_db,"r")
		lines = f.readlines()
		f.close()

		db = []
		for line in lines:
			name = line.split("=")[0].rstrip()
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
		total_played = 0
		f = open(stats_file,"w")
		f.write('<html><head><meta charset="utf8">')
		f.write('<style>.game-name {color: #f2bc02; } body {font-family: Tahoma; background-color:#061222; color:white;} td {padding:8px;} table,td {border:1px solid #0e4d75; border-collapse:collapse;}</style>')
		f.write('</head><body>')
		f.write('<p>Playtimes as of ' + str( time.strftime("%Y-%m-%d %H:%M:%S") ) + '</p>')
		f.write('<table>')
		# Write table
		for game in reversed(d): # reverse to get most on top
			name = game['name']
			total_played += game['seconds_played']
			hours = round( game['seconds_played'] / 3600 )
			f.write('<tr><td><div class="game-name">' + name + '</div></td>')
			f.write('<td><span title="' + secs_to_hhmmss(game['seconds_played']) + '">')
			if hours < 1:
				f.write("<1 hour")
			elif hours == 1:
				f.write("1 hour")
			else:
				f.write(str(hours) + " hours")
			f.write("</span></td>")
			f.write("</tr>")

		# Write total
		total_hours = round( total_played / 3600 )
		f.write("<tr><td><b>Total:</b></td>")
		f.write('<td><span title="' + secs_to_hhmmss(total_played) + '"><b>')
		if total_hours < 1:
			f.write("<1 hour")
		elif total_hours == 1:
			f.write("1 hour")
		else:
			f.write(str(total_hours) + " hours")
		f.write("</b></td></tr></table>")
		f.write("</body></html>")
		f.close()

		print("updated",stats_file)

# refresh stats if asked to do so
if len(sys.argv) > 1:
	if sys.argv[1] == "-r":
		print("Refreshing stats")
		make_stats_file()


# main
games_running = []
games_started = []
print()
print(datetime.now(), "OK! Go play games. I'll keep track.")
while True:
	#print("loop")
	#print("games running:",games_running)
	#print("games started:",games_started)

	exes = get_running_exes()
	for game in games_db:
		if game in exes and game not in games_running:

			time_started = datetime.now()
			print(time_started, "Started playing", name_from_exe(game), "(" + game + ")")

			games_running.append(game)
			games_started.append(time_started)

		elif game in games_running and game not in exes:

			time_stopped = datetime.now()
			print(time_stopped, "Stopped playing", name_from_exe(game))

			index = games_running.index(game)

			time_started = games_started[index]
			time_played = time_stopped - time_started
			print(name_from_exe(game),"played for",secs_to_hhmmss(time_played.total_seconds()))

			games_running.pop(index)
			games_started.pop(index)


			if update_playtimes(name_from_exe(game),time_played):
				make_stats_file()
				print(datetime.now(), "OK! Ready for more games to be played.")

	time.sleep(refresh_interval)