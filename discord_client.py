import logging
import yt_dlp as youtube_dl

from dataclasses import dataclass

from discord import FFmpegPCMAudio
from discord.ext.commands import Context

@dataclass
class RadioPreset:
    name: str
    url: str

_radio_presets_list = [
    RadioPreset('шансон', 'https://chanson.hostingradio.ru:8041/chanson128.mp3?md5=X0T88ApvwQEy8XTCR--xhA&amp;e=1707603476'),
    RadioPreset('дача', 'http://vdfm.ru:8000/dacha?type=.mp3'),
]

_radio_presets = { preset.name: preset for preset in _radio_presets_list }


class DiscordClient:
    def __init__(self):
        self.player = None

    async def play(self, ctx: Context, inp: str):
        logging.debug(f'receivied play with url {inp}')
        source = ''
        if 'youtube' in inp or 'youtu.be' in inp:
            logging.debug('it is youtube')
            source = self._get_source_from_youtube(inp)
        elif inp.lower() in _radio_presets:
            logging.debug(f'found radio {inp}')
            source = _radio_presets[inp].url
        else:
            source = inp

        logging.debug(f'play source: {source}')

        try:
            await self._send_reply(ctx, 'Коннекчусь, потерпи')
            await self._connect_to_channel(ctx)
        except Exception as e:
            logging.warning('Failed to connect to channel')
            await self._send_reply(ctx, str(e))
            pass

        try:
            self.player.play(FFmpegPCMAudio(source))
        except Exception as e:
            logging.warning(f'Failed to play: {e}')
            if 'Already playing audio' in str(e):
                await self._send_reply(ctx, 'Уже кайфуем под другой трек, стопни через /stop')
            else:
                await self._send_reply(ctx, str(e))

    async def stop(self, ctx: Context):
        if self.player:
            self.player.stop()
            await self._disconnect_from_channel(ctx)

    async def presets(self, ctx: Context):
        answer = 'Пресеты радио:\n' + '\n'.join(map(lambda preset: f'{preset.name} -- {preset.url}', _radio_presets.values()))
        await self._send_reply(ctx, answer)

    async def _connect_to_channel(self, ctx: Context):
        channel = ctx.message.author.voice.channel
        self.player = await channel.connect()

    async def _disconnect_from_channel(self, ctx: Context):
        client = ctx.message.guild.voice_client
        self.player = None
        await client.disconnect()

    async def _send_reply(self, ctx: Context, reply: str):
        await ctx.message.reply(reply)

    def _get_source_from_youtube(self, url: str) -> str:
        assert 'youtube' in url or 'youtu.be' in url

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            song_info = ydl.extract_info(url, download=False)
            formats = song_info['formats']
            for format in formats:
                if format['resolution'] == 'audio only':
                    return format['url']

        raise ValueError("No url found")
