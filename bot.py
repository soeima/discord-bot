import discord 
from discord.utils import get
import os
from dotenv import load_dotenv
from converter import get_song_url, get_spotify_playlist
import youtube_dl
from discord import FFmpegPCMAudio

load_dotenv()
client = discord.Client()

queue = []

@client.event
async def on_ready():
    print('Bot is online')

@client.event
async def on_message(message):
    prefix = "!"
    if message.author == client.user:
        return

    msg = message.content.split()

    voicechannel = message.author.voice.channel
    if not voicechannel:
        await message.channel.send("You need to be connected to a voice channel to call the bot!")
        
    voiceclient = get(client.voice_clients, guild=message.guild)

    if msg[0] == prefix+'join':

        #If bot is already connected, switch to the correct channel

        if voiceclient and voiceclient.is_connected():
            await voiceclient.move_to(voicechannel)

        #if it's not connected, connect
        else:
            await voicechannel.connect()

    elif msg[0] == prefix+'dc':

        if voiceclient.is_connected():
            await voiceclient.disconnect()
        await message.channel.send("Goodbye!")

    elif msg[0] == prefix+'play':

        if voiceclient and voiceclient.is_connected():
            await voiceclient.move_to(voicechannel)
        else:
            await voicechannel.connect()

        voiceclient = get(client.voice_clients, guild=message.guild)
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        if not voiceclient.is_playing():

            url = str(message.content)[len(msg[0])+1:]
            #if it is a spotify link
            if "spotify" in url:
                #if it is a playlist
                if "playlist" in url:
                    queue.extend(get_spotify_playlist(url))
                    url = get_song_url(queue.pop(0))
                else:
                    url = get_song_url(url)
            
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            URL = info['url']
            voiceclient.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
            voiceclient.is_playing()

        else:
            url = str(message.content)[len(msg[0])+1:]
            if "spotify" in url:
                if "playlist" in url:
                    queue.extend(get_spotify_playlist(url))
            queue.append(url)
            await message.channel.send("Song added to queue!")



    elif msg[0] == prefix+'skip':

        if queue:
            
            url = queue.pop(0)

            voiceclient.stop()

            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            if "youtube" in url:
                with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
                URL = info['url']
                voiceclient = get(client.voice_clients, guild=message.guild)
                voiceclient.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
                voiceclient.is_playing()


            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(get_song_url(url), download=False)
            URL = info['url']
            title = info['title']
            voiceclient = get(client.voice_clients, guild=message.guild)
            voiceclient.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
            voiceclient.is_playing()
            await message.channel.send("Song skipped! Now playing: **" + title + "**")

        else:

            await message.channel.send("There are no more queued songs to skip to!")

    elif msg[0] == prefix+"pause":
        if voiceclient.is_playing():
            voiceclient.pause()
        await message.channel.send("Pausing...")

    elif msg[0] == prefix+"resume":
        if voiceclient.is_paused():
            voiceclient.resume()

        await message.channel.send("Resuming...")
            
    elif msg[0] == prefix+"stop":
        voiceclient.stop()
        await message.channel.send("Stopping...")

    elif msg[0] == prefix+"queue":

        if queue:
            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
            reply = ""
            if len(queue) > 10:
                
                for i in range(0,10):
                    if "youtube" in queue[i]:
                        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                            info = ydl.extract_info(queue[i], download=False)
                        title = info['title']
                        reply += "**" + str(i+1) + ".**   " + title + "\n"
                    if "spotify" in queue[i]:
                        url = get_song_url(queue[i])
                        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                            info = ydl.extract_info(url, download=False)
                        title = info['title']
                        reply += "**" + str(i+1) + ".**   " + title + "\n"
                    else:
                        reply += "**" + str(i+1) + ".**   " + queue[i] + "\n"
                
                reply += "** More... **"
                    
            else:
                for i in range(0,len(queue)):
                    if "youtube" in queue[i]:
                        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                            info = ydl.extract_info(queue[i], download=False)
                        title = info['title']
                        reply += "**" + str(i+1) + ".**   " + title + "\n"
                    if "spotify" in queue[i]:
                        url = get_song_url(queue[i])
                        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                            info = ydl.extract_info(url, download=False)
                        title = info['title']
                        reply += "**" + str(i+1) + ".**   " + title + "\n"
                    else:
                        reply += "**" + str(i+1) + ".**   " + queue[i] + "\n"

            await message.channel.send(reply)

        else:
            await message.channel.send("Queue is empty at the moment!")

    elif msg[0] == prefix+"clear":

        queue.clear()
        await message.channel.send("Queue cleared!")

    elif msg[0] == prefix+"commands":
        await message.channel.send("```\n!join - Bot will join your channel\n!dc - Bot will disconnect from your channel\n!play <url> - Bot will play the url, if it is already playing something, it will add it to a queue\n!skip - Bot will skip the track currently playing\n!pause - Bot will pause the track\n!stop - Bot will stop playing\n!queue - Bot will display the currently queued tracks\n!clear - Bot will clear all queued tracks\n```")


client.run(os.environ.get('TOKEN'))