import openpiv.tools
import openpiv.process
import openpiv.scaling
import openpiv.validation
import openpiv.filters
import numpy as np
import pandas as pd
import cv2



file_a = '/home/dbath/Desktop/dots_imgs/frame-000048.png'
file_b = '/home/dbath/Desktop/dots_imgs/frame-000049.png'
save_dir = '/home/dbath/Documents/PIV/output/'
first_file = 48

def PIVIT(args):
	file_a, _, counter = args
	pre, post = file_a.rsplit('/',1)
	num = int(post.split('frame-')[-1].split('.png')[0])
	file_b =  pre + '/frame-%06d.png'%(num+1)
	frame_a  = openpiv.tools.imread(file_a).astype(np.int32)[:,289:1152]
	frame_b  = openpiv.tools.imread(file_b).astype(np.int32)[:,289:1152]
	u, v, sig2noise = openpiv.process.extended_search_area_piv( frame_a, frame_b, window_size=24, overlap=12, dt=0.02, search_area_size=64, sig2noise_method='peak2peak' )
	x, y = openpiv.process.get_coordinates( image_size=frame_a.shape, window_size=24, overlap=12 )
	
	u, v, mask = openpiv.validation.sig2noise_val( u, v, sig2noise, threshold = 1.3 )
	u, v = openpiv.filters.replace_outliers( u, v, method='localmean', kernel_size=2)
	x, y, u, v = openpiv.scaling.uniform(x, y, u, v, scaling_factor = 96.52 )

	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.quiver(x,y,u,v)
	ax.set_axis_off()
	plt.savefig(save_dir + 'img_%06d.png'%(num - first_file))
	#openpiv.tools.save(x, y, u, v, 'exp1_001.txt' )
	return x,y,u,v
	
task = openpiv.tools.Multiprocesser(data_dir='/home/dbath/Desktop/dots_imgs', pattern_a='frame-*.png', pattern_b='frame-*.png')
task.run( func = PIVIT, n_cpus=8 )
