PY ?= .venv/bin/python
FF := $(shell $(PY) -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
OUT := out/GP_Estados_Unidos_2026_Clasificacion.mp4

.PHONY: all audio video mux preview clean

all: mux

audio:
	$(PY) src/build_audio.py

video:
	$(PY) src/render.py video

mux: video audio
	$(FF) -y -hide_banner -loglevel error -i out/video_silent.mp4 -i build/mix.wav \
		-c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 \
		-c:a aac -b:a 192k -shortest -movflags +faststart $(OUT)

preview:
	$(PY) src/render.py preview 3.6 9.5 15.5 21.0 25.4 29.0

clean:
	rm -rf build out/preview_*.png out/video_silent.mp4
