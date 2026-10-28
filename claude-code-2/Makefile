PY ?= .venv/bin/python
FF := $(shell $(PY) -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
OUT := out/Claude_Code_2x_guia_completa.mp4

.PHONY: all video audio mux preview thumb clean

all: mux

video:
	$(PY) src/render.py video

audio:
	$(PY) src/build_audio.py

mux: video audio
	$(FF) -y -hide_banner -loglevel error -i out/video_silent.mp4 -i build/mix.wav \
		-c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 \
		-c:a aac -b:a 192k -shortest -movflags +faststart $(OUT)

thumb:
	$(PY) src/render.py thumb

preview:
	$(PY) src/render.py preview 3 63 125 155 250 340 425 470

clean:
	rm -rf build out/preview_*.png out/video_silent.mp4
