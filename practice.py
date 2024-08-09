import tensorflow as tf
from keras.utils import to_categorical
# 예제 데이터
y = [0, 1, 2, 3]

# one-hot 인코딩
y_encoded = to_categorical(y)

print(y_encoded)

