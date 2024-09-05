from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt

def visualize_yolo_predictions(model_path, image_path):
    # 모델 로드
    model = YOLO(model_path)

    # 이미지에 대한 예측 수행
    results = model(image_path)

    # 결과 시각화
    for r in results:
        im_array = r.plot()  # plot() 메소드는 예측 결과가 그려진 이미지 배열을 반환합니다
        plt.figure(figsize=(12, 8))
        plt.imshow(cv2.cvtColor(im_array, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.title('YOLOv8 Prediction')
        plt.show()

# 모델 경로와 테스트 이미지 경로 설정
model_path = 'static\models\kind_detection_yolov8_model.pt'
test_image_path = 'static\images\혼종.jpg'  # 테스트 이미지 경로를 적절히 수정해주세요

# 예측 및 시각화 함수 호출
visualize_yolo_predictions(model_path, test_image_path)