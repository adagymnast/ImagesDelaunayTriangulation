import numpy as np
import cv2
import random
import scipy.spatial
import matplotlib.pyplot as plt
from tqdm import trange

# CHOOSE SIZE OF IMAGE (SUBSET OF IMAGE), IF -1 THEN WHOLE IMAGE
SIZE_X = -1
SIZE_Y = -1

# READ IMAGE
path = r'C:\Users\Adela\Desktop\tablo.png'
img = cv2.imread(path)[:SIZE_X, :SIZE_Y]
img_points = cv2.imread(path)[:SIZE_X, :SIZE_Y]

# CHOOSE THE METHOD: BASED ON SIMILARITY OR SOBEL: Similarity is better but slower
# method = 'Sobel'
method = 'Similarity'

# RANDOM SEED
random.seed(0)
np.random.seed(0)

# CONSTANTS
# Density of pixels: Every PART's pixel is a chosen point
PART = 50
STEP = 250 # step should be changed based on PART
ROWS, COLS, CHANNELS = img.shape
SIZE = ROWS * COLS
KERNEL_SIZE = 5
PIXELS = KERNEL_SIZE ** 2
S = (KERNEL_SIZE - 1) // 2
COUNT = int(SIZE/PART)

# POINTS
all_points = np.array([[[x, y] for x in range(COLS)] for y in range(ROWS)]).reshape(SIZE, 2)

# COUNT DIFFERENCES BASED ON METHOD
if method == 'Similarity':
    differences = np.zeros((ROWS, COLS))
    for y in range(S, ROWS - S):
        for x in range(S, COLS - S):
            average = img[y - S: y + S + 1, x - S: x + S + 1].reshape(KERNEL_SIZE ** 2, CHANNELS).mean(axis=0)
            differences[y, x] = \
                np.sum(np.sqrt(np.sum(np.power(average - img[y - S: y + S + 1, x - S: x + S + 1], 2), axis=2)))

elif method == 'Sobel':
    sobel_x = cv2.Sobel(img,cv2.CV_64F, 1, 0, ksize=3)
    d = np.abs(sobel_x)
    d = d-d.min()
    d = d/d.max()*255
    d = d.astype(np.uint8)
    differences = cv2.cvtColor(d, cv2.COLOR_BGR2GRAY)

# CHOOSE POINTS WITH PROBABILITIES DISTRIBUTED ACCORDING TO DIFFERENCES
probabilities = differences.reshape(-1)
indices = np.random.choice(np.arange(all_points.shape[0]), size=COUNT, replace=False, p=probabilities/probabilities.sum())
for i in range(COUNT):
    cv2.circle(img_points, tuple(all_points[indices[i]]), 3, [255, 255, 0], -1)
points_without_corners = np.array([tuple(all_points[indices[i]]) for i in range(COUNT)])
corners = np.array([[0, 0], [ROWS-1, 0], [0, COLS-1], [ROWS-1, COLS-1]])
points = np.concatenate((points_without_corners, corners))

# CREATE DELAUNAY TRIANGULATION
triangulation = scipy.spatial.Delaunay(points)
result = np.zeros(img.shape)

# CREATE VIDEO
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output_tablo.mp4', fourcc, 25.0, (img.shape[1], img.shape[0]), True)

for i in trange(triangulation.simplices.shape[0]):
    triangles_indices = triangulation.simplices[i]
    mask = np.zeros(img.shape[:2])
    cv2.fillConvexPoly(mask, np.array(points[triangles_indices], np.int32).reshape((-1, 1, 2)), 1)
    mean = cv2.mean(img, mask.astype(np.uint8))
    cv2.fillConvexPoly(result, np.array(points[triangles_indices], np.int32).reshape((-1, 1, 2)), mean[:3])
    if i % ((triangulation.simplices.shape[0])//STEP) == 0:
        out.write(result.astype(np.uint8))

for _ in range(50):
    out.write(result.astype(np.uint8))
out.release()

# Show original image, equalized histogram distances image and points image
cv2.imshow('Original_image', img)
cv2.imshow('image2', differences/differences.max())
cv2.imshow('image3', cv2.equalizeHist((differences/differences.max() * 255).astype(np.uint8)))
cv2.imshow('Points_image', img_points)
cv2.imshow('Result_image', result.astype(np.uint8))
cv2.waitKey(0)