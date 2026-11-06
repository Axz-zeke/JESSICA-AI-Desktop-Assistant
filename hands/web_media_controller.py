"""
Jessica Hands - Sovereign Web Browser, YouTube Auto-Play & Spotify Controller (Phase 13.5)
100% Local Python execution for media playback, hardware key simulation, and web browsing.
Zero 3rd-party AI / Zero external paid services.

Capabilities:
1. Direct YouTube Auto-Play: Resolves the exact first video_id in <0.8s and launches https://www.youtube.com/watch?v=...
2. Spotify & Hardware Media Keys: Virtual key events for Play/Pause, Next Track, Prev Track, Volume Mute/Up/Down.
3. Smart Website & Google Search: Opens any website or searches Google with live grounded web summary.
"""

import os
import sys
import re
import time
import ctypes
import threading
import webbrowser
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Any, Optional, List

from brain.media_disambiguator import check_media_disambiguation, get_pending_media, clear_pending_media

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

# Windows Virtual-Key Codes for Media
VK_MEDIA_NEXT_TRACK = 0xB0  # 176
VK_MEDIA_PREV_TRACK = 0xB1  # 177
VK_MEDIA_STOP       = 0xB2  # 178
VK_MEDIA_PLAY_PAUSE = 0xB3  # 179
VK_VOLUME_MUTE      = 0xAD  # 173
VK_VOLUME_DOWN      = 0xAE  # 174
VK_VOLUME_UP        = 0xAF  # 175

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002

POPULAR_SITES = {
    "youtube": "https://www.youtube.com",
    "spotify": "https://open.spotify.com",
    "github": "https://www.github.com",
    "gmail": "https://mail.google.com",
    "facebook": "https://www.facebook.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "chatgpt": "https://chatgpt.com",
    "google": "https://www.google.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "instagram": "https://www.instagram.com",
    "amazon": "https://www.amazon.com",
    "wikipedia": "https://en.wikipedia.org"
}


def send_hardware_media_key(vk_code: int, repeat: int = 1):
    """
    Sends low-level hardware virtual key events to the Windows OS.
    Works universally across Spotify, YouTube in browser, VLC, and Windows Media Player.
    """
    try:
        user32 = ctypes.windll.user32
        for _ in range(repeat):
            user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
            time.sleep(0.04)
            user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
            time.sleep(0.04)
        return True
    except Exception as e:
        print(f"[!] Hardware media key event error: {e}")
        return False


