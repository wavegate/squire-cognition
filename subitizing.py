import numpy as np 
import matplotlib.pyplot as plt

# Fixing random state for reproducibility
#np.random.seed(19680801)

for i in range(10):
	N = np.random.random_integers(1,9)
	x = np.random.rand(N)
	y = np.random.rand(N)
	#colors = np.random.rand(N)
	colors = 'k'
	#area = (30 * np.random.rand(N))**2  # 0 to 15 point radii
	area = 20

	plt.scatter(x, y, s=area, c=colors)
	plt.axis([0, 1, 0, 1])
	plt.axis('scaled')

	plt.axis('off')

	plt.savefig('app/static/img/subitizing/{}.png'.format(i))

	plt.clf()