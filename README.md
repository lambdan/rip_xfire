# rip_xfire

[Xfire](https://en.wikipedia.org/wiki/Xfire) was a great service for gamers that unfortunately died in 2013. I was a heavy user of Xfire, it was always one of the first programs I installed and I chatted a lot with my friends there. Apart from chatting with friends it also let you launch games from its taskbar icon, show a FPS overlay, take screenshots and most importantly keep track of how long you played.

I loved browsing my stats page and seeing how many hours I had gotten.
And what was nice about it was that it kept track no matter how you launched games, be it through Steam or if you had some standalone exe files just lying around.
This is becoming more and more annoying nowadays with every company having their own launcher or locking games to exclusive game launchers (*cough* Epic *cough*). And every launcher displays time played in different spots, if at all. 

So this is just a simple script that looks at what `.exe`'s you have running and if it recognizes it, it keeps track of how long it's been running.
In order to recognize games you simply add them to `games.txt` - it should be pretty self-explanatory.

After you exit a game it updates your total playtime and also writes the simple stats in a simple HTML document and a `.csv` you can import into Excel or whatever you like to visualize.

# Tips and tricks

- You can run with the `-r` parameter to force a refresh of the Stats files on launch. Useful if you're manually editting `playtimes.txt`