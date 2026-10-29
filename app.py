import streamlit as st
import subprocess
import os
from faster_whisper import WhisperModel

st.set_page_config(page_title="Auto Subtitle Video", page_icon="🎬")
st.title("🎬 Auto-Subtitle Video Gratis")
st.write("Upload video, dan AI akan otomatis menempelkan teks langsung ke dalam videomu.")

@st.cache_resource
def load_model():
    return WhisperModel("small", device="cpu", compute_type="int8")

model = load_model()

def format_timestamp(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

uploaded_file = st.file_uploader("Pilih file video (.mp4, .mov)", type=["mp4", "mov"])

if uploaded_file is not None:
    input_video = "input_temp.mp4"
    with open(input_video, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.video(input_video)
    
    if st.button("🚀 Buat & Tempel Subtitle Sekarang"):
        with st.spinner("1/2 Sedang mendengarkan suara dan membuat teks (AI)..."):
            segments, _ = model.transcribe(input_video, vad_filter=True)
            
            srt_filename = "subtitles.srt"
            with open(srt_filename, "w", encoding="utf-8") as srt_file:
                for i, segment in enumerate(segments, start=1):
                    start = format_timestamp(segment.start)
                    end = format_timestamp(segment.end)
                    text = segment.text.strip()
                    srt_file.write(f"{i}\n{start} --> {end}\n{text}\n\n")
        
        with st.spinner("2/2 Sedang menempelkan teks ke dalam video..."):
            output_video = "video_bersubtitle.mp4"
            if os.path.exists(output_video):
                os.remove(output_video)
                
            style = "Fontsize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,MarginV=25"
            cmd = [
                "ffmpeg", "-y", "-i", input_video,
                "-vf", f"subtitles={srt_filename}:force_style='{style}'",
                "-c:a", "copy", output_video
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        st.success("✅ Selesai! Silakan tonton atau download videomu di bawah ini:")
        st.video(output_video)
        
        with open(output_video, "rb") as file:
            st.download_button(
                label="⬇️ Download Video Ber-subtitle",
                data=file,
                file_name="hasil_subtitle.mp4",
                mime="video/mp4"
            )
