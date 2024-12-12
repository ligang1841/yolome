"""
    predict ca
"""

from ultralytics import YOLO
import cv2
import os
from glob import glob
import argparse
from report_ca_xml import *
import time

# ====== config =======
keep_label = ["dic", "f1", "min", "f", "r", "nr", "f2"]
colour=[(255,0,0),(0,0,220),(0,0,200),(0,0,220),(200,0,0),(0,0,200),(0,0,220)]
EXT='png'

limit=300  # limit imgages
model_count = 'weights/last_count.pt'
ch_range=[40,52]
# =====================


def predict(chosen_model, img, classes=[], conf=0.5):
    if classes:
        results = chosen_model.predict(img, classes=classes, conf=conf)
    else:
        results = chosen_model.predict(img, conf=conf)

    return results


def predict_count(chosen_model, img, conf=0.5): 
    results = predict(chosen_model, img, [], conf=conf)
    count = 0
    for result in results:
        count += len(result.boxes)
    return count


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

def predict_report(model,case_dir):
    cmodel = YOLO(model_count)

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

        # test ch count
        ch_num = predict_count(cmodel,img)
        if ch_num<ch_range[0] or ch_num>ch_range[1]:
            continue

        data1 = predict_and_detect(model, img)
        
        # one image
        roi_img_node = add_roi_imgname(roi_root, 
                            os.path.basename(iname),
                            str(count_img),'0, 0',ch_num=str(ch_num))

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
