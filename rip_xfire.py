import os,sys,time,shutil,json
from datetime import datetime, timedelta
from natsort import natsorted

games_list = "games.tsv"
playtimes_db = "playtimes.json"
refresh_interval = 5

print("Running in", os.getcwd())

game_exes = []
game_names = []

if not os.path.isfile(games_list):
	print(games_list,"not found")
	sys.exit(1)
else:
	f = open(games_list,"r")
	lines = f.readlines()
	f.close()

	for line in lines: # add exe names to games_db
		title = line.split("\t")[1].strip()
		#print(title)

		for exe in line.split("\t")[0].strip().split(","):
			game_exes.append(exe)
			game_names.append(title)
			print("Tracking:", title, exe)

print("EXEs tracked:", len(game_exes))

def get_running_exes(): # https://www.geeksforgeeks.org/python-get-list-of-running-processes/
	wmic_output = os.popen('wmic process get description, processid').read().strip() 
	# TODO: can get path by using ExecutablePath (useful for games using same .exe name, like re3)
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

def secs_to_hrs(secs):
	return round(secs/3600, 1)

def update_playtimes(exe,played_secs,unixdate):

	title = game_names[game_exes.index(exe)]

	j = []

	if os.path.isfile(playtimes_db):
		with open(playtimes_db, "r") as f:
			j = json.load(f)

	#print(j)

	found = False
	for g in j:
		#print(g)
		if g["title"] == title:
			found = True
			g["secs"] = g["secs"] + played_secs
			g["lastplayed"] = unixdate
			print("new total play time for", title, ":", secs_to_hrs(g["secs"]), "hrs")

	if not found:
		print(title, "was not in playtimes db, adding it...")
		g = {
			'title': title,
			'secs': played_secs,
			'lastplayed': unixdate
		}
		j.append(g)

	# write db_games and db_playtimes to file
	f = open(playtimes_db,"w")
	f.write(json.dumps(j, indent=2))
	f.close()
	print("updated",playtimes_db)

	return True

def make_stats_file():
	j = []

	if os.path.isfile(playtimes_db):
		with open(playtimes_db, "r") as f:
			j = json.load(f)

	
		# sort by most played (most seconds)
		j = sorted(j, key=lambda k: k.get('secs', 0), reverse=True)

		# CSV stats
		stats_file = "Stats.csv"
		f = open(stats_file,"w")
		f.write("Game,Hours,LastPlayed\n") # top row (column names)
		for game in j: # reverse to get most on top
			name = game['title']
			hours = round(game['secs'] / 3600, 1)

			date = ""
			if game['lastplayed'] > 0:
				date = (datetime.fromtimestamp(game['lastplayed']).strftime('%Y-%m-%d %H:%M:%S'))

			f.write(name + "," + str(hours) + "," + date + "\n")
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
		f.write("<tr><th>Title</th><th>Hours</th><th>Last Played</th></tr>")
		# Write table
		for game in j: # reverse to get most on top
			name = game['title']
			total_played += game['secs']
			date = ""
			if game['lastplayed'] > 0:
				date = (datetime.fromtimestamp(game['lastplayed']).strftime('%Y-%m-%d %H:%M:%S'))
			hours = round(game['secs'] / 3600, 1)
			f.write('<tr><td><div class="game-name">' + name + '</div></td>')
			f.write('<td><span title="' + secs_to_hhmmss(game['secs']) + '">')
			f.write(str(hours) + " hrs")
			f.write("</span></td>")
			f.write("<td>" + str(date) + "</td>")
			f.write("</tr>")

		# Write total
		total_hours = round( total_played / 3600 )
		f.write("<tr><td><b>Total:</b></td>")
		f.write('<td><span title="' + secs_to_hhmmss(total_played) + '"><b>')
		f.write(str(total_hours) + " hrs")
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
print("OK! Go play games. I'll keep track.")
while True:
	#print("loop")
	#print("games running:",games_running)
	#print("games started:",games_started)

	exes = get_running_exes()
	for exe in game_exes:
		if exe in exes and exe not in games_running:

			time_started = datetime.now()
			print(time_started, exe, "started")

			games_running.append(exe)
			games_started.append(time_started)

		elif exe in games_running and exe not in exes:

			time_stopped = datetime.now()
			print(time_stopped, exe, "stopped")

			index = games_running.index(exe)

			time_started = games_started[index]
			time_played = int( round( (time_stopped - time_started).total_seconds() ) )
			print(exe,"ran for",time_played,"secs")

			games_running.pop(index)
			games_started.pop(index)


			if update_playtimes(exe,time_played,int(time_stopped.timestamp())):
				make_stats_file()
				print("OK! Ready for more games to be played.")
				print()

	time.sleep(refresh_interval)