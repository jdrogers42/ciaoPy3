import centroid
from matplotlib import pyplot as plt
import glob,sys,os
import numpy as np
from time import time
import centroid

image_width = 2048
fractional_spot_positions = np.arange(0.1,0.9,0.03)

#fractional_spot_positions = np.array([0.3,0.5,0.7])
spot_positions = fractional_spot_positions*image_width

border = fractional_spot_positions[0]-np.mean(np.diff(fractional_spot_positions))
spots_image = np.zeros((image_width,image_width),dtype=np.int16)

XX,YY = np.meshgrid(spot_positions,spot_positions)

sb_x_vec = XX.ravel()
sb_y_vec = YY.ravel()

valid_vec = np.ones(sb_x_vec.shape,dtype=np.int16)

sb_half_width = int(round(1/float(len(sb_x_vec))*image_width))-1
centroiding_half_width = 10

xout = np.zeros(sb_x_vec.shape)
yout = np.zeros(sb_y_vec.shape)
max_intensity = np.zeros(sb_x_vec.shape)

n_spots = len(sb_x_vec)

if False:
# generate some random blobs around the SB centers
    for spot in range(n_spots):
        for dx in range(-1,2):
            for dy in range(-1,2):
                yput,xput = int(round(sb_y_vec[spot]))+dy,int(round(sb_x_vec[spot]))+dx
                spots_image[yput,xput] = np.random.rand()*1000.0

x_spot_location = []
y_spot_location = []


for spot in range(n_spots):
    dx = np.random.randint(-1,2)
    dy = np.random.randint(-1,2)
    yput,xput = int(round(sb_y_vec[spot]))+dy,int(round(sb_x_vec[spot]))+dx
    spots_image[yput,xput] = 1000.0
    x_spot_location.append(xput)
    y_spot_location.append(yput)

x_spot_location = np.array(x_spot_location)
y_spot_location = np.array(y_spot_location)

def fast_centroids(spots_image,sb_x_vec,sb_y_vec,sb_half_width,centroiding_half_width,verbose=False):
    n_spots = len(sb_x_vec)
    x_out = np.zeros(n_spots)
    y_out = np.zeros(n_spots)
    for spot_index in range(n_spots):
        current_max = -2**16+1
        
        x1 = int(round(sb_x_vec[spot_index]-sb_half_width))
        x2 = int(round(sb_x_vec[spot_index]+sb_half_width))
        y1 = int(round(sb_y_vec[spot_index]-sb_half_width))
        y2 = int(round(sb_y_vec[spot_index]+sb_half_width))

        if verbose:
            print 'python A',spot_index,x1,x2,y1,y2
        
        for y in range(y1,y2+1):
            for x in range(x1,x2+1):
                pixel = spots_image[y,x]
                if pixel>current_max:
                    current_max = pixel
                    max_y = y
                    max_x = x
                    
        x1 = int(round(max_x-centroiding_half_width))
        x2 = int(round(max_x+centroiding_half_width))
        y1 = int(round(max_y-centroiding_half_width))
        y2 = int(round(max_y+centroiding_half_width))

        if verbose:
            print 'python B',spot_index,x1,x2,y1,y2
        
        xnum = 0.0
        ynum = 0.0
        denom = 0.0

        for y in range(y1,y2+1):
            for x in range(x1,x2+1):
                pixel = spots_image[y,x]
                xnum = xnum + pixel*x
                ynum = ynum + pixel*y
                denom = denom + pixel

        x_out[spot_index] = xnum/denom
        y_out[spot_index] = ynum/denom

    return x_out,y_out

centroid.fast_centroids(spots_image,sb_x_vec,sb_y_vec,sb_half_width,centroiding_half_width,xout,yout,max_intensity,valid_vec,0,1)
pxout,pyout = fast_centroids(spots_image,sb_x_vec,sb_y_vec,sb_half_width,centroiding_half_width)

python_cython_err = (xout-pxout).tolist()+(yout-pyout).tolist()
if any(python_cython_err):
    sys.exit('Error between Cython centroiding and Python centroiding. Please fix.')
else:
    print 'Cython centroid centers of mass match pure Python calculations.'
    
cython_ground_truth_err = (xout-x_spot_location).tolist()+(yout-y_spot_location).tolist()
if any(cython_ground_truth_err):
    sys.exit('Error between Cython centroiding and ground truth. Please fix.')
else:
    print 'Cython centroid centers of mass match ground truth.'

N = 1000
t0 = time()
for k in range(N):
    centroid.fast_centroids(spots_image,sb_x_vec,sb_y_vec,sb_half_width,centroiding_half_width,xout,yout,max_intensity,valid_vec,0,1)

t_total = time()-t0
t_iteration = t_total/float(N)
fps = 1.0/t_iteration

print '%d spots, %d iterations, total time %0.1f, iteration time %0.1e, fps %0.1f'%(n_spots,N,t_total,t_iteration,fps)
