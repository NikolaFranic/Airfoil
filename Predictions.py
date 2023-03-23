import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from scipy import interpolate
import Extraction_Methods


df = pd.read_csv("m3-il_m3.csv")
x_c = []
y_c = []

df.reset_index()
for index,row in df.iterrows():
    x_c.append(float(row["X"])/100)
    y_c.append(float(row["Y"]) / 100)

x_c, y_c = Extraction_Methods.Sorting_points(x_c, y_c)
tck, u = interpolate.splprep([x_c, y_c], k=1, s=0)
xnew, ynew = interpolate.splev(np.linspace(0, 1, 1000), tck)

array_test = np.append(ynew,[-3,1000000])

df_test = pd.DataFrame(array_test)
df_test = df_test.transpose()

model = tf.keras.models.load_model("airfoil_nn_model")

test_prediction = model.predict(df_test)

print(test_prediction)