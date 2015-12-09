from fr_on_premise.stream_video import StreamVideo


s = StreamVideo('tests/obama.mp4', 'ws://localhost:8000/recognize');
s.stream()