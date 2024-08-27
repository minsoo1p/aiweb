import numpy as np
import cv2
from PIL import Image
from collections import Counter

def tal_line (predicted_mask_tal) :
  # 이진화 - 임계값을 설정하여 이진 마스크를 생성합니다.
  _, binary_mask = cv2.threshold(predicted_mask_tal, 0.5, 1.0, cv2.THRESH_BINARY)

  # 이진화된 이미지를 uint8 타입으로 변환합니다.
  binary_mask = (binary_mask * 255).astype(np.uint8)

  # 외곽선 찾기
  contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  # 가장 잘 맞는 타원 찾기
  cnt = contours[0]
  ellipse = cv2.fitEllipse(cnt)

  (center, axes, angle) = ellipse
  major_axis_length = max(axes)
  minor_axis_length = min(axes)
  center_x, center_y = int(center[0]), int(center[1])

  angle_rad = np.deg2rad(angle+90)
  end_x = int(center_x + major_axis_length / 2 * np.cos(angle_rad))
  end_y = int(center_y + major_axis_length / 2 * np.sin(angle_rad))
  start_x = int(center_x - major_axis_length / 2 * np.cos(angle_rad))
  start_y = int(center_y - major_axis_length / 2 * np.sin(angle_rad))

  data = {
      'axis' : [[start_x, start_y], [end_x, end_y]]
  }

  return data

def tib_line (predicted_mask_tib) :
  # 이진화 - 임계값을 설정하여 이진 마스크를 생성합니다.
  _, binary_mask = cv2.threshold(predicted_mask_tib, 0.5, 1.0, cv2.THRESH_BINARY)

  # # 이진화된 이미지를 uint8 타입으로 변환합니다.
  # binary_mask = (binary_mask * 255).astype(np.uint8)

  # 외곽선 찾기
  contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  cntr = contours[0]

#Axis

  dst = cv2.distanceTransform(binary_mask, cv2.DIST_L2, 5)
  dst = (dst/(dst.max()-dst.min())*255).astype(np.uint8)
  # skeleton = cv2.adaptiveThreshold(dst, 255, cv2.cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \cv2.THRESH_BINARY, 7, -3)
  skeleton = cv2.adaptiveThreshold(dst, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, -3)
  skeleton = cv2.ximgproc.thinning(skeleton)
  _, binary_skeleton = cv2.threshold(skeleton, 0, 255, cv2.THRESH_BINARY)

  result = []
  y = 0
  for skel in binary_skeleton:
      if 255 in skel:
        if np.sum(skel) == 255 :
          x = np.where(skel == 255)[0][0]  # 첫 번째 255의 인덱스를 가져옴
          result.append((x, y))
        else:
          pass
      else:
        pass
      y += 1

  groups = []
  current_group = []

  current_group.append(result[0])

  for i in range(1, len(result)):
      if abs(result[i][1] - result[i-1][1]) >= 6:
          # 차이가 6 이상이면 현재 그룹을 저장하고 새로운 그룹 시작
          groups.append(current_group)
          current_group = []

      current_group.append(result[i])

  if current_group:
      groups.append(current_group)

  for idx, group in enumerate(groups):
      globals()[f'result{idx + 1}'] = group

  largest_group = max(groups, key=len)

  length = len(largest_group)
  x0, y0 =largest_group[0]
  x1, y1 =largest_group[length-1]
  (x2, y2) = (x1-x0, y1-y0)

  data = {}
  data['axis'] = [[x0 - x2, y0 - y2],[x1 + x2, y1 + y2]]