def play_on_youtube(query: str, defer_open: bool = False, delay_sec: float = 2.5) -> Dict[str, Any]:
    """
    Finds the exact first YouTube video for the search query in <0.8s
    and launches direct https://www.youtube.com/watch?v={video_id} in the default browser.
    If defer_open=True, browser launch is deferred so Jessica speaks her response first.
    """
    t0 = time.perf_counter()
    clean_query = query.strip()
    # Strip leading assistant names & trigger words: "Jessica, play ... on youtube", "play ..."
    clean_query = re.sub(r'^(?:(?:hey|hi|yo)\s+)?jessica[,\s]+', '', clean_query, flags=re.IGNORECASE).strip()
    clean_query = re.sub(r'^(?:can you\s+|please\s+)?(?:play|search for|watch)\s+', '', clean_query, flags=re.IGNORECASE).strip()
    clean_query = re.sub(r'\s+(?:on youtube|in youtube|youtube)$', '', clean_query, flags=re.IGNORECASE).strip()

    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(clean_query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    video_id = None
    direct_url = None

    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

            # Look for /watch?v= or "videoId":"..."
            matches = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
            if not matches:
                matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            if matches:
                video_id = matches[0]
                direct_url = f"https://www.youtube.com/watch?v={video_id}"
    except Exception as e:
        print(f"[!] YouTube fast scrape notice: {e}")

    # Fallback to search results page if scraping failed
    if not direct_url:
        direct_url = search_url

    # Speak-First Sequencing: Defer or schedule browser launch
    def _do_open():
        try:
            webbrowser.open(direct_url)
        except Exception:
            os.system(f'start "" "{direct_url}"')

    if defer_open:
        # Caller (e.g. jessica_server) will execute _do_open after speech finishes
        pass
    elif delay_sec > 0:
        threading.Timer(delay_sec, _do_open).start()
    else:
        _do_open()

    elapsed = round(time.perf_counter() - t0, 3)
    return {
        "status": "success",
        "action": "youtube_autoplay",
        "query": clean_query,
        "video_id": video_id,
        "url": direct_url,
        "deferred_url": direct_url if defer_open else None,
        "elapsed_sec": elapsed,
        "reply": f"Playing {clean_query} on YouTube right now, Boss!"
    }


def control_spotify_and_media(action: str, query: Optional[str] = None) -> Dict[str, Any]:
    """
    Controls Spotify desktop app and Windows system media keys.
    Supports play, pause, resume, next track, previous track, volume adjustments, and song searches.
    """
    act = action.lower().strip()
    query_str = query.strip() if query else ""

    # Clean query of common prefix words
    if query_str:
        query_str = re.sub(r'^(?:play|search for|listen to)\s+', '', query_str, flags=re.IGNORECASE)
        query_str = re.sub(r'\s+(?:on spotify|in spotify|spotify)$', '', query_str, flags=re.IGNORECASE).strip()

    # 1. Media key actions
    if any(k in act for k in ["pause", "stop playing"]):
        send_hardware_media_key(VK_MEDIA_PLAY_PAUSE)
        return {"status": "success", "action": "pause", "reply": "Paused the music, Boss."}

    if any(k in act for k in ["resume", "unpause"]) or (act == "play" and not query_str):
        send_hardware_media_key(VK_MEDIA_PLAY_PAUSE)
        return {"status": "success", "action": "resume", "reply": "Resumed playback, Boss."}

    if any(k in act for k in ["next", "skip"]):
        send_hardware_media_key(VK_MEDIA_NEXT_TRACK)
        return {"status": "success", "action": "next_track", "reply": "Skipped to the next track, Boss."}

    if any(k in act for k in ["prev", "previous", "go back"]):
        send_hardware_media_key(VK_MEDIA_PREV_TRACK)
        return {"status": "success", "action": "prev_track", "reply": "Went back to the previous track, Boss."}

    if "mute" in act:
        send_hardware_media_key(VK_VOLUME_MUTE)
        return {"status": "success", "action": "mute", "reply": "Muted system audio, Boss."}

    if "up" in act or "increase" in act:
        send_hardware_media_key(VK_VOLUME_UP, repeat=5)
        return {"status": "success", "action": "volume_up", "reply": "Turned the volume up, Boss."}

    if "down" in act or "lower" in act:
        send_hardware_media_key(VK_VOLUME_DOWN, repeat=5)
        return {"status": "success", "action": "volume_down", "reply": "Lowered the volume, Boss."}

    # 2. Launching Spotify or playing a specific song/artist on Spotify
    if query_str:
        # Launch Spotify search URI
        spotify_uri = f"spotify:search:{urllib.parse.quote(query_str)}"
        opened = False
        try:
            os.startfile(spotify_uri)
            opened = True
        except Exception:
            try:
                os.system(f'start "" "{spotify_uri}"')
                opened = True
            except Exception:
                pass

        if not opened:
            # Fallback to Spotify Web Player
            webbrowser.open(f"https://open.spotify.com/search/{urllib.parse.quote(query_str)}")

        # Send play key after brief window launch
        time.sleep(0.8)
        send_hardware_media_key(VK_MEDIA_PLAY_PAUSE)

        return {
            "status": "success",
            "action": "spotify_play_query",
            "query": query_str,
            "reply": f"Opening Spotify to play {query_str}, Boss!"
        }
    else:
        # Open Spotify Desktop App
        try:
            os.startfile("spotify:")
        except Exception:
            try:
                os.system('start "" "spotify:"')
            except Exception:
                webbrowser.open("https://open.spotify.com")

        return {"status": "success", "action": "open_spotify", "reply": "Opening Spotify for you, Boss."}


def open_browser_or_site(command: str) -> Dict[str, Any]:
    """
    Opens Brave or default browser to a specific popular site or executes a search with live grounded summary.
    """
    cmd = command.lower().strip()

    # 0. Brave & Explicit Browser queries: "open in the Brave browser about ...", "open in brave ...", "open brave and search for ..."
    brave_match = re.search(
        r'(?:open\s+in\s+(?:the\s+)?(?:brave\s+browser|brave|browser)\s+(?:about|for)?|'
        r'open\s+(?:the\s+)?(?:brave|browser)\s+(?:and\s+search\s+for|about)?|'
        r'search\s+in\s+(?:the\s+)?(?:brave|browser)\s+for)\s*(.+)',
        cmd,
        re.IGNORECASE
    )
    if brave_match:
        query = brave_match.group(1).strip()
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        brave_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        opened_in_brave = False
        if os.path.exists(brave_exe):
            try:
                subprocess.Popen([brave_exe, search_url])
                opened_in_brave = True
            except Exception:
                pass
        if not opened_in_brave:
            webbrowser.open(search_url)

        from brain.sovereign_web_researcher import search_live_web
        research = search_live_web(query)
        summary = research.get("summary", "")

        target_name = "Brave" if opened_in_brave else "your browser"
        reply = f"I opened {target_name} and searched for '{query}', Boss. "
        if summary and "limited immediate" not in summary:
            reply += summary
        else:
            reply += "Your search results are ready on screen."

        return {
            "status": "success",
            "action": "brave_search",
            "query": query,
            "url": search_url,
            "summary": summary,
            "reply": reply
        }

    # 1. Google Search request: "Search Google for ...", "Google ...", "Search the web for ..."
    search_match = re.search(r'(?:search(?:\s+google|\s+the\s+web|\s+online)?\s+for|google|look\s+up)\s+(.+)', cmd, re.IGNORECASE)
    if search_match and not any(cmd.startswith(f"open {s}") for s in POPULAR_SITES):
        query = search_match.group(1).strip()
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(search_url)

        # Simultaneously run live sovereign web research for Jessica's voice reply
        from brain.sovereign_web_researcher import search_live_web
        research = search_live_web(query)
        summary = research.get("summary", "")

        reply = f"I opened Google for '{query}', Boss. "
        if summary and "limited immediate" not in summary:
            reply += summary
        else:
            reply += "Your search results are ready on screen."

        return {
            "status": "success",
            "action": "google_search",
            "query": query,
            "url": search_url,
            "summary": summary,
            "reply": reply
        }

    # 2. Known site match
    for site_key, site_url in POPULAR_SITES.items():
        # e.g. "open youtube", "launch github", "go to facebook", "open gmail"
        if re.search(rf'\b(?:open|launch|go\s+to)\s+{re.escape(site_key)}\b', cmd) or cmd == f"open {site_key}":
            webbrowser.open(site_url)
            return {
                "status": "success",
                "action": "open_site",
                "site": site_key,
                "url": site_url,
                "reply": f"Opening {site_key.title()} in your browser, Boss."
            }

    # 3. Direct URL or domain (e.g., "open example.com", "open https://...")
    url_match = re.search(r'(?:open|go\s+to|launch)\s+((?:https?://)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)', cmd)
    if url_match:
        target_url = url_match.group(1).strip()
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url
        webbrowser.open(target_url)
        return {
            "status": "success",
            "action": "open_url",
            "url": target_url,
            "reply": f"Opening {target_url} in your browser, Boss."
        }

    # 4. Default: Open browser to homepage
    webbrowser.open("https://www.google.com")
    return {
        "status": "success",
        "action": "open_browser",
        "url": "https://www.google.com",
        "reply": "Opening your browser, Boss."
    }


def execute_web_media_command(command: str, defer_open: bool = True) -> Optional[Dict[str, Any]]:
    """
    Main dispatcher for all web, YouTube, Spotify, and media automation requests.
    Returns None if command does not match web/media intents.
    """
    cmd = command.lower().strip()

    # 0. Smart Artist vs Song Disambiguation Gate
    disambig = check_media_disambiguation(command)
    if disambig.get("status") == "needs_disambiguation":
        return {
            "status": "disambiguation_required",
            "action": "media_disambiguation",
            "artist": disambig.get("artist"),
            "reply": disambig.get("reply"),
            "requires_followup": True
        }
    elif disambig.get("status") == "resolved":
        res_query = disambig.get("query")
        custom_reply = disambig.get("reply")
        res = play_on_youtube(res_query, defer_open=defer_open)
        if custom_reply:
            res["reply"] = custom_reply
        return res

    # YouTube requests: "play ... on youtube", "play ... video", "youtube ..."
    if "youtube" in cmd and any(w in cmd for w in ["play", "watch", "listen", "search"]):
        return play_on_youtube(cmd, defer_open=defer_open)

    if cmd.startswith("play ") and ("youtube" in cmd or "video" in cmd or "song" in cmd or "music" in cmd or "track" in cmd):
        if "spotify" in cmd:
            return control_spotify_and_media("play", cmd)
        return play_on_youtube(cmd, defer_open=defer_open)

    # General "play [song/artist]" (defaults to YouTube video auto-play for instant audiovisual playback)
    if cmd.startswith("play ") and len(cmd) > 6 and not any(w in cmd for w in ["game", "with"]):
        return play_on_youtube(cmd, defer_open=defer_open)

    # Spotify requests
    if "spotify" in cmd:
        if any(w in cmd for w in ["play", "listen"]):
            return control_spotify_and_media("play", cmd)
        return control_spotify_and_media("open")

    # Hardware Media Key controls
    pause_phrases = ["pause music", "pause the music", "pause song", "pause the song", "pause video", "pause the video", "stop playing", "stop the music", "pause playback", "pause"]
    if any(k == cmd or k in cmd for k in pause_phrases):
        return control_spotify_and_media("pause")

    resume_phrases = ["resume music", "resume the music", "resume song", "resume playback", "unpause", "resume", "play the music"]
    if any(k == cmd or k in cmd for k in resume_phrases):
        return control_spotify_and_media("resume")

    if any(k in cmd for k in ["next song", "next track", "skip track", "skip song", "skip this", "skip"]):
        return control_spotify_and_media("next")

    if any(k in cmd for k in ["previous song", "previous track", "go back a track", "last song", "previous"]):
        return control_spotify_and_media("prev")

    # Web browser / search commands (including Brave and general browser)
    if any(k in cmd for k in ["brave", "browser"]) or \
       any(cmd.startswith(p) for p in ["open browser", "open google", "search google", "search the web", "look up", "google "]) or \
       any(re.search(rf'\b(?:open|launch|go\s+to)\s+{re.escape(site)}\b', cmd) for site in POPULAR_SITES):
        return open_browser_or_site(cmd)

    return None


def can_handle_web_media(command: str) -> bool:
    """
    Fast boolean check if a command matches web, media, YouTube, or Spotify execution patterns.
    """
    cmd = command.lower().strip()
    if not cmd:
        return False
    # Active multi-turn media disambiguation in progress: intercept follow-up song choice!
    if get_pending_media() is not None:
        return True
    # Explicit Brave / Browser commands
    if any(k in cmd for k in ["brave browser", "in brave", "open brave", "in the brave", "open in browser", "open in the browser", "open the browser", "open browser", "browser about"]):
        return True
    if "youtube" in cmd and any(w in cmd for w in ["play", "watch", "listen", "search", "open"]):
        return True
    if cmd.startswith("play ") and len(cmd) > 6 and not any(w in cmd for w in ["game", "with"]):
        return True
    if "spotify" in cmd:
        return True
    if any(k in cmd for k in ["pause music", "pause the music", "pause song", "pause the song", "pause video", "pause playback", "pause", "stop playing", "stop the music"]):
        return True
    if any(k in cmd for k in ["resume music", "resume the music", "resume song", "resume playback", "unpause", "resume"]):
        return True
    if any(k in cmd for k in ["next song", "next track", "skip track", "skip song", "skip this", "skip"]):
        return True
    if any(k in cmd for k in ["previous song", "previous track", "go back a track", "last song", "previous"]):
        return True
    if any(cmd.startswith(p) for p in ["open browser", "open google", "search google", "search the web", "look up", "google "]) or \
       any(re.search(rf'\b(?:open|launch|go\s+to)\s+{re.escape(site)}\b', cmd) for site in POPULAR_SITES):
        return True
    return False

