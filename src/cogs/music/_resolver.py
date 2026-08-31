"""
Hertz Music Bot - Ultimate Unstoppable Music Resolver
Official 320kbps CD Master Engine + YouTube & Spotify Studio Extractors + 0ms RAM Cache.
"""

from __future__ import annotations

import asyncio
import base64
import html
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional

import aiohttp
from pyDes import des, ECB, PAD_PKCS5
import yt_dlp

from src.cogs.music._types import TrackItem, YDL_OPTS

logger = logging.getLogger("Hertz.Music.Resolver")

RESOLVER_POOL = ThreadPoolExecutor(max_workers=4, thread_name_prefix="MusicResolver")


class MusicResolver:
    """Universal Unstoppable Music Resolver."""
    _CACHE: Dict[str, TrackItem] = {}

    @classmethod
    def _decrypt_saavn_url(cls, encrypted_url: str) -> Optional[str]:
        """Decrypt JioSaavn 320kbps master media URL."""
        try:
            cipher = des(b'38346591', ECB, pad=None, padmode=PAD_PKCS5)
            dec = cipher.decrypt(base64.b64decode(encrypted_url.strip()))
            url = dec.decode('utf-8', errors='ignore')
            if 'http' in url:
                url = url[url.find('http'):]
                if '.mp4' in url:
                    url = url.split('.mp4')[0] + '.mp4'
                return url.replace('_96.mp4', '_320.mp4').replace('_160.mp4', '_320.mp4')
        except Exception as e:
            logger.warning(f"Saavn decrypt error: {e}")
        return None

    @classmethod
    async def extract_spotify_title(cls, url: str) -> Optional[str]:
        """Extract song title from Spotify URL using Spotify oEmbed."""
        try:
            oembed_url = f"https://open.spotify.com/oembed?url={url}"
            headers = {"User-Agent": "Mozilla/5.0"}
            async with aiohttp.ClientSession(headers=headers) as s:
                async with s.get(oembed_url, timeout=aiohttp.ClientTimeout(total=3)) as r:
                    if r.status == 200:
                        data = await r.json()
                        title = data.get("title", "")
                        return title
        except Exception:
            pass
        return None

    @classmethod
    async def resolve(cls, query: str) -> Optional[TrackItem]:
        raw_q = query.strip()
        cache_key = raw_q.lower()

        # Step 0: Instant 0ms RAM Cache Check
        if cache_key in cls._CACHE:
            cached = cls._CACHE[cache_key]
            logger.info(f"Instant cache hit for '{raw_q}' (0ms)")
            return TrackItem(
                title=cached.title,
                author=cached.author,
                duration=cached.duration,
                url=cached.url,
                stream_url=cached.stream_url,
                thumbnail=cached.thumbnail,
                requester=""
            )

        # Spotify URL detection
        search_query = raw_q
        if "spotify.com" in raw_q:
            spotify_title = await cls.extract_spotify_title(raw_q)
            if spotify_title:
                search_query = spotify_title

        is_url = search_query.startswith("http://") or search_query.startswith("https://")

        # Step 1: Official 320kbps CD Studio Master Engine (For Search Keywords)
        if not is_url:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                params = {
                    '__call': 'search.getResults',
                    '_format': 'json',
                    '_marker': '0',
                    'api_version': '4',
                    'ctx': 'web6dot0',
                    'n': '3',
                    'p': '1',
                    'q': search_query
                }
                async with aiohttp.ClientSession(headers=headers) as s:
                    async with s.get('https://www.jiosaavn.com/api.php', params=params, timeout=aiohttp.ClientTimeout(total=4)) as r:
                        if r.status == 200:
                            data = json.loads(await r.text())
                            results = data.get('results', [])
                            if results:
                                pids = results[0].get('id')
                                dparams = {
                                    '__call': 'song.getDetails',
                                    'cc': 'in',
                                    '_marker': '0',
                                    '_format': 'json',
                                    'pids': pids
                                }
                                async with s.get('https://www.jiosaavn.com/api.php', params=dparams, timeout=aiohttp.ClientTimeout(total=4)) as dr:
                                    if dr.status == 200:
                                        ddata = json.loads(await dr.text())
                                        sinfo = ddata.get(pids, {})
                                        enc_url = sinfo.get('encrypted_media_url')
                                        stream_url = cls._decrypt_saavn_url(enc_url) if enc_url else None
                                        
                                        if stream_url:
                                            raw_title = sinfo.get('song') or sinfo.get('title') or search_query
                                            clean_title = html.unescape(raw_title)
                                            author = html.unescape(sinfo.get('primary_artists') or sinfo.get('singers') or 'Official Artist')
                                            thumb = sinfo.get('image', '').replace('150x150', '500x500')
                                            duration = int(sinfo.get('duration', 240))
                                            web_url = sinfo.get('perma_url') or search_query

                                            track = TrackItem(
                                                title=clean_title,
                                                author=author,
                                                duration=duration,
                                                url=web_url,
                                                stream_url=stream_url,
                                                thumbnail=thumb,
                                                requester=""
                                            )
                                            cls._CACHE[cache_key] = track
                                            return track
            except Exception as e:
                logger.warning(f"Official 320kbps master search notice: {e}")

        # Step 2: YouTube Studio Extractor
        loop = asyncio.get_event_loop()
        target = search_query if is_url else f"ytsearch1:{search_query}"

        def _yt_extract():
            try:
                with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
                    info = ydl.extract_info(target, download=False)
                    if not info:
                        return None
                    if 'entries' in info and info['entries']:
                        return info['entries'][0]
                    return info
            except Exception as e:
                logger.error(f"YouTube studio extraction error for '{target}': {e}")
            return None

        entry = await loop.run_in_executor(RESOLVER_POOL, _yt_extract)
        if entry and entry.get('url'):
            raw_title = entry.get('title', search_query)
            clean_t = re.sub(
                r'\(Full Video\)|\[Official Video\]|\(Official Audio\)|\|.*$',
                '',
                raw_title,
                flags=re.IGNORECASE
            ).strip()
            author = entry.get('uploader') or entry.get('artist') or entry.get('channel') or 'Official Artist'
            track = TrackItem(
                title=clean_t or raw_title,
                author=author,
                duration=int(entry.get('duration', 0)),
                url=entry.get('webpage_url') or raw_q,
                stream_url=entry.get('url'),
                thumbnail=entry.get('thumbnail', ''),
                requester=""
            )
            cls._CACHE[cache_key] = track
            return track

        return None
