#import warnings
#warnings.filterwarnings('ignore')
from ultralytics import YOLO
import os,sys
import argparse
from glob import glob

WNAME = 'exp'
MODEL_DIR = 'runs/train'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='pbc-nv11 train')
    parser.add_argument('--yaml',  '-y', default='mot_wbc2')
    parser.add_argument('--imgsz',  '-sz', default=2560, type=int,help="img width")
    parser.add_argument('--epochs', '-i', default=30, type=int,help="about img-count*1.5 or 2.5")
    parser.add_argument('--model',  '-m', default='yolo11.yaml',help="base model: weights/yolo11n.yaml or weights/last.pt")
    #parser.add_argument('--resume', '-c', action='store_true')
    args = parser.parse_args()

    print("e.g. -y mot_wbc2 -i 10 -m weights/last.pt -c")
    print("For continue: training by loading the weights from your previously trained model and starting a new training session without the resume parameter")
    print("  model = YOLO('last.pt')")
    print("  model.train(data='data.yaml', epochs=200, imgsz=640, batch=64, workers=0)")

    # 如何切换模型版本, 上面的ymal文件可以改为 yolov11s.yaml就是使用的v11s,
    # 类似某个改进的yaml文件名称为yolov11-XXX.yaml
    #   那么如果想使用其它版本就把上面的名称改为yolov11l-XXX.yaml即可
    #   （改的是上面YOLO中间的名字不是配置文件的）！

    model = YOLO(args.model)
    
    # 是否加载预训练权重,科研不建议大家加载否则很难提升精度
    # model.load('yolov11n.pt') 

    yamlfile = f"../../yolo_datasets/{args.yaml}/dataset.yaml"
    model.train(data = yamlfile,
                #task 为下面的某个 detect, segment, classify, pose
                #task=
                cache   = True,
                imgsz   = args.imgsz,
                epochs  = args.epochs,
                single_cls=False,  # 是否是单类别检测
                batch   = 2,
                close_mosaic=0,
                workers = 2,
                device  = '0',
                optimizer= 'SGD', # using SGD 优化器 默认为auto建议大家使用固定的.
                # 续训的话这里填写True, 
                # yaml文件的地方改为exp(n)/weights/last.pt的地址,
                # 需要注意的是如果你设置训练200轮次模型，
                # 训练了200轮次是没有办法进行续训的.
                resume  = False, 
                #pretrained=True,
                amp     = True,  # 如果出现训练损失为Nan可以关闭amp
                project = MODEL_DIR,
                name    = WNAME,
                )
 
