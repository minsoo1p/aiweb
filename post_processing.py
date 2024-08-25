import numpy as np
import cv2
from PIL import Image
from collections import Counter

def tal_line (predicted_mask_tal) :
  # 이진화 - 임계값을 설정하여 이진 마스크를 생성합니다.
  if predicted_mask_tal is None or predicted_mask_tal.size == 0:
    print("Warning: Input mask is empty or None")
    return None
  
  try : 

    _, binary_mask = cv2.threshold(predicted_mask_tal, 0.5, 1.0, cv2.THRESH_BINARY)

    # 이진화된 이미지를 uint8 타입으로 변환합니다.
    binary_mask = (binary_mask * 255).astype(np.uint8)

    # 외곽선 찾기
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print("Warning: No contours found")
        return None

    # 가장 잘 맞는 타원 찾기
    cnt = max(contours, key=cv2.contourArea)

    if len(cnt) < 5:
      print("Warning: Not enough points to fit an ellipse")
      return None
    
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
  
  except Exception as e:
    print(f"An error occurred: {str(e)}")
    return None

def tib_line(predicted_mask_tib):
    # 입력 마스크 검증
    if predicted_mask_tib is None or predicted_mask_tib.size == 0:
        print("Warning: Input mask is empty or None")
        return None

    try:
        # 이진화
        _, binary_mask = cv2.threshold(predicted_mask_tib, 0.5, 1.0, cv2.THRESH_BINARY)

        # 외곽선 찾기
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            print("Warning: No contours found")
            return None

        cntr = max(contours, key=cv2.contourArea)

        # Axis 계산
        dst = cv2.distanceTransform(binary_mask, cv2.DIST_L2, 5)
        dst = (dst/(dst.max()-dst.min())*255).astype(np.uint8)
        skeleton = cv2.adaptiveThreshold(dst, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, -3)
        skeleton = cv2.ximgproc.thinning(skeleton)
        _, binary_skeleton = cv2.threshold(skeleton, 0, 255, cv2.THRESH_BINARY)

        result = []
        for y, skel in enumerate(binary_skeleton):
            if 255 in skel:
                if np.sum(skel) == 255:
                    x = np.where(skel == 255)[0][0]
                    result.append((x, y))

        if len(result) < 2:
            print("Warning: Not enough points found in skeleton")
            return None

        groups = []
        current_group = [result[0]]

        for i in range(1, len(result)):
            if abs(result[i][1] - result[i-1][1]) >= 6:
                groups.append(current_group)
                current_group = []
            current_group.append(result[i])

        if current_group:
            groups.append(current_group)

        if not groups:
            print("Warning: No valid groups found")
            return None

        largest_group = max(groups, key=len)

        x0, y0 = largest_group[0]
        x1, y1 = largest_group[-1]
        x2, y2 = x1-x0, y1-y0

        data = {}
        data['axis'] = [[x0 - x2, y0 - y2], [x1 + x2, y1 + y2]]

        # Tangent 계산
        if len(cntr) > 3:  # convexHull needs at least 4 points
            hull = cv2.convexHull(cntr, returnPoints=False)
            defects = cv2.convexityDefects(cntr, hull)

            if defects is not None and defects.shape[0] > 0:
                starts = []
                ends = []
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(cntr[s][0])
                    end = tuple(cntr[e][0])
                    dist = d/256.0
                    if dist > 1:
                        starts.append(start)
                        ends.append(end)

                if starts and ends:
                    max_start = max(starts, key=lambda point: point[1])
                    max_end = max(ends, key=lambda point: point[1])

                    x3, y3 = max_start
                    x4, y4 = max_end
                    x5, y5 = x4-x3, y4-y3

                    data['tangent'] = [[x3 - x5, y3 - y5], [x4 + x5, y4 + y5]]
                else:
                    print("Warning: No valid defects found")
            else:
                print("Warning: No convexity defects found")
        else:
            print("Warning: Not enough points to compute convex hull")

        return data

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def cal_line(predicted_mask_cal):
    # 입력 마스크 검증
    if predicted_mask_cal is None or predicted_mask_cal.size == 0:
        print("Warning: Input mask is empty or None")
        return None

    try:
        # 이진화
        _, binary_mask = cv2.threshold(predicted_mask_cal, 0.5, 1.0, cv2.THRESH_BINARY)

        # 외곽선 찾기
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            print("Warning: No contours found")
            return None

        cntr = max(contours, key=cv2.contourArea)

        data = {}

        # Tangent 계산
        if len(cntr) > 3:  # convexHull needs at least 4 points
            hull = cv2.convexHull(cntr, returnPoints=False)
            defects = cv2.convexityDefects(cntr, hull)

            if defects is not None and defects.shape[0] > 0:
                starts = []
                ends = []
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(cntr[s][0])
                    end = tuple(cntr[e][0])
                    dist = d/256.0
                    if dist > 1:
                        starts.append(start)
                        ends.append(end)

                if starts and ends:
                    max_start = max(starts, key=lambda point: point[1])
                    max_end = max(ends, key=lambda point: point[1])

                    x3, y3 = max_start
                    x4, y4 = max_end
                    x5, y5 = x4-x3, y4-y3

                    data['tangent'] = [[x3, y3], [x4 + x5, y4 + y5]]
                else:
                    print("Warning: No valid defects found")
            else:
                print("Warning: No convexity defects found")
        else:
            print("Warning: Not enough points to compute convex hull")

        # Lowest point 계산
        if cntr.size > 0:
            points = cntr.reshape(-1, 2)
            max_y_index = np.argmax(points[:, 1])
            max_y_point = points[max_y_index]
            data['lowest'] = list(max_y_point)
        else:
            print("Warning: No points found in contour")

        return data

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def m5_line(predicted_mask_m5):
    # 입력 마스크 검증
    if predicted_mask_m5 is None or predicted_mask_m5.size == 0:
        print("Warning: Input mask is empty or None")
        return None

    try:
        # 이진화
        _, binary_mask = cv2.threshold(predicted_mask_m5, 0.5, 1.0, cv2.THRESH_BINARY)

        # 외곽선 찾기
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            print("Warning: No contours found")
            return None

        cntr = max(contours, key=cv2.contourArea)

        # Lowest point 계산
        if cntr.size > 0:
            points = cntr.reshape(-1, 2)
            max_y_value = points[:, 1].max()

            # 최대 y값과 같은 y값을 가진 모든 점의 인덱스를 찾습니다.
            max_y_indices = np.where(points[:, 1] == max_y_value)[0]

            if len(max_y_indices) > 0:
                lowest_point = points[round(sum(max_y_indices)/len(max_y_indices))]
                
                data = {}
                data['lowest'] = list(lowest_point)
                return data
            else:
                print("Warning: No points with maximum y-value found")
                return None
        else:
            print("Warning: No points found in contour")
            return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    

