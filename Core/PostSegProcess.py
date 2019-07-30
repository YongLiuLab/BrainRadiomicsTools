import numpy as np
from skimage import measure
def postSegProcess(seg):
    data = np.zeros((182, 218, 182))
    label = seg.copy()
    label[label > 0] = 1
    regions = measure.label(label)
    for i in range(0, np.max(regions.flatten()) + 1):
        if (np.size(np.where(regions == i)) > 300):
            data[np.where(regions == i)] = 1
    del label
    # save_vol(data, files[-(case_idx + 1)], "results/2" + model_name)
    seg = data * seg
    del data
    seg_data = seg.copy()
    seg_data[seg_data > 0] = 1

    return seg_data