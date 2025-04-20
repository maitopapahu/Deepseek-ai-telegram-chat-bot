# youtube.py
import yt_dlp

def search_youtube(query):
    ydl_opts = {'quiet': True, 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            return f"https://www.youtube.com/watch?v={info['id']}"
    except Exception as e:
        print("YouTube search error:", e)
        return None
      