def get_main_branch_endpoints(skeleton):
    # 입력 검증
    if skeleton is None or skeleton.size == 0:
        print("Warning: Input skeleton is empty or None")
        return None, None

    try:
        # 흰색 픽셀의 좌표 추출
        points = np.column_stack(np.where(skeleton == 255))

        if len(points) == 0:
            print("Warning: No white pixels found in the skeleton")
            return None, None

        x_group = [point[1] for point in points]
        x_counter = Counter(x_group)
        
        # 빈도수가 1인 x 좌표만 선택
        unique_x = [x for x, count in x_counter.items() if count == 1]
        
        # 원래 포인트 중에서 유일한 x 좌표를 가진 포인트만 선택
        filtered_points = [point for point in points if point[1] in unique_x]

        if len(filtered_points) == 0:
            print("Warning: No points with unique x-coordinates found")
            return None, None

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
        
        if len(groups) == 0:
            print("Warning: No groups formed")
            return None, None

        # 가장 긴 그룹 선택
        longest_group = max(groups, key=len)

        if len(longest_group) < 2:
            print("Warning: Longest group has less than 2 points")
            return None, None

        # 가장 긴 그룹의 시작점과 끝점 찾기
        start_point = longest_group[0]
        end_point = longest_group[-1]

        return start_point[::-1], end_point[::-1]

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, None 

def m1_line(predicted_mask_m1):
    # 입력 마스크 검증
    if predicted_mask_m1 is None or predicted_mask_m1.size == 0:
        print("Warning: Input mask is empty or None")
        return None

    try:
        # 이진화
        _, binary_mask = cv2.threshold(predicted_mask_m1, 0.5, 1.0, cv2.THRESH_BINARY)

        # 이진화된 이미지를 uint8 타입으로 변환
        binary_mask = (binary_mask * 255).astype(np.uint8)

        # 외곽선 찾기
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            print("Warning: No contours found")
            return None

        # Distance Transform
        dst = cv2.distanceTransform(binary_mask, cv2.DIST_L2, 5)
        if dst.max() == dst.min():
            print("Warning: Distance transform resulted in uniform image")
            return None
        
        dst = ((dst - dst.min()) / (dst.max() - dst.min()) * 255).astype(np.uint8)

        # Adaptive Thresholding
        skeleton = cv2.adaptiveThreshold(dst, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, -3)

        # Thinning
        skeleton = cv2.ximgproc.thinning(skeleton)

        # Final thresholding
        _, binary_skeleton = cv2.threshold(skeleton, 0, 255, cv2.THRESH_BINARY)

        # Get main branch endpoints
        start_point, end_point = get_main_branch_endpoints(binary_skeleton)

        if start_point is None or end_point is None:
            print("Warning: Could not find valid endpoints")
            return None

        data = {'axis': [[start_point[0], start_point[1]], [end_point[0], end_point[1]]]}
        return data

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    
    
class Cleaning_contour :
  def __init__(self) :
    pass

  def clean_contour(self, mask) :
    # 외곽선 찾기
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    largest_contour_mask = np.zeros_like(mask)
    # 가장 큰 외곽선만
    if contours:
      largest_contour = max(contours, key=cv2.contourArea)
      cv2.drawContours(largest_contour_mask,[largest_contour],-1,255, thickness=cv2.FILLED)
    else : 
       largest_contour_mask = mask

    return largest_contour_mask

  def arc_contour(self, mask) :
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    arc_contour_mask = np.zeros_like(mask)

    if contours :   
      largest_contour = contours[0]

      # 오차범위는?
      epsilon = 0.005 * cv2.arcLength(largest_contour, True)
      approx = cv2.approxPolyDP(largest_contour, epsilon, True)
      
      cv2.drawContours(arc_contour_mask, [approx], -1, 255, thickness=cv2.FILLED)
    else : 
      arc_contour_mask = mask 

    return arc_contour_mask

  def arc_contour(self, mask):
      contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      arc_contour_mask = np.zeros_like(mask)
      
      if contours:
          largest_contour = contours[0]
          epsilon = 0.005 * cv2.arcLength(largest_contour, True)
          approx = cv2.approxPolyDP(largest_contour, epsilon, True)
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
    
