import discord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv

async def send_message(message, user_message, is_private):
    try:
        response = "Placeholder response"  # Ajuste conforme necessário
        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)
            
    except Exception as e:
        print(e)

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('discord_token')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    voice_clients = {}
    queues = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)
    ffmpeg_options = {'options': '-vn'}

    async def play_next(ctx):
        guild_id = ctx.guild.id
        if queues[guild_id]:
            url = queues[guild_id].pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            song = data['url']
            player = discord.FFmpegPCMAudio(song, **ffmpeg_options)

            def after_playing(error):
                coro = play_next(ctx)
                fut = asyncio.run_coroutine_threadsafe(coro, loop)
                try:
                    fut.result()
                except Exception as e:
                    print(e)

            voice_clients[guild_id].play(player, after=after_playing)
        else:
            await voice_clients[guild_id].disconnect()
            del voice_clients[guild_id]

    @client.event
    async def on_ready():
        print(f'{client.user} is working')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        
        user_message = str(message.content)

        if user_message.startswith('?'):
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)

        guild_id = message.guild.id
        if message.content.startswith("?play"):
            url = message.content.split()[1]

            if guild_id not in queues:
                queues[guild_id] = []

            queues[guild_id].append(url)

            if guild_id not in voice_clients:
                try:
                    voice_client = await message.author.voice.channel.connect()
                    voice_clients[guild_id] = voice_client
                    await play_next(message)
                except Exception as e:
                    print(e)
            else:
                await message.channel.send(f'Added to queue: {url}')

        if message.content.startswith("?pause"):
            try:
                voice_clients[guild_id].pause()
            except Exception as e:
                print(e)

        if message.content.startswith("?resume"):
            try:
                voice_clients[guild_id].resume()
            except Exception as e:
                print(e)

        if message.content.startswith("?stop"):
            try:
                voice_clients[guild_id].stop()
                queues[guild_id] = []
                await voice_clients[guild_id].disconnect()
                del voice_clients[guild_id]
            except Exception as e:
                print(e)

        if message.content.startswith("?queue"):
            try:
                queue_list = "\n".join(queues[guild_id]) if guild_id in queues and queues[guild_id] else "The queue is empty."
                await message.channel.send(f"Current queue:\n{queue_list}")
            except Exception as e:
                print(e)

        if message.content.startswith("?skip"):
            try:
                if guild_id in voice_clients and voice_clients[guild_id].is_playing():
                    voice_clients[guild_id].stop()
                    await play_next(message)
                else:
                    await message.channel.send("No song is currently playing.")
            except Exception as e:
                print(e)

    client.run(TOKEN)
