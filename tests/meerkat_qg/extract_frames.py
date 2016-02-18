import cv2




videofiles = ['video000.avi', 'video001.avi', 'video002.avi']
folders = ['frames/renan/', 'frames/guilherme/', 'frames/gfuhr/']

FRAME_STEP = 14

for vid, fol in zip(videofiles, folders):
	print(vid,fol)
	vidfile = cv2.VideoCapture(vid)

	ret, frame = vidfile.read()
	frame_number = 1
	while ret:
		cv2.imwrite(fol+'{0:02d}.png'.format(frame_number), frame)
		print(frame_number)
		frame_number = frame_number + 1
		for x in range(FRAME_STEP-1): vidfile.grab()
		ret, frame = vidfile.read()
	
