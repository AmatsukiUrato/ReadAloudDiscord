# -*- coding: utf-8 -*-

# MustNeedPackage
from ctypes.util import find_library
import discord
import asyncio

# AddedPackage
import sqlite3
import threading

# version
__version__ = '0.1.0'


# Discord.pyの読み込み
client = discord.Client()


# 鍵の読み込み
KEY = None
with open('TESTKEY.txt', 'r') as f:
    KEY = f.read()


# データベースの読み込み
dbname = 'readloud.db'
conn = sqlite3.connect(dbname)
c = conn.cursor()


# Botが接続出来たとき
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    if not discord.opus.is_loaded():
        discord.opus.load_opus(find_library("opus"))

    # テーブルの存在確認
    # テーブル名の定義
    tablename = "readloud"
    c.execute("SELECT * FROM sqlite_master WHERE type='table' and name='%s'" % tablename)
    if not c.fetchone():
        # id, 名前，現在のタイム，アラート終了予定タイム，入力した人
        c.execute("CREATE TABLE %s(id INTEGER PRIMARY KEY, channel_name TEXT, channel_id TEXT)" % tablename)
        conn.commit()


@client.event
async def on_message(message):


    ##########################
    # チャンネルへ呼び出し
    ##########################
    if message.content.startswith('!rbot summon'):
        if not client.is_voice_connected(message.server):
            await client.join_voice_channel(message.author.voice.voice_channel)



    ##########################
    # チャンネル移動
    ##########################
    elif message.content.startswith('!rbot move'):
        if client.is_voice_connected(message.server):
            await client.voice_client_in(message.server).move_to(message.author.voice.voice_channel)



    ##########################
    # チャンネルから落とす
    ##########################
    elif message.content.startswith('!rbot disconnect'):
        if client.is_voice_connected(message.server):
            await client.voice_client_in(message.server).disconnect()



    ##########################
    # チャンネルに再入場(エラー時利用)
    ##########################
    elif message.content.startswith('!rbot rejoin'):
        if client.is_voice_connected(message.server):
            voice_channel = client.voice_client_in(message.server)
            print(type(voice_channel))
            await voice_channel.disconnect()
            await client.join_voice_channel(voice_channel.channel)



    ##########################
    # 読み上げるチャンネルの登録
    ##########################
    elif message.content.startswith('!rbot register'):
        c.execute("SELECT * FROM readloud WHERE channel_id = ?", (message.channel.id,))
        # is_read
        if not c.fetchone():
            c.execute("INSERT INTO readloud (channel_name, channel_id) VALUES (?,?)", (message.channel.name,message.channel.id))
            conn.commit()




    ##########################
    # 読み上げ
    ##########################
    else:
        # is_InVC
        if client.is_voice_connected(message.server):
            c.execute("SELECT * FROM readloud WHERE channel_id = ?", (message.channel.id,))
            # is_read
            if c.fetchone():
                # if sound_player is None:
                sound_player = client.voice_client_in(message.server).create_ffmpeg_player('test.wav')
                sound_player.start()
                sound_player.join()



# Run
client.run(KEY)
