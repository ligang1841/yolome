"""
    predict ca
    QC: mark and unmark
        1 keep only mark-image, 200 valid image
        2 sort leveled image and with count ch numbers
        2.1 1st queue:level 0,1,2
        2.2 2nd queue: 3,4 level
        2.3 give up others
    Predict:
        1 predict 1st queue
        2 predict 2nd queue
    report:
        ab(dic,trc,r) = dic + 2xtrc +r
        f,min,ar,(ace = f+min+ar)
        染色体畸变率(Chromosome aberration rate)： ab / images

"""

from ultralytics import YOLO
import cv2
import os
from glob import glob
import argparse
from report_ca_xml import *
import time
import celltools

# ====== config ===============================================================
# defind rect colour for test
keep_label = ["dic", "f1", "min", "f", "r", "nr", "f2"]
colour=[(255,0,0),(0,0,220),(0,0,200),(0,0,220),(200,0,0),(0,0,200),(0,0,220)]
#  png or jpg, the better is jpg
EXT='png'
level_good=['a','b','c']
level_general=['e']
level_bad=['f','g']

# limit images, valid >= 200
limit=300
model_count = 'weights/last_count.pt'
model_mark = 'weights/last_level.ph'
# 46-4 ~ 46+4 in general
ch_range=[40,52]
std_axis=125.9,36.7,160,13.5

# =============================================================================

# real predict for given-one-image
def predict(chosen_model, img, classes=[], conf=0.5):
    if classes:
        results = chosen_model.predict(img, classes=classes, conf=conf)
    else:
        results = chosen_model.predict(img, conf=conf)

    # will be yolo-result, include type,score
    return results

# test mark-level is 0? 1? ...
# None means ummarked
def predict_level(chosen_model, img, conf=0.5):
    results = predict(chosen_model, img, [], conf=conf)
    boxes = 0
    tp = None
    for result in results:
        for box in result.boxes:
            boxes += len(result.boxes)
            tp = result.names[int(box.cls[0])]

    if boxes == 1:
        return tp
    else:
        return None


# count ch in one image
# a good trained pt-lib, will be +1 or -1 in error
def predict_count(chosen_model, img, conf=0.5): 
    results = predict(chosen_model, img, [], conf=conf)
    count = 0
    tp = 0
    for result in results:
        count += len(result.boxes)
    return count


# predict this not bad image
def predict_and_detect(chosen_model, img, classes=[], conf=0.5):
    results = predict(chosen_model, img, classes, conf=conf)
    data1 = []

    for result in results:
        for box in result.boxes:
            tp = result.names[int(box.cls[0])]

            if tp=='f1':
                tp = 'min'

            if tp not in keep_label:
                continue
            data1.append({'x1':int(box.xyxy[0][0]),
                          'y1':int(box.xyxy[0][1]),
                          'x2':int(box.xyxy[0][2]),
                          'y2':int(box.xyxy[0][3]),
                          'tp':tp,
                        })
    return data1


# predict work flow
# all images in case/xy dir:
# 1 QC: mark / level test
# 2 count: count dc numbers
# if QC and count is valid, then predict it
# 3 predict if this is a good image
# 4 create report
def predict_report(model,case_dir):
    cmodel = YOLO(model_count)
    mmodel = YOLO(model_mark)

    # report init
    roi_root = create_roi('new_one')
    report_root = create_report()
   
    bar_code = os.path.basename(case_dir) 
    baseinfo_node = {
        'pname': 'new-ca',
        'pid': 'p0000',
        'hid': 'c345',    # Hospital number
        'bid': '',          #病床号
        'dept': '体检中心',
        'bar_code': bar_code,
        'app_doctor':'',
        'app_time':'',
        'sampling_time':'',
        'test_item': '全血',  #标本类型
        'age': '41',
        'sex': '1'  #性别 1：男， 0：女
    }
    # add to xml
    add_report_baseinfo(report_root, baseinfo_node)
    add_report_aerial(report_root)

    # ---------- predict all images ----------
    imgs = glob(case_dir + f'/xy/*.{EXT}')
    count_img = 0
    c_tp={}
    for c in keep_label:
        c_tp[c] = 0

    for iname in imgs:
        img = cv2.imread(iname)

        # test QC mark
        # QC test
        qc = predict_level(mmodel, img)
        if qc is not None:
            if qc in level_bad:
                continue
        else:
            continue

        # test ch count
        ch_num = predict_count(cmodel,img)
        if ch_num<ch_range[0] or ch_num>ch_range[1]:
            continue

        data1 = predict_and_detect(model, img)

        # leica: Ann to axis(x,y)
        # basename like:  "1.slide4-977-F29_0"
        basename = os.path.basename(iname)[:-4] # remove ext name
        try:
            Ann = basename.split('-')[-1]
            tmp = celltools.leica_Ann_to_axis(Ann,std_axis)
            real_axis = f"{tmp[0]}, {tmp[1]}"
            # like '125.3, 22.4'
        except:
            real_axis = '0, 0'
        
        # one image
        roi_img_node = add_roi_imgname(roi_root, 
                            os.path.basename(iname),
                            str(count_img),real_axis,ch_num=str(ch_num))

        # box in boxes
        for d in data1:
            add_roi_img_roi(roi_img_node,
                        [d['x1'], d['y1'],d['x2'],d['y2']],   
                        tp = d['tp'])
            c_tp[d['tp']] += 1

        count_img += 1
        if count_img >=limit:
            break

    # save roi xml
    write_pretty_xml(case_dir + '/roi.xml',roi_root)

    # report subtotal info
    calcinfo_node = { 
        'images': str(count_img), # all image num
        'marked': str(count_img), # marked image num
        'dic'   : str(c_tp['dic']),
        'trc'   : '0', 
        'f': str(c_tp['f'] + c_tp['min']),
        'min': '0',
        't': '0',
        'r': str(c_tp['r']),
        'nr': str(c_tp['nr']),
        'rogue':'0',
        'abn':str(c_tp['f'] + c_tp['min']+c_tp['nr']), # total abnormal numbers
        'abb_rate': '0.0',
        'marked_rate': '0.0',
    }   
    add_report_calc(report_root, calcinfo_node)
    
    # report info
    receiver_time = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
    report_info = { 
        'reportdate' : '',  # 报告日期
        'receiver' : '',    # 接收医生
        'receiver_time': receiver_time, #接收时间 2020-01-22 16:20
        'inspector' : '',    #检查医生
        'reviewer' : '',     #审核医生
        'reviewer_time' : '' #审核时间 2020-01-24 10:10
    }
    add_report_reportinfo(report_root, report_info)

    # save report xml
    write_pretty_xml(case_dir + '/report.xml', report_root)



# test this predict by command line for one case
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='mn predict')
    parser.add_argument('--model',  '-m', default='weights/last.pt')
    parser.add_argument('--case_dir','-c', default='')
    parser.add_argument('--limit',  '-l', default=10, type=int,
                        help="limit image numbers")
    parser.add_argument('--score', '-sc', default=0.5, type=float)
    args = parser.parse_args()

    model = YOLO(args.model)

    # read the image
    if os.path.isdir(args.case_dir):
        predict_report(model,args.case_dir)
    else:
        print('do nothing')
