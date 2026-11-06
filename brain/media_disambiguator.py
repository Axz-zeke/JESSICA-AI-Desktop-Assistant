"""
Media Disambiguator & Multi-Turn Conversational State Tracker
============================================================
Handles smart artist vs. song disambiguation:
1. Detects when user asks to play a band/artist without specifying a track.
2. Prompts user with natural spoken recommendations.
3. Tracks pending media state so the follow-up song choice is resolved seamlessly.
"""

import re
import time
import threading
from typing import Dict, Any, Optional, Tuple

KNOWN_ARTISTS = {
    "iv of spades": {
        "canonical": "IV of Spades",
        "top_songs": ["Mundo", "Come Inside of My Heart", "Hey Barbara", "Bawat Kaluluwa"],
        "prompt_suggestions": "Mundo, Come Inside of My Heart, or Hey Barbara"
    },
    "eraserheads": {
        "canonical": "Eraserheads",
        "top_songs": ["Ang Huling El Bimbo", "With a Smile", "Ligaya", "Magasin"],
        "prompt_suggestions": "Ang Huling El Bimbo, With a Smile, or Ligaya"
    },
    "queen": {
        "canonical": "Queen",
        "top_songs": ["Bohemian Rhapsody", "Don't Stop Me Now", "Under Pressure"],
        "prompt_suggestions": "Bohemian Rhapsody, Don't Stop Me Now, or Under Pressure"
    },
    "bruno mars": {
        "canonical": "Bruno Mars",
        "top_songs": ["Die With A Smile", "That's What I Like", "Just the Way You Are"],
        "prompt_suggestions": "Die With A Smile, That's What I Like, or Just the Way You Are"
    },
    "red hot chili peppers": {
        "canonical": "Red Hot Chili Peppers",
        "top_songs": ["Californication", "Under the Bridge", "Can't Stop"],
        "prompt_suggestions": "Californication, Under the Bridge, or Can't Stop"
    },
    "taylor swift": {
        "canonical": "Taylor Swift",
        "top_songs": ["Cruel Summer", "Blank Space", "Anti-Hero"],
        "prompt_suggestions": "Cruel Summer, Blank Space, or Anti-Hero"
    },
    "beatles": {
        "canonical": "The Beatles",
        "top_songs": ["Hey Jude", "Let It Be", "Come Together"],
        "prompt_suggestions": "Hey Jude, Let It Be, or Come Together"
    },
    "the beatles": {
        "canonical": "The Beatles",
        "top_songs": ["Hey Jude", "Let It Be", "Come Together"],
        "prompt_suggestions": "Hey Jude, Let It Be, or Come Together"
    },
    "parokya ni edgar": {
        "canonical": "Parokya ni Edgar",
        "top_songs": ["Harana", "Gitara", "Your Song"],
        "prompt_suggestions": "Harana, Gitara, or Your Song"
    },
    "rivermaya": {
        "canonical": "Rivermaya",
        "top_songs": ["214", "Kisapmata", "Liwanag sa Dilim"],
        "prompt_suggestions": "214, Kisapmata, or Liwanag sa Dilim"
    }
}

PENDING_MEDIA_REQUEST: Optional[Dict[str, Any]] = None
_MEDIA_LOCK = threading.Lock()
PENDING_EXPIRY_SECONDS = 35.0


