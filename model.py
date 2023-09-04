import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
import os
from keras.optimizers import SGD

# from sklearn.metrics import confusion_matrix, classification_report


# model for training the dogs and cats dataset, scrapped from bing


import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation, BatchNormalization, GlobalAveragePooling2D, Conv2D, Dense, Dropout, Flatten, MaxPooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping
from tensorflow.keras.applications import DenseNet121

MODEL_NAME = 'cats and dogs'



# load datasets paths
train_dataset_path = MODEL_NAME  + '/seg_train'
validation_dataset_path = MODEL_NAME  + '/seg_test'
num_classes = len(os.listdir(train_dataset_path))
# resize images to 1/3:

IMG_WIDTH = 256
IMG_HEIGHT = 256

# SIZE OF BATCH

BATCH_SIZE = 32


def main():
    train_datagen = ImageDataGenerator(rescale=1.0/255,
                                       zoom_range=0.2,
                                       width_shift_range=0.2,
                                       height_shift_range=0.2,
                                       fill_mode='nearest')
    train_generator = train_datagen.flow_from_directory(train_dataset_path,
                                                        target_size=(
                                                            IMG_HEIGHT, IMG_WIDTH),
                                                        batch_size=BATCH_SIZE,
                                                        class_mode='categorical',
                                                        shuffle=True)

    validation_datagen = ImageDataGenerator(rescale=1.0/255)
    validation_generator = validation_datagen.flow_from_directory(validation_dataset_path,
                                                                  target_size=(
                                                                      IMG_HEIGHT, IMG_WIDTH),
                                                                  batch_size=BATCH_SIZE,
                                                                  class_mode='categorical',
                                                                  shuffle=True)

    labels = {value: key for key,
              value in train_generator.class_indices.items()}

    print("Label Mappings for classes present in the training and validation datasets\n")
    for key, value in labels.items():
        print(f"{key} : {value}")
    
    model = create_model()
    # model = create_model()
    # print(model.summary())
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss', factor=np.sqrt(0.1), patience=5)

    # model.compile(optimizer='adam',
    #               loss='categorical_crossentropy', metrics=['accuracy'])
    history = model.fit(train_generator, epochs=25, validation_data=validation_generator,
                        verbose=1)
    if not os.path.exists('datasets/models/' + MODEL_NAME):
        os.makedirs('datasets/models/' + MODEL_NAME)

    model.save('datasets/models/' + MODEL_NAME)


def create_model():
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', padding='same', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)))
    model.add(MaxPooling2D((2, 2)))

    model.add(Dropout(0.2))

    model.add(Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_uniform', padding='same'))
    model.add(MaxPooling2D((2, 2)))

    model.add(Dropout(0.2))

    model.add(Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_uniform', padding='same'))
    model.add(MaxPooling2D((2, 2)))

    model.add(Dropout(0.2))

    model.add(Flatten())
    model.add(Dense(128, activation='relu', kernel_initializer='he_uniform'))

    model.add(Dropout(0.5))

    model.add(Dense(num_classes, activation='sigmoid'))
    # compile model
    opt = SGD(lr=0.01)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    model .summary()
    return model


if __name__ == "__main__":
    main()