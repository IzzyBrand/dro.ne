import numpy as np
import math
import cv2
from cv2 import aruco

aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_50) # use the 5x5 dictionary of 50 markers
markerEdgeLength = 7.391 # the length of the edge of a marker. this is in cm for now

# RMS: 0.279129288995
# cameraMatrix = np.array([
#  [  1.03931729e+03,   0.00000000e+00,   5.35435602e+02],
#  [  0.00000000e+00,   1.04185081e+03,   3.40268819e+02],
#  [  0.00000000e+00,   0.00000000e+00,   1.00000000e+00]])
# distCoeffs = np.array([0.11964666, -0.32592062, -0.01000587, -0.00188305, 0.37782278])

# RMS: 0.30710868491
cameraMatrix = np.array([
 [  1.04304578e+03,   0.00000000e+00,   5.46544858e+02],
 [  0.00000000e+00,   1.04432128e+03,  3.46273512e+02],
 [  0.00000000e+00,   0.00000000e+00,  1.00000000e+00]])
distCoeffs =  np.array([0.11330149, -0.27730294, -0.00748054,  0.00234142,  0.28207847])

# generate aruco markers and save them in the local dir
for i in range(5):
	a = aruco.drawMarker(aruco_dict, i, sidePixels = 200, borderBits=1)
	cv2.imwrite('aruco{}.jpg'.format(i), a)

cv2.namedWindow("preview")	# created a window named preview
vc = cv2.VideoCapture(0)	# set up the video capture from the webcam

while True:
	rval, frame = vc.read()	# read a new frame from the webcam. 
	if rval:	# if we got a new frame
		corners, ids, regjected = aruco.detectMarkers(frame, aruco_dict)	# run aruco on the frame
		detected_frame = aruco.drawDetectedMarkers(frame, corners, ids)		# draw the boxes on the detected markers
		rvecs, tvecs = aruco.estimatePoseSingleMarkers(corners, markerEdgeLength, cameraMatrix, distCoeffs)

		if rvecs != None:
			rot = cv2.Rodrigues(rvecs)[0]	# get the rotation matrix
			inv_rot = np.transpose(rot)		# invert it
			new_translation = np.matmul(inv_rot, np.multiply(tvecs[0][0],-1.0))	# apply it to the translation matrix
			print new_translation

			axis_frame = aruco.drawAxis(frame, cameraMatrix, distCoeffs, rvecs, tvecs, 7.39)
			cv2.imshow("preview", axis_frame)  # display the frame

		else: 
			cv2.imshow("preview", detected_frame)							# display the frame

	if cv2.waitKey(1) & 0xFF == ord('q'): break	# allow the user to press q on the window to exit

vc.release()	# close the camera stream