# tangent

  hull = cv2.convexHull(cntr, returnPoints=False)
  # cv2.drawContours(image, [hull],-1, (0, 255, 0), 1)

  defects = cv2.convexityDefects(cntr, hull)

  starts = []
  ends = []
  for i in range(defects.shape[0]) :
    s, e, f, d = defects[i, 0]
    start = tuple(cntr[s][0])
    end = tuple(cntr[e][0])
    farthest = tuple(cntr[f][0])
    dist = d/256.0
    if dist > 1 :
      starts.append(start)
      ends.append(end)
  max_start = max(starts, key=lambda point: point[1])
  max_end = max(ends, key=lambda point: point[1])

  x3, y3 = max_start
  x4, y4 = max_end
  (x5, y5) = (x4-x3, y4-y3)



  data['tangent'] = [[x3 - x5, y3 - y5],[x4 + x5, y4 + y5]]

  return data

def cal_line (predicted_mask_cal) :
  # 이진화 - 임계값을 설정하여 이진 마스크를 생성합니다.
  _, binary_mask = cv2.threshold(predicted_mask_cal, 0.5, 1.0, cv2.THRESH_BINARY)

  # # 이진화된 이미지를 uint8 타입으로 변환합니다.
  # binary_mask = (binary_mask * 255).astype(np.uint8)

  # 외곽선 찾기
  contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  cntr = contours[0]

# tangent

  hull = cv2.convexHull(cntr, returnPoints=False)
  # cv2.drawContours(image, [hull],-1, (0, 255, 0), 1)

  defects = cv2.convexityDefects(cntr, hull)

  starts = []
  ends = []
  for i in range(defects.shape[0]) :
    s, e, f, d = defects[i, 0]
    start = tuple(cntr[s][0])
    end = tuple(cntr[e][0])
    farthest = tuple(cntr[f][0])
    dist = d/256.0
    if dist > 1 :
      starts.append(start)
      ends.append(end)
  max_start = max(starts, key=lambda point: point[1])
  max_end = max(ends, key=lambda point: point[1])

  x3, y3 = max_start
  x4, y4 = max_end
  (x5, y5) = (x4-x3, y4-y3)

  data={}

  data['tangent'] = [[x3 , y3 ],[x4 + x5, y4 + y5]]

# lowest point

  points = cntr.reshape(-1, 2)

  max_y_index = np.argmax(points[:, 1])
  max_y_point = points[max_y_index]

  data['lowest'] = list(max_y_point)


  return data


def m5_line (predicted_mask_m5) :
  # 이진화 - 임계값을 설정하여 이진 마스크를 생성합니다.
  _, binary_mask = cv2.threshold(predicted_mask_m5, 0.5, 1.0, cv2.THRESH_BINARY)

  # # 이진화된 이미지를 uint8 타입으로 변환합니다.
  # binary_mask = (binary_mask * 255).astype(np.uint8)

  # 외곽선 찾기
  contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  cntr = contours[0]

# lowest point

  points = cntr.reshape(-1, 2)

  max_y_value = points[:, 1].max()

  # 최대 y값과 같은 y값을 가진 모든 점의 인덱스를 찾습니다.
  max_y_indices = np.where(points[:, 1] == max_y_value)[0]


  lowest_point = points[round(sum(max_y_indices)/len(max_y_indices))]

  data = {}
  data['lowest'] = list(lowest_point)


  return data

def get_main_branch_endpoints(skeleton):
    # 흰색 픽셀의 좌표 추출
    points = np.column_stack(np.where(skeleton == 255))

    x_group = [point[1] for point in points]
    x_counter = Counter(x_group)
    
    # 빈도수가 1인 x 좌표만 선택
    unique_x = [x for x, count in x_counter.items() if count == 1]
    
    # 원래 포인트 중에서 유일한 x 좌표를 가진 포인트만 선택
    filtered_points = [point for point in points if point[1] in unique_x]

    sorted_points = sorted(filtered_points, key=lambda p: p[1])
    
    groups = []
    current_group = [sorted_points[0]]
    
    for i in range(1, len(sorted_points)):
        current_point = sorted_points[i]
        previous_point = sorted_points[i-1]
        
        if current_point[1] - previous_point[1] >= 6:
            # 새 그룹 시작
            groups.append(current_group)
            current_group = [current_point]
        else:
            # 현재 그룹에 포인트 추가
            current_group.append(current_point)
    
    # 마지막 그룹 추가
    groups.append(current_group)
    
    # 가장 긴 그룹 선택
    longest_group = max(groups, key=len)

    # 가장 긴 그룹의 시작점과 끝점 찾기
    start_point = longest_group[0]
    end_point = longest_group[-1]

    return start_point[::-1], end_point[::-1]   