def check_media_disambiguation(command_text: str) -> Dict[str, Any]:
    """
    Evaluates whether a media request requires disambiguation, resolves a pending
    disambiguation turn, or should proceed directly to playback.

    Returns dict with keys:
      - status: 'needs_disambiguation' | 'resolved' | 'direct'
      - artist: str
      - song: str
      - query: str
      - reply: str
    """
    global PENDING_MEDIA_REQUEST
    now = time.time()
    cmd = command_text.lower().strip()

    # Clean punctuation and extra spaces
    cmd_clean = re.sub(r'[^\w\s]', ' ', cmd)
    cmd_clean = re.sub(r'\s+', ' ', cmd_clean).strip()

    with _MEDIA_LOCK:
        # Check expired pending state
        if PENDING_MEDIA_REQUEST and (now - PENDING_MEDIA_REQUEST["timestamp"] > PENDING_EXPIRY_SECONDS):
            PENDING_MEDIA_REQUEST = None

        # -------------------------------------------------------------
        # CASE B: Active Follow-Up to Pending Disambiguation
        # -------------------------------------------------------------
        if PENDING_MEDIA_REQUEST:
            pending_artist = PENDING_MEDIA_REQUEST["artist"]
            canonical = PENDING_MEDIA_REQUEST.get("canonical", pending_artist)

            # Strip common conversational affirmative prefixes: "play ...", "i want ...", "how about ..."
            song_candidate = re.sub(r'^(?:play\s+|put\s+on\s+|i\s+want\s+|how\s+about\s+|can\s+you\s+play\s+|let\s+s\s+hear\s+)', '', cmd_clean).strip()
            song_candidate = re.sub(r'^(?:the\s+song\s+)', '', song_candidate).strip()

            if any(w in song_candidate for w in ["anything", "surprise me", "any", "whatever", "random", "any song"]):
                # Pick top iconic song
                chosen_song = KNOWN_ARTISTS.get(pending_artist.lower(), {}).get("top_songs", ["Mundo"])[0]
            elif song_candidate:
                chosen_song = song_candidate.title()
            else:
                chosen_song = KNOWN_ARTISTS.get(pending_artist.lower(), {}).get("top_songs", ["Mundo"])[0]

            PENDING_MEDIA_REQUEST = None

            full_query = f"{canonical} {chosen_song}"
            reply = f"Awesome choice, Boss! Playing {chosen_song} by {canonical} on YouTube right now."

            return {
                "status": "resolved",
                "artist": canonical,
                "song": chosen_song,
                "query": full_query,
                "reply": reply,
                "requires_playback": True
            }

    # -----------------------------------------------------------------
    # CASE A vs CASE C: Initial Request Check
    # -----------------------------------------------------------------
    # Strip greetings & triggers to isolate search core
    core = re.sub(r'^(?:(?:hey|hi|yo)\s+)?jessica[,\s]+', '', cmd, flags=re.IGNORECASE).strip()
    core = re.sub(r'^(?:can you\s+|please\s+)?(?:play|put on|listen to)\s+', '', core, flags=re.IGNORECASE).strip()
    core = re.sub(r'\s+(?:on youtube|in youtube|youtube|on spotify|spotify)$', '', core, flags=re.IGNORECASE).strip()
    core_clean = core.lower().strip()

    # Check against known artists
    for artist_key, info in KNOWN_ARTISTS.items():
        if artist_key in core_clean:
            canonical = info["canonical"]
            top_songs = info["top_songs"]

            # Check if any specific song was already named in this command (Case C)
            song_named = any(s.lower() in core_clean for s in top_songs)
            has_specific_by = " by " in core_clean

            if song_named or has_specific_by:
                # Case C: Both song and artist already specified
                return {
                    "status": "direct",
                    "artist": canonical,
                    "query": core,
                    "requires_playback": True
                }

            # If the user only named the artist/band, trigger Case A Disambiguation
            # e.g., "play IV of Spades on YouTube", "play eraserheads"
            with _MEDIA_LOCK:
                PENDING_MEDIA_REQUEST = {
                    "artist": artist_key,
                    "canonical": canonical,
                    "timestamp": time.time()
                }

            suggestions = info["prompt_suggestions"]
            reply = f"Sure thing, Boss! Which {canonical} song do you want me to play—maybe {suggestions}?"

            return {
                "status": "needs_disambiguation",
                "artist": canonical,
                "query": core,
                "reply": reply,
                "requires_followup": True
            }

    # Direct query (not an ambiguous known band)
    return {
        "status": "direct",
        "artist": None,
        "query": core,
        "requires_playback": True
    }


def clear_pending_media():
    global PENDING_MEDIA_REQUEST
    with _MEDIA_LOCK:
        PENDING_MEDIA_REQUEST = None


def get_pending_media() -> Optional[Dict[str, Any]]:
    global PENDING_MEDIA_REQUEST
    with _MEDIA_LOCK:
        if PENDING_MEDIA_REQUEST and (time.time() - PENDING_MEDIA_REQUEST["timestamp"] > PENDING_EXPIRY_SECONDS):
            PENDING_MEDIA_REQUEST = None
        return PENDING_MEDIA_REQUEST

