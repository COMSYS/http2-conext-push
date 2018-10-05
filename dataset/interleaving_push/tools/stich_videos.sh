set -x
ORDNER_A=$1
ORDNER_B=$2

ffmpeg \
	-i $ORDNER_A/push/video/1.mp4 \
	-i $ORDNER_A/push/video/2.mp4 \
	-i $ORDNER_A/push/video/3.mp4 \
	-i $ORDNER_A/push/video/4.mp4 \
	-i $ORDNER_A/push/video/5.mp4 \
	-i $ORDNER_A/push/video/6.mp4 \
	-i $ORDNER_A/push/video/7.mp4 \
	-i $ORDNER_A/push/video/8.mp4 \
	-i $ORDNER_A/push/video/9.mp4 \
	-i $ORDNER_A/push/video/10.mp4 \
	-i $ORDNER_B/push/video/1.mp4 \
	-i $ORDNER_B/push/video/2.mp4 \
	-i $ORDNER_B/push/video/3.mp4 \
	-i $ORDNER_B/push/video/4.mp4 \
	-i $ORDNER_B/push/video/5.mp4 \
	-i $ORDNER_B/push/video/6.mp4 \
	-i $ORDNER_B/push/video/7.mp4 \
	-i $ORDNER_B/push/video/8.mp4 \
	-i $ORDNER_B/push/video/9.mp4 \
	-i $ORDNER_B/push/video/10.mp4 \
	-filter_complex " nullsrc=size=640x2400 [base];
		[0:v] setpts=PTS-STARTPTS, scale=320x240 [left1];
		[1:v] setpts=PTS-STARTPTS, scale=320x240 [left2];
		[2:v] setpts=PTS-STARTPTS, scale=320x240 [left3];
		[3:v] setpts=PTS-STARTPTS, scale=320x240 [left4];
		[4:v] setpts=PTS-STARTPTS, scale=320x240 [left5];
		[5:v] setpts=PTS-STARTPTS, scale=320x240 [left6];
		[6:v] setpts=PTS-STARTPTS, scale=320x240 [left7];
		[7:v] setpts=PTS-STARTPTS, scale=320x240 [left8];
		[8:v] setpts=PTS-STARTPTS, scale=320x240 [left9];
		[9:v] setpts=PTS-STARTPTS, scale=320x240 [left10];
		[10:v] setpts=PTS-STARTPTS, scale=320x240 [right1];
		[11:v] setpts=PTS-STARTPTS, scale=320x240 [right2];
		[12:v] setpts=PTS-STARTPTS, scale=320x240 [right3];
		[13:v] setpts=PTS-STARTPTS, scale=320x240 [right4];
		[14:v] setpts=PTS-STARTPTS, scale=320x240 [right5];
		[15:v] setpts=PTS-STARTPTS, scale=320x240 [right6];
		[16:v] setpts=PTS-STARTPTS, scale=320x240 [right7];
		[17:v] setpts=PTS-STARTPTS, scale=320x240 [right8];
		[18:v] setpts=PTS-STARTPTS, scale=320x240 [right9];
		[19:v] setpts=PTS-STARTPTS, scale=320x240 [right10];
		[base][left1] overlay=shortest=1 [tmpleft1];
		[tmpleft1][left2] overlay=shortest=1:y=240 [tmpleft2];
		[tmpleft2][left3] overlay=shortest=1:y=480 [tmpleft3];
		[tmpleft3][left4] overlay=shortest=1:y=720 [tmpleft4];
		[tmpleft4][left5] overlay=shortest=1:y=960 [tmpleft5];
		[tmpleft5][left6] overlay=shortest=1:y=1200 [tmpleft6];
		[tmpleft6][left7] overlay=shortest=1:y=1440 [tmpleft7];
		[tmpleft7][left8] overlay=shortest=1:y=1680 [tmpleft8];
		[tmpleft8][left9] overlay=shortest=1:y=1920 [tmpleft9];
		[tmpleft9][left10] overlay=shortest=1:y=2160 [tmpright1];
		[tmpright1][right1] overlay=shortest=1:x=320:y=0 [tmpright2];
		[tmpright2][right2] overlay=shortest=1:x=320:y=240 [tmpright3];
		[tmpright3][right3] overlay=shortest=1:x=320:y=480 [tmpright4];
		[tmpright4][right4] overlay=shortest=1:x=320:y=720 [tmpright5];
		[tmpright5][right5] overlay=shortest=1:x=320:y=960 [tmpright6];
		[tmpright6][right6] overlay=shortest=1:x=320:y=1200 [tmpright7];
		[tmpright7][right7] overlay=shortest=1:x=320:y=1440 [tmpright8];
		[tmpright8][right8] overlay=shortest=1:x=320:y=1680 [tmpright9];
		[tmpright9][right9] overlay=shortest=1:x=320:y=1920 [tmpright10];
		[tmpright10][right10] overlay=shortest=1:x=320:y=2160
	" -c:v libx264 output.mkv  
