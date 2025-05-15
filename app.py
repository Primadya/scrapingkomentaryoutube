import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import re

# Konfigurasi halaman
st.set_page_config(page_title="YouTube Comment Scraper", page_icon="📺", layout="centered")

# API Key YouTube kamu
API_KEY = st.secrets["YOUTUBE_API_KEY"]

# Fungsi ekstrak Video ID
def extract_video_id(url):
    pattern = r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

# Fungsi scraping komentar
def get_comments(api_key, video_id, max_comments):
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )
    response = request.execute()

    while request and len(comments) < max_comments:
        for item in response['items']:
            snippet = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'Author': snippet['authorDisplayName'],
                'Comment': snippet['textDisplay'],
                'PublishedAt': snippet['publishedAt']
            })
            if len(comments) >= max_comments:
                break

        if 'nextPageToken' in response:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=response['nextPageToken'],
                textFormat="plainText"
            )
            response = request.execute()
        else:
            break

    return comments

# === UI Streamlit ===
st.title("📺 YouTube Comment Scraper")
st.markdown("Masukkan link video YouTube dan jumlah komentar yang ingin diambil.")

# Input pengguna
video_url = st.text_input("🔗 Masukkan URL Video YouTube")
jumlah = st.number_input("📝 Jumlah komentar yang ingin diambil", min_value=1, max_value=1000, step=10)

# Proses saat user klik tombol
if st.button("🚀 Ambil Komentar"):
    video_id = extract_video_id(video_url)
    
    if not video_id:
        st.error("❌ URL tidak valid. Cek kembali.")
    else:
        # Tampilkan thumbnail / embed video
        st.video(f"https://www.youtube.com/watch?v={video_id}")
        st.info("⏳ Sedang mengambil komentar...")

        # Scraping komentar
        comments_data = get_comments(API_KEY, video_id, jumlah)
        df = pd.DataFrame(comments_data)

        # Tampilkan hasil
        st.success(f"✅ Berhasil mengambil {len(df)} komentar.")
        st.dataframe(df)

        # Tombol unduh CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Komentar sebagai CSV",
            data=csv,
            file_name=f'youtube_comments_{video_id}.csv',
            mime='text/csv',
        )
