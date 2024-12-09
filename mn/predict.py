from ultralytics import YOLO
import cv2
from glob import glob
import argparse

def predict(chosen_model, img, classes=[], conf=0.5):
    if classes:
        results = chosen_model.predict(img, classes=classes, conf=conf)
    else:
        results = chosen_model.predict(img, conf=conf)

    return results


def predict_and_detect(chosen_model, img, classes=[], conf=0.5, rectangle_thickness=2, text_thickness=1):
    results = predict(chosen_model, img, classes, conf=conf)
    for result in results:
        for box in result.boxes:
            cv2.rectangle(img, (int(box.xyxy[0][0]), int(box.xyxy[0][1])),
                          (int(box.xyxy[0][2]), int(box.xyxy[0][3])), (255, 0, 0), rectangle_thickness)
            cv2.putText(img, f"{result.names[int(box.cls[0])]}",
                        (int(box.xyxy[0][0]), int(box.xyxy[0][1]) - 10),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), text_thickness)
    return img, results



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='mn predict')
    parser.add_argument('--model', '-m',default='weights/last.pt')
    parser.add_argument('--image', '-img')
    parser.add_argument('--display', '-d', action='store_true')
    parser.add_argument('--save', '-s')
    parser.add_argument('--score', '-sc',default=0.2, type=float)

    args = parser.parse_args()

    model = YOLO(args.model)

    # read the image
    image = cv2.imread(args.image)
    result_img, _ = predict_and_detect(model, image, classes=[], conf=args.score)

    if args.save is not None:
        cv2.imwrite(args.save, result_img)
    if args.display:
        cv2.imshow("Image", result_img)
        cv2.waitKey(0)
