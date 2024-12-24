from ultralytics import YOLO
import cv2
import os
from glob import glob
import argparse

def predict(chosen_model, img, classes=[], conf=0.5):
    if classes:
        results = chosen_model.predict(img, classes=classes, conf=conf)
    else:
        results = chosen_model.predict(img, conf=conf)

    return results


def predict_and_detect(chosen_model, img, classes=[], conf=0.5, 
                       rectangle_thickness=2, text_thickness=1):
    results = predict(chosen_model, img, classes, conf=conf)
    for result in results:
        print(result)
        exit()
        for box in result.boxes:
            cv2.rectangle(img, 
                    (int(box.xyxy[0][0]), int(box.xyxy[0][1])),
                    (int(box.xyxy[0][2]), int(box.xyxy[0][3])),
                    (255, 0, 0),
                    rectangle_thickness)
            cv2.putText(img, f"{result.names[int(box.cls[0])]}",
                        (int(box.xyxy[0][0]), int(box.xyxy[0][1]) - 10),
                        cv2.FONT_HERSHEY_PLAIN, 1,
                        (255, 0, 0), text_thickness)
    return img, results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='mn predict')
    parser.add_argument('--model',  '-m', default='weights/last.pt')
    parser.add_argument('--val_dir','-v', default='val')
    parser.add_argument('--image',  '-i', default='')
    parser.add_argument('--display','-d', action='store_true')
    parser.add_argument('--save',   '-s', default='/dev/shm',
                        help="saved name or dir")
    parser.add_argument('--limit',  '-l', default=100, type=int)
    parser.add_argument('--score', '-sc', default=0.5, type=float)
    args = parser.parse_args()

    model = YOLO(args.model)

    # read the val's images
    if os.path.isdir(args.val_dir):
        print('test val')
        os.makedirs(f"{args.save}/mctest",exist_ok=True)
        count = 0
        imgs = glob(args.val_dir + "/*.png")
        for img in imgs:
            image = cv2.imread(img)
            result_img, _ = predict_and_detect(model,
                            image,
                            classes=[],
                            conf=args.score)
            
            bname = os.path.basename(img)
            cv2.imwrite(f"{args.save}/mctest/{bname}", result_img)
            print('predicted',bname)
            
            if count>=args.limit: break
            count += 1
    # read one image
    elif os.path.isfile(args.image):
        print(args.image)
        image = cv2.imread(args.image)
        result_img, _ = predict_and_detect(model,
                            image,
                            classes=[],
                            conf=args.score)
        bname = os.path.basename(args.image)
        if args.save is not None:
            cv2.imwrite(f"{args.save}/{bname}", result_img)
            print('predicted',bname)
        if args.display:
            cv2.imshow("Image", result_img)
            cv2.waitKey(0)
    else:
        print('do nothing')
