# remove overlay boxes
# all these model has the general problem, and must remove overlay boxes

import numpy as np

#get 2bbox IoU
def bb_iou(x1, y1, w1, h1, x2, y2, w2, h2):
    '''
    说明：图像中，从左往右是 x 轴（0~无穷大），从上往下是 y 轴（0~无穷大），从左往右是宽度 w ，从上往下是高度 h
    :param x1: 第一个框的左上角 x 坐标
    :param y1: 第一个框的左上角 y 坐标
    :param w1: 第一幅图中的检测框的宽度
    :param h1: 第一幅图中的检测框的高度
    :param x2: 第二个框的左上角 x 坐标
    :param y2:
    :param w2:
    :param h2:
    :return: 两个如果有交集则返回重叠度 IOU, 如果没有交集则返回 0
    '''
    if(x1>x2+w2):
        return 0
    if(y1>y2+h2):
        return 0
    if(x1+w1<x2):
        return 0
    if(y1+h1<y2):
        return 0
    colInt = abs(min(x1 +w1 ,x2+w2) - max(x1, x2))
    rowInt = abs(min(y1 + h1, y2 +h2) - max(y1, y2))
    overlap_area = colInt * rowInt
    area1 = w1 * h1
    area2 = w2 * h2
    return overlap_area / (area1 + area2 - overlap_area)



#get min-bbox over %
#return [n,overide %]
# n=0(no intersect),1:first bbox area is small, 2:second bbox area is small
def bb_minbbox_over(box1,box2):
    x1,y1,x2,y2 = box1
    x3,y3,x4,y4 = box2
    #print('box1 vs box2 = {} : {}'.format(box1,box2))
    
    if(x2<x3 or x4<x1):
        return 0,1
    if(y2<y3 or y4<y1):
        return 0,2
    
    colInt = abs(min(x2 ,x4) - max(x1, x3))
    rowInt = abs(min(y2, y4) - max(y1, y3))
    overlap_area = colInt * rowInt
    area1 = abs((x2-x1)*(y2-y1))
    area2 = abs((x4-x3)*(y4-y3))
    if area1<area2:
        return 1, overlap_area/area1
    else:
        return 2, overlap_area/area2

### find and remove overlap bbox,and change type of big bbox to mc if has
def remove_overlap_bbox(bbox,bclasses,iou=0.5):
    #print(bbox)
    #print(bclasses)
    rm_bbox=[]
    for i in range(len(bbox)-1):
        for j in range(i+1,len(bbox)):
            overate = bb_minbbox_over(bbox[i],bbox[j])
            if overate[0]==1 and overate[1]>iou: #bbox[i] is small
                if bclasses[i]==1 and bclasses[j]==0: # bclasses 1 is 'mc', 0 is 'lymph':
                   bclasses[j]=1
                rm_bbox.append(i)
            elif overate[0]==2 and overate[1]>iou: #bbox[j] is small
                if bclasses[i]==0 and bclasses[j]==1: # bclasses 1 is 'mc', 0 is 'lymph':
                   bclasses[i]=1
                rm_bbox.append(j)

    if len(rm_bbox)>0:
        bbox = np.delete(bbox,rm_bbox,axis=0)
        bclasses = np.delete(bclasses,rm_bbox)

    return bbox,bclasses


### find and remove overlap lymph and mc , remove lymph box
def remove_overlap_type(data1,iou=0.5):
    bbox = []
    bclasses=[]
    for i in data1:
        bbox.append([i['x1'],i['y1'],i['x2'],i['y2']])
        bclasses.append(i['tp'])

    rm_bbox=[]
    for i in range(len(bbox)-1):
        for j in range(i+1,len(bbox)):
            overate = bb_minbbox_over(bbox[i],bbox[j])
            if overate[0]==1 and overate[1]>iou: #bbox[i] is small
                if bclasses[i]=='mc' and bclasses[j]=='lymph':
                    rm_bbox.append(j)
                    print(f"rm {bbox[j]}, keep {bbox[i]}")
            elif overate[0]==2 and overate[1]>iou: #bbox[j] is small
                if bclasses[i]=='lymph' and bclasses[j]=='mc':
                    rm_bbox.append(i)
                    print(f"rm {bbox[i]}, keep {bbox[j]}")

    if len(rm_bbox)>0:
        data1 = np.delete(data1,rm_bbox,axis=0)
    return data1
