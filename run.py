from fr_on_premise.stream_video import StreamVideo


s = StreamVideo('/Users/gfuhr/meerkat/codes/fr_on_premise/tests/obama_noaudio.mp4', 'ws://localhost:4444/echo?api_key=d4498a41d58519da0a4514a40a5d8e8c');
# s = StreamVideo('http://admin:gremio83@192.168.0.52/video/mjpg.cgi?.mjpeg', 'ws://localhost:4444/echo?api_key=d4498a41d58519da0a4514a40a5d8e8c');

s.stream()