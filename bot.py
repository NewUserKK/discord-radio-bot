#!/usr/bin/python3

import discord
import logging
import os

from discord.ext.commands import Bot, Context
from discord_client import DiscordClient

DISCORD_PUBLIC_KEY = os.environ['DISCORD_PUBLIC_KEY']
DISCORD_SECRET_KEY = os.environ['DISCORD_SECRET_KEY']
DISCORD_APP_ID = os.environ['DISCORD_APP_ID']
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

clients = {}

def ensure_client(ctx: Context) -> DiscordClient:
    guild_id = ctx.guild.id

    if guild_id not in clients:
        clients[guild_id] = DiscordClient()

    return clients[guild_id]


intents = discord.Intents.default()
intents.message_content = True
bot = Bot(command_prefix='/', intents=intents)


@bot.command(name='play', description='Play youtube link or stream radio')
async def play(ctx: Context, url: str):
    await ensure_client(ctx).play(ctx, url)


@bot.command(name='stop', description='Stop currently playing track')
async def stop(ctx: Context):
    await ensure_client(ctx).stop(ctx)


@bot.command(name='presets', description='Get radio presets')
async def presets(ctx: Context):
    await ensure_client(ctx).presets(ctx)


@bot.command(name='ping', description='Healthcheck')
async def ping(ctx: Context):
    await ctx.send('pong')


logging.basicConfig(filename='std.log', level=logging.DEBUG)

log_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
bot.run(DISCORD_TOKEN, log_handler=log_handler, log_level=logging.DEBUG)
