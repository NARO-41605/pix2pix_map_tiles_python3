# -*- coding: utf-8 -*

import os
import numpy as np
import argparse
import re
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("--target_dir", required=True)
parser.add_argument("--correct_dir", required=True)
parser.add_argument("--result_file", default="./result.txt")
parser.add_argument("--image_ext", default="png")

args = parser.parse_args()

TARGET_DIR = args.target_dir
CORRECT_DIR = args.correct_dir
RESULT_FILE = args.result_file

IMAGE_EXT = args.image_ext
if IMAGE_EXT[0] != ".":
    IMAGE_EXT = "."+IMAGE_EXT

# 評価する画像を取得
'''
targetImageList = []

for pathname, dirnames, filenames in os.walk(TARGET_DIR):
    for filename in filenames:
        # tifファイルのみ取得
        if filename.endswith(IMAGE_EXT):
            targetImageList.append(os.path.join(pathname, filename))
'''
targetImageList = ([os.path.join(pathname, filename) for pathname, dirnames, filenames in os.walk(TARGET_DIR) 
                                                     for filename in filenames if filename.endswith(IMAGE_EXT)])

if not os.path.isdir(os.path.dirname(RESULT_FILE)):
    os.makedirs(os.path.dirname(RESULT_FILE))

fp = open(RESULT_FILE, "w")

all_correctSize = 0
all_imageSize = 0
result_str = ""
count_num = 0
classCorrectSize = {}

for targetImagePath in targetImageList:
    correctImagePath = os.path.join(CORRECT_DIR, targetImagePath.replace(TARGET_DIR, ""))

    if not os.path.isfile(correctImagePath):
        continue

    target_img = Image.open(targetImagePath)
    correct_img = Image.open(correctImagePath)
    correct_img = correct_img.convert("RGB")
    target_img = target_img.convert("RGB")
    correct_img = correct_img.convert("P")
    target_img = target_img.convert("P")

    if target_img.mode != "P" or correct_img.mode != "P":
        print("\n-------------------------------------\n")
        print("target : "+targetImagePath)
        print("correct : "+correctImagePath)
        print("Skip : no index color images.")
        continue

    count_num += 1
    print("\n------ "+str(count_num)+" -------------------------------\n")
    print("target : "+targetImagePath)
    print("correct : "+correctImagePath+"\n")

    # 全体の正解率を出す
    targetArr = np.asarray(target_img)
    correctArr = np.asarray(correct_img)
    resultArr = np.equal(targetArr, correctArr)
    imageSize = targetArr.size
    correctSize = np.sum(resultArr)
    correctRate = (float(correctSize) / float(imageSize))*100.0

    all_imageSize += imageSize
    all_correctSize += correctSize

    result_str += "------ "+str(count_num)+" -------------------------------\n\n"
    result_str += "target : "+targetImagePath+"\n"
    result_str += "correct : "+correctImagePath+"\n"
    result_str += "\n"

    # クラスごとの正解率を出す
    classList, classSizeList = np.unique(correct_img, return_counts=True)
    classCorrectSize_tmp = {}
    for classVal, classSize in zip(classList, classSizeList):
        result_classArr = np.logical_and(resultArr, correctArr == classVal)
        classCorrectRate = float(np.sum(result_classArr)) / float(np.sum(correctArr == classVal))*100.0
        classCorrectObj = [classCorrectRate, np.sum(result_classArr), np.sum(correctArr == classVal)]
        classCorrectSize_tmp[classVal] = classCorrectObj

        if not classVal in classCorrectSize:
            classCorrectSize[classVal] = [0, 0]
        classCorrectSize[classVal][0] += classCorrectObj[1]
        classCorrectSize[classVal][1] += classCorrectObj[2]

        print("index "+str(classVal)+" : "+str(classCorrectObj[0])+"% ("+str(classCorrectObj[1])+"/"+str(classCorrectObj[2])+")")
        result_str += "index "+str(classVal)+" : "+str(classCorrectObj[0])+"% ("+str(classCorrectObj[1])+"/"+str(classCorrectObj[2])+")\n"

    result_str += "\n"
    result_str += "correct rate : "+str(correctRate)+"% ("+str(correctSize)+"/"+str(imageSize)+")\n"
    result_str += "\n"

    print("\ncorrect rate : "+str(correctRate)+"% ("+str(correctSize)+"/"+str(imageSize)+")")

if not all_imageSize == 0:
    all_correctRate = (float(all_correctSize) / float(all_imageSize))*100.0
else:
    all_correctRate = 0
result_str += "-------------------------------------\n\n"

print("\n-------------------------------------\n")
for classVal in classCorrectSize:
    classCorrectObj = classCorrectSize[classVal]
    classCorrectRate = float(classCorrectObj[0]) / float(classCorrectObj[1]) * 100.0
    result_str += "index "+str(classVal)+" : "+str(classCorrectRate)+"% ("+str(classCorrectObj[0])+"/"+str(classCorrectObj[1])+")\n"
    print("index "+str(classVal)+" : "+str(classCorrectRate)+"% ("+str(classCorrectObj[0])+"/"+str(classCorrectObj[1])+")")

result_str += "\n"
result_str += "all correct rate : "+str(all_correctRate)+"% ("+str(all_correctSize)+"/"+str(all_imageSize)+")\n"
result_str += str(count_num)+" images\n"

print("\nall correct rate : "+str(all_correctRate)+"% ("+str(all_correctSize)+"/"+str(all_imageSize)+")\n")
print(str(count_num)+" images")

fp.write(result_str)
fp.close()