def m1_line (predicted_mask_m1) :
  # 이진화 - 임계값을 설정하여 이진 마스크를 생성합니다.
  _, binary_mask = cv2.threshold(predicted_mask_m1, 0.5, 1.0, cv2.THRESH_BINARY)

  # # 이진화된 이미지를 uint8 타입으로 변환합니다.
  # binary_mask = (binary_mask * 255).astype(np.uint8)

  # 외곽선 찾기
  contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  dst = cv2.distanceTransform(binary_mask, cv2.DIST_L2, 5)
  dst = (dst/(dst.max()-dst.min())*255).astype(np.uint8)
  # skeleton = cv2.adaptiveThreshold(dst, 255, cv2.cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \cv2.THRESH_BINARY, 7, -3)
  skeleton = cv2.adaptiveThreshold(dst, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, -3)
  skeleton = cv2.ximgproc.thinning(skeleton)
  _, binary_skeleton = cv2.threshold(skeleton, 0, 255, cv2.THRESH_BINARY)

  start_point, end_point = get_main_branch_endpoints(binary_skeleton)

  data = {'axis' : [[start_point[0], start_point[1]], [end_point[0], end_point[1]]]}
  return data

class Cleaning_contour :
  def __init__(self) :
    pass

  def clean_contour(self, mask) :
    # 외곽선 찾기
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 가장 큰 외곽선만
    if not contours:
      pass
    else : 
      largest_contour = max(contours, key=cv2.contourArea)


    # 빈 마스크 생성
    largest_contour_mask = np.zeros_like(mask)

    # 가장 큰 외곽선만 그리기
    cv2.drawContours(largest_contour_mask, [largest_contour], -1, 255, thickness=cv2.FILLED)
    # largest_contour_mask = cv2.cvtColor(largest_contour_mask, cv2.COLOR_GRAY2BGR)

    return largest_contour_mask

  def arc_contour(self, mask) :
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = contours[0]

    # 오차범위는?
    epsilon = 0.005 * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)
    arc_contour_mask = np.zeros_like(mask)

    cv2.drawContours(arc_contour_mask, [approx], -1, 255, thickness=cv2.FILLED)

    return arc_contour_mask

  def decay_contour(self, mask) :
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    return closing
  
class Post_processing : 
    def __init__(self, cleaned_masks_data) :
        self.cleaned_masks_data = cleaned_masks_data

    def postProcess(self):
        self.cleaned_masks_data = self.cleaned_masks_data.copy()
        for input in self.cleaned_masks_data:
            if input == 'tib':
               cleaned_mask = self.cleaned_masks_data['tib']
               self.cleaned_masks_data['tib'] = tib_line(cleaned_mask) 
            elif input == 'tal':
               cleaned_mask = self.cleaned_masks_data['tal']
               self.cleaned_masks_data['tal'] = tal_line(cleaned_mask) 
            elif input == 'cal':
               cleaned_mask = self.cleaned_masks_data['cal']
               self.cleaned_masks_data['cal'] = cal_line(cleaned_mask) 
            elif input == 'm5':
               cleaned_mask = self.cleaned_masks_data['m5']
               self.cleaned_masks_data['m5'] = m5_line(cleaned_mask) 
            elif input == 'm1':
               cleaned_mask = self.cleaned_masks_data['m1']
               self.cleaned_masks_data['m1'] = m1_line(cleaned_mask) 
            else : 
               pass
        data = self.cleaned_masks_data
        return data