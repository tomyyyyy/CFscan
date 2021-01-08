import time
from tqdm import tqdm
from tqdm import tnrange, tqdm_notebook
from collections import OrderedDict

for i in tqdm(range(5), desc='Total', ncols=100, ascii=' =', bar_format='{l_bar}{bar}|'):
    for i in tqdm(range(100), desc='Progress', ncols=100, ascii=' ='):
        # time.sleep(0.01)
        pass
    for i in tqdm(range(100), desc='Progress', ncols=100, ascii=' ='):
        time.sleep(0.01)
    
