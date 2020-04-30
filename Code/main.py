"""
Visual Odomotry SFM

Authors:
Nalin Das (nalindas9@gmail.com)
Graduate Student pursuing Masters in Robotics,
University of Maryland, College Park
"""
import numpy as np
import glob
import cv2
import ReadCameraModel
import UndistortImage
from matplotlib import pyplot as plt
from cv2 import xfeatures2d 

# Specify the path for all the video frames here
IMAGES_PATH = "/home/nalindas9/Documents/courses/spring_2020/enpm673-perception/datasets/Oxford_dataset/stereo/centre"
# Specify the path for the camera parameters
MODELS_PATH = "/home/nalindas9/Documents/courses/spring_2020/enpm673-perception/datasets/Oxford_dataset/model"

# Function to find point correspondences between two successive frames
def featurematch(frame1, frame2):
  # Using SIFT to find keypoints and descriptors
  orb = xfeatures2d.SIFT_create()
  kp1, des1 = orb.detectAndCompute(frame1,None)
  kp2, des2 = orb.detectAndCompute(frame2,None)
  flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
  matches = flann.knnMatch(des1, des2, 2)
  left_pts = list()
  right_pts = list()
  
  # Need to draw only good matches, so create a mask
  matchesMask = [[0,0] for i in range(len(matches))]
  # Ratio criteria according to Lowe's paper
  for i, (m, n) in enumerate(matches):
    if m.distance < 0.75 * n.distance:
      left_pts.append(kp2[m.trainIdx].pt)
      right_pts.append(kp1[m.queryIdx].pt)
      matchesMask[i]=[1,0]
  
  draw_params = dict(matchColor = (0,255,0),
                     singlePointColor = (255,0,0),
                     matchesMask = matchesMask,
                     flags = 0)

  img3 = cv2.drawMatchesKnn(frame1,kp1,frame2,kp2,matches,None,**draw_params)

  plt.imshow(img3,),plt.show()
  left_pts = np.array(left_pts)
  right_pts = np.array(right_pts)
  return left_pts, right_pts
  
# Function to compute fundamental matrix
def fundamental_matrix(pts1, pts2):
  x1 = pts1[:, 0]    
  y1 = pts1[:, 1]
  x2 = pts2[:, 0]
  y2 = pts2[:, 1]
  n = x1.shape[0]
  A = np.zeros((n, 9))
  # Find A matrix
  for i in range(0,n):
    A[i] = [x1[i] * x2[i], x1[i] * y2[i], x1[i], y1[i] * x2[i], y1[i] * y2[i], y1[i], x2[i], y2[i], 1]
  print('A is:', A)
  # Compute the F matrix by calculating the SVD
  U, S, V = np.linalg.svd(A)
  print('U: {:}, S: {:}, V: {:}'.format(U, S, V))
  F = V[:, -1].reshape(3,3)
  print('F:', F)
  
# Main Function
def main():
  # Extract the camera params
  fx, fy, cx, cy, G_camera_image, LUT = ReadCameraModel.ReadCameraModel(MODELS_PATH)
  print('The extracted camera parameters are fx = {:}, fy = {:}, cx = {:}, cy = {:}, G_camera_image = {:}, LUT = {:}:'.format(fx, fy, cx, cy, G_camera_image, LUT))
  successive_frames = []
  itr = 0
  # Iterating through all frames in the video and doing some preprocessing
  for frame in sorted(glob.glob(IMAGES_PATH + "/*")):
    print('Image:', frame.split("centre/", 1)[1])
    img = cv2.imread(frame,0)
    img = cv2.cvtColor(img, cv2.COLOR_BayerGR2BGR)
    img = UndistortImage.UndistortImage(img,LUT)
    img = cv2.resize(img, (0,0),fx=0.5,fy=0.5)
    successive_frames.append(img)
    if itr != 0 and itr%2 == 0:
      # Get point matches 
      left_pts, right_pts = featurematch(successive_frames[0], successive_frames[1])
      fundamental_matrix(left_pts[0:8], right_pts[0:8])
      successive_frames = []        
    cv2.imshow('Color image', img)
    cv2.waitKey(0)
    itr = itr + 1
    
if __name__ == '__main__':
  main()
