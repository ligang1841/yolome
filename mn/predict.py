from ultralytics import YOLO
import cv2
from glob import glob

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
    #model = YOLO("yolo11x.pt")
    model = YOLO("runs/train/exp7/weights/last.pt")

    # read the image
    image = cv2.imread("test-mc2.png")
    result_img, _ = predict_and_detect(model, image, classes=[], conf=0.5)

    cv2.imwrite("/dev/shm/test.png", result_img)
    #cv2.imshow("Image", result_img)
    #cv2.waitKey(0)
