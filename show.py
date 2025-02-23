import sys
import numpy as np
import matplotlib.pyplot as pp
loaded=np.load(sys.argv[1],allow_pickle=True)
# pp.imshow(loaded['original_teeth'])
# pp.show()
masks=loaded['y']
names=loaded['y']
print(masks.shape)
#quit()
fig,axs=pp.subplots(9,8,figsize=(20,20))
for i in range(masks.shape[2]):
 axs[i//8,i%8].imshow(masks[:,:,i])
# axs[i//8,i%8].set_title(names[i])

axs[8,7].imshow(loaded['x'])

for i in range(72):
 axs[i//8,i%8].set_xticks([])
 axs[i//8,i%8].set_yticks([])
pp.savefig('show1.jpg')

 