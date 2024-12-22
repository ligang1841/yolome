"""
    predict mn
    QC: NOT nessesary

    Predict:
        get lymph,mc,bc, until lymph > 1000 or images >=300

    report:
        mc: num, rate
        lymph: num
        微核率： micro core / lymphs+mc
        微核细胞率：mc / lymphs+mc
"""

from ultralytics import YOLO
import cv2
import os
from glob import glob
import argparse
from report_mn_xml import *
import time
from nms import remove_overlap_type as rm_bbox

# ====== config ===============================================
keep_label = ['lymph','mc','bc']
colour=[(0,255,0),(255,0,0),(0,0,255),(255,255,0)]
# jpg or png, jpg is better, but zeiss always output png
EXT='png'
# images number. 70 cells/image as good, 10 cells as bad image
# this limit will stop to analyze, even not get 1000 cells
limit=300
# =============================================================

# real predict in one image
def predict(chosen_model, img, classes=[], conf=0.5):
    if classes:
        results = chosen_model.predict(img, classes=classes, conf=conf)
    else:
        results = chosen_model.predict(img, conf=conf)

    return results

# get cells(lymph,mc,bc) with type and rect box
def predict_and_detect(chosen_model, img, classes=[], conf=0.5): 
    results = predict(chosen_model, img, classes, conf=conf)
    data1 = []
    this_mn = 0

    for result in results:
        for box in result.boxes:
            tp = result.names[int(box.cls[0])]
            if tp not in keep_label:
                continue
            mc = int(tp=='mc')
            data1.append({'x1':int(box.xyxy[0][0]),
                          'y1':int(box.xyxy[0][1]),
                          'x2':int(box.xyxy[0][2]),
                          'y2':int(box.xyxy[0][3]),
                          'tp':tp,
                          'mc':mc})
            this_mn += mc

    return data1,this_mn


# main work flow and create report xml
def predict_report(model,case_dir):
    # report init
    roi_root = create_roi('new_one')
    report_root = create_report()
   
    bar_code = os.path.basename(case_dir) 
    baseinfo_node = {
        'pname': 'new-one',
        'pid': 'p0000',
        'hid': 'n12345',    # Hospital number
        'bid': '',          #病床号
        'dept': '体检中心',
        'bar_code': bar_code,
        'app_doctor':'',
        'app_time':'',
        'sampling_time':'',
        'test_item': '全血',  #标本类型
        'age': '40',
        'sex': '1'  #性别 1：男， 0：女
    }
    # add to xml
    add_report_baseinfo(report_root, baseinfo_node)
    add_report_aerial(report_root)

    # ---------- predict all images ----------
    imgs = glob(case_dir + f'/xy/*.{EXT}')
    X=Y = '0'
    count_img = 0
    count_lym = 0
    count_mc = 0
    count_bc = 0
    for iname in imgs:
        img = cv2.imread(iname)
        data1,this_mn = predict_and_detect(model, img)
        if data1==[]:
            continue

        # remove overlap bbox
        data1 = rm_bbox(data1)
        
        # one image
        roi_img_node = add_roi_imgname(roi_root, 
                            os.path.basename(iname),
                            bar_code,X,Y,this_mn)

        # box in boxes
        for d in data1:
            add_roi_img_roi(roi_img_node,
                        [d['x1'], d['y1'],d['x2'],d['y2']],   
                        tp = d['tp'],
                        mn = int(d['tp']=='mc'))
            count_lym += int(d['tp'] == 'lymph')
            count_mc  += int(d['tp'] == 'mc')
            count_bc  += int(d['tp'] == 'bc')

        count_img += 1
        if count_img >=limit:
            break

    # save roi xml
    write_pretty_xml(case_dir + '/roi.xml',roi_root)

    # report subtotal info
    calcinfo_node = { 
        'images' : str(count_img),
        'mc_cell': str(count_mc), # mc cell number, count_tp[0]
        'mc'     : str(count_mc), # core number in this image
        'lymph'  : str(count_lym),
        'bc'     : str(count_bc), # Undifferentiated cells
        'mc_cell_rate': '0',
        'mc_rate': '0',
        'bc_rate': '0',
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
    parser.add_argument('--val_dir','-v', default='')
    parser.add_argument('--image',  '-i', default='')
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
