import discord
import os
import asyncio
import yt_dlp
import spotipy

from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

def run_bot():
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()
    # Variáveis de ambiente
    TOKEN = os.getenv('discord_token')
    SPOTIFY_CLIENT_ID = os.getenv('spotify_client_id')
    SPOTIFY_CLIENT_SECRET = os.getenv('spotify_client_secret')
    SPOTIFY_REDIRECT_URI = os.getenv('spotify_redirect_uri')

    # Configura as credenciais do cliente
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    # Dicionário para armazenar clientes de voz
    voice_clients = {}

    # Opções de configuração para baixar áudio do YouTube
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    # Opções de configuração para o ffmpeg
    ffmpeg_options = {'options': '-vn'}

    # Autenticação no Spotify
    spotify_auth_manager = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                        client_secret=SPOTIFY_CLIENT_SECRET,
                                        redirect_uri=SPOTIFY_REDIRECT_URI,
                                        scope="user-read-playback-state,user-modify-playback-state")

    spotify = spotipy.Spotify(auth_manager=spotify_auth_manager)

    @client.event
    async def on_ready():
        print(f'{client.user} is working')

    @client.event
    async def on_message(message):
        if message.content.startswith("?play"):
            try:
                # Conecta ao canal de voz do autor da mensagem
                voice_client = await message.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client
            except Exception as e:
                print(e)

            try:
                url = message.content.split()[1]
                if "spotify.com" in url:
                    # Lida com URLs do Spotify
                    track_info = spotify.track(url)
                    song_url = track_info['preview_url']
                    if song_url is None:
                        await message.channel.send("Desculpe, não foi possível encontrar uma prévia desta faixa no Spotify.")
                        return
                else:
                    # Lida com URLs do YouTube
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                    song_url = data['url']

                # Toca a música
                player = discord.FFmpegPCMAudio(song_url, **ffmpeg_options)
                voice_clients[message.guild.id].play(player)
            except Exception as e:
                print(e)

        if message.content.startswith("?pause"):
            try:
                voice_clients[message.guild.id].pause()
            except Exception as e:
                print(e)

        if message.content.startswith("?resume"):
            try:
                voice_clients[message.guild.id].resume()
            except Exception as e:
                print(e)

        if message.content.startswith("?stop"):
            try:
                voice_clients[message.guild.id].stop()
            except Exception as e:
                print(e)
                
    client.run(TOKEN)

if __name__ == "__main__":
    run_bot()
