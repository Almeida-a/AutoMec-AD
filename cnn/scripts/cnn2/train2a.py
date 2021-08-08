#!/usr/bin/env python3

import csv
import cv2
import numpy as np

from keras.models import Sequential
from keras.layers import Flatten, Dense, Lambda, Cropping2D, Dropout
from keras.layers import Convolution2D, MaxPooling2D, ZeroPadding2D
#from keras.optimizers import Adam
from tensorflow.keras.optimizers import Adam 

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

import rospy
import pathlib

def main():


    # Init Node
    rospy.init_node('ml_training', anonymous=False)

    base_folder = rospy.get_param('~base_folder', 'set1') 
    modelname = rospy.get_param('~modelname', 'model-0808.h5')
    nb_epoch = rospy.get_param('~epochs', 30)
    batch_size = rospy.get_param('~batch_size', 32)
    #steps_per_epoch = rospy.get_param('~steps_per_epoch', 100)
    #batch_xtrain = rospy.get_param('~batch_xtrain', 20)
    #batch_ytrain = rospy.get_param('~batch_ytrain', 1)
    #batch_xval = rospy.get_param('~batch_xval', 25)
    #batch_yval = rospy.get_param('~batch_yval', 0)
    #validation_steps = rospy.get_param('~validation_steps', 50)

    print('base_folder: ', base_folder)
    print('modelname: ', modelname)
    print('epochs: ', nb_epoch)
    #print('steps_per_epoch: ', steps_per_epoch)

    #print('batch_xtrain: ', batch_xtrain)
    #print('batch_ytrain: ', batch_ytrain)
    #print('batch_xval: ', batch_xval)
    #print('batch_yval: ', batch_yval)
    #print('validation_steps: ', validation_steps)

    s = str(pathlib.Path(__file__).parent.absolute())
    path_data = s + '/../../data/' + base_folder
    
    #print('\ndata load from ' + base_folder)
    rospy.loginfo('Train with data load from:\n %s', base_folder)

    image_path = path_data + '/IMG/'

    total_left_angles = 0
    total_right_angles = 0
    total_straight_angles = 0

    images = []
    angles = []
    with open(path_data + '/driving_log.csv') as csvfile:
        reader = csv.reader(csvfile)
        k = 0
        for line in reader:
            k += 1
            if (k%2)==0:
                continue
            if k==1: continue

            print(line)
            center_image = cv2.imread(image_path + line[0],0)
            center_image = cv2.resize(center_image, (200, 100))
            center_image_temp = np.expand_dims(center_image, axis=2)

            images.append(center_image_temp)
            angles.append(float(line[1]))
            
            # Change image and store the same angle, with some distortion, both in image and in angle (to increase robustness)
            
            # flipped
            
            center_image_temp = np.expand_dims(cv2.flip(center_image, 1), axis=2)

            images.append(center_image_temp)


            angles.append(-float(line[1]))
            
            # add more distortions
            # ... 
            
            if(float(line[1]) < -0.1):
                total_left_angles += 1
            elif(float(line[1]) > 0.1):
                total_right_angles += 1
            else:
                total_straight_angles += 1


    left_to_straight_ratio = total_straight_angles/total_left_angles
    right_to_straight_ratio = total_straight_angles/total_right_angles

    print('angles are: ' + str(list(angles)))

    print('Total Samples : ', len(images))
    print()
    print('Initial Angle Distribution')
    print('Total Left Angles : ', total_left_angles)
    print('Total Right Angles : ', total_right_angles)
    print('Total Straight Angles : ', total_straight_angles)
    print('Left to Straight Ratio : ', left_to_straight_ratio)
    print('Right to Straight Ratio : ', right_to_straight_ratio)


    images = np.asarray(images)
    images = images.astype('float32')
    images /= 255
    angles = np.asarray(angles)


    X_train, X_test, y_train, y_test = train_test_split(images, angles, test_size=0.00001)


    train_samples_size = len(X_train)
    validation_samples_size = len(X_test)

    total_left_angles = 0
    total_right_angles = 0
    total_straight_angles = 0

    for train_sample in y_train:
        if(float(train_sample) < -0.15):
            total_left_angles += 1
        elif(float(train_sample) > 0.15):
            total_right_angles += 1
        else:
            total_straight_angles += 1

    left_to_straight_ratio = 0
    right_to_straight_ratio = 0

    left_to_straight_ratio = total_straight_angles/total_left_angles
    right_to_straight_ratio = total_straight_angles/total_right_angles

    print()
    print('Train Sample Size : ', train_samples_size)
    print('Validation Sample Size : ', validation_samples_size)

    print()
    print('After Train-Test split, Angle Distribution')
    print('Total Left Angles : ', total_left_angles)
    print('Total Right Angles : ', total_right_angles)
    print('Total Straight Angles : ', total_straight_angles)
    print('Left to Straight Ratio : ', left_to_straight_ratio)
    print('Right to Straight Ratio : ', right_to_straight_ratio)

    #batch_size = 20
    #nb_epoch = 20

    model = Sequential()
    model.add(Convolution2D(24, (5,5),(2, 2), input_shape = (100,200,1), activation='elu'))
    model.add(Convolution2D(36,(5,5),(2, 2), activation='elu'))
    model.add(Convolution2D(48, (5,5),(2, 2), activation='elu'))
    model.add(Convolution2D(64, 3, 3, activation='elu'))
    model.add(Convolution2D(64, 3, 3, activation='elu'))

    #model.add(Dropout(0.8))
    model.add(Flatten())
    model.add(Dense(100,activation='elu'))
    model.add(Dense(50,activation='elu'))
    model.add(Dense(10,activation='elu'))
    model.add(Dense(1))

    model.summary()

    model.compile(Adam(lr=0.0001),loss='mse')
    model.fit(X_train, y_train,epochs=nb_epoch, batch_size=batch_size)

    model.save('cnn2a-' + modelname)


if __name__ == '__main__':
    main()
