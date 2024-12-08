#import warnings
#warnings.filterwarnings('ignore')
from ultralytics import YOLO

if __name__ == '__main__':
    # 如何切换模型版本, 上面的ymal文件可以改为 yolov11s.yaml就是使用的v11s,
    # 类似某个改进的yaml文件名称为yolov11-XXX.yaml
    #   那么如果想使用其它版本就把上面的名称改为yolov11l-XXX.yaml即可
    #   （改的是上面YOLO中间的名字不是配置文件的）！
    model = YOLO('yolo11.yaml')
    
    # 是否加载预训练权重,科研不建议大家加载否则很难提升精度
    # model.load('yolov11n.pt') 

    model.train(data=r"mn_zss_jiangmen.yaml",
                # 如果任务是其它的
                #   'ultralytics/cfg/default.yaml'找到这里
                #   修改task 为下面的某个 detect, segment, classify, pose
                cache=False,
                imgsz=1360,
                scale=0, # no scale image
                epochs=100,
                single_cls=False,  # 是否是单类别检测
                batch=4,
                close_mosaic=0,
                workers=0,
                device='0',
                optimizer='SGD', # using SGD 优化器 默认为auto建议大家使用固定的.
                # resume=, # 续训的话这里填写True, 
                           # yaml文件的地方改为lats.pt的地址,
                           # 需要注意的是如果你设置训练200轮次模型，训练了200轮次是没有办法进行续训的.
                amp=True,  # 如果出现训练损失为Nan可以关闭amp
                project='runs/train',
                name='exp',
                )
 