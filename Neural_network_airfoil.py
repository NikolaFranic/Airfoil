import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from numpy.random import default_rng


def build_and_compile_model(norm):
  model = keras.Sequential([
      norm,
      layers.Dense(124, activation='relu'),
      layers.Dense(64, activation='relu'),
      layers.Dense(16, activation='relu'),
      layers.Dense(1)
  ])

  model.compile(loss="mean_absolute_error",
                optimizer=tf.keras.optimizers.Adam(0.0001))
  return model

# Make NumPy printouts easier to read.
np.set_printoptions(precision=3, suppress=True)

# import dataset
dataset = pd.read_pickle("data\\airfoil_database_with_angle_1.pk1")
for i in range(2,19):
    dataset_temp = pd.read_pickle(f"data\\airfoil_database_with_angle_{i}.pk1")
    dataset = dataset.append(dataset_temp)
dataset = dataset.reset_index(drop=True)

print(dataset.shape)

# reducing size of dataset due to memmory error
arr_indices_top_drop = default_rng().choice(dataset.index,size =700000,replace=False)
dataset = dataset.drop(index=arr_indices_top_drop)
dataset = dataset.reset_index(drop=True)
print(dataset.shape)

# make splits
train_dataset = dataset.sample(frac=0.8, random_state=0)
test_dataset = dataset.drop(train_dataset.index)


train_features = train_dataset.copy()
test_features = test_dataset.copy()

train_labels = train_features.pop(1001)
test_labels = test_features.pop(1001)

train_features.pop(1002)
test_features.pop(1002)


#train_labels = train_features.iloc[:,[1000,1001]]
#train_features = train_features.drop(train_features.iloc[:,[1000,1001]], axis = 1)

#test_labels = test_features.iloc[:,[1000,1001]]
#test_features = test_features.drop(test_features.iloc[:,[1000,1001]], axis = 1)

# network
normalizer = tf.keras.layers.Normalization(axis=-1)
normalizer.adapt(np.array(train_features))

dnn_model = build_and_compile_model(normalizer)
dnn_model.summary()

history = dnn_model.fit(
    train_features,
    train_labels,
    validation_split=0.2,
    verbose=2, epochs=3000)

# plot loss
plt.plot(history.history['loss'], label='loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.xlabel('Epoch')
plt.ylabel('Error')
plt.legend()
plt.grid(True)
plt.show()


test_predictions = dnn_model.predict(test_features).flatten()

# print error
print("Mean Absolute Error: " + str(dnn_model.evaluate(test_features, test_labels, verbose=0)))

"""#print(test_labels)
#print(test_predictions)
# plot predictions - true values
a = plt.axes(aspect='equal')
plt.scatter(test_labels, test_predictions)
plt.xlabel('True Values')
plt.ylabel('Predictions')
#lims = [0, 1]
#plt.xlim(lims)
#plt.ylim(lims)
#_ = plt.plot(lims, lims)
plt.show()"""


# save model
dnn_model.save('airfoil_nn_model')