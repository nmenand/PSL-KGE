import argparse, sys, json, os, random

def main():

    seed = 1949019809340912
    random.seed(seed)
    print(seed)

#Append TransE dataset into one big file
"""
    test  = open("WN18/test.txt", "r")
    train = open("WN18/train.txt", "r")
    valid = open("WN18/valid.txt", "r")
    data = open("WN18/data.txt", "w")

    for x in test:
        data.write(x)
    for x in train:
        data.write(x)
    for x in valid:
        data.write(x)
    data.close()
"""


#    os.mkdir("FB15k/split1")
#    os.mkdir("FB15k/split2")
#    os.mkdir("FB15k/split3")
#    os.mkdir("FB15k/split4")
#    os.mkdir("FB15k/split5")
#    os.mkdir("FB15k/split6")
#    os.mkdir("FB15k/split7")
#    os.mkdir("FB15k/split8")
#    os.mkdir("FB15k/split9")
#    os.mkdir("FB15k/split10")


# Split dataset into 10 parts
"""
    data = open("FB15k/data.txt", "r")
    data1 = open("FB15k/split1/data.txt", "w")
    data2 = open("FB15k/split2/data.txt", "w")
    data3 = open("FB15k/split3/data.txt", "w")
    data4 = open("FB15k/split4/data.txt", "w")
    data5 = open("FB15k/split5/data.txt", "w")
    data6 = open("FB15k/split6/data.txt", "w")
    data7 = open("FB15k/split7/data.txt", "w")
    data8 = open("FB15k/split8/data.txt", "w")
    data9 = open("FB15k/split9/data.txt", "w")
    data10 = open("FB15k/split10/data.txt", "w")

    #data = open("WN18/data.txt", "r")
    dataList = data.read().split('\n')
    random.shuffle(dataList)
    splitLen = len(dataList)/10
    counter = 1
    splitNo = 1

    for x in dataList:
        if(counter == 1):
            print(x)
        if(splitNo==1):
            data1.write(x+"\n")
        if(splitNo==2):
            data2.write(x+"\n")
        if(splitNo==3):
            data3.write(x+"\n")
        if(splitNo==4):
            data4.write(x+"\n")
        if(splitNo==5):
            data5.write(x+"\n")
        if(splitNo==6):
            data6.write(x+"\n")
        if(splitNo==7):
            data7.write(x+"\n")
        if(splitNo==8):
            data8.write(x+"\n")
        if(splitNo==9):
            data9.write(x+"\n")
        if(splitNo==10):
            data10.write(x+"\n")
        counter += 1
        if(counter == splitLen):
            counter = 1
            splitNo += 1
    data1.close()
    data2.close()
    data3.close()
    data4.close()
    data5.close()
    data6.close()
    data7.close()
    data8.close()
    data9.close()
    data10.close()
"""

#Generate Test, Train and validation sets in each split
"""
    random.seed(192039114042603812)
    data = open("FB15k/split9/data.txt", "r")
    test = open("FB15k/split9/test.txt", "w")
    train = open("FB15k/split9/train.txt", "w")
    valid = open("FB15k/split9/valid.txt", "w")
    dataList = data.read().split('\n')
    random.shuffle(dataList)
    print(len(dataList))
    trainLen = int((len(dataList)*.9))
    print(trainLen)
    testLen = len(dataList) - trainLen
    counter = 1
    for x in dataList:
        if(counter < trainLen):
            train.write(x + '\n')
        elif(counter > trainLen and counter < trainLen + testLen*.5):
            test.write(x + '\n')
        else:
            valid.write(x + '\n')
        counter += 1

    #test.close()
    #train.close()
    #valid.close()
    #data.close()
"""

#Generate Negative Data
"""
random.seed(1092398032350812409324)
data = open("FB15k/data.txt", "r")
entity = open("FB15k/entity2id.txt", "r")
negData = open("FB15k/negData.txt", "w")
entityList  = entity.read().split('\n')
entitys = []
for x in entityList:
    entitys.append(x.split('\t')[0])

dataList = data.read().split('\n')

negList = []
for x in dataList:
    if(x):
        elem = x.split('\t')
        negElem = random.choice(entitys)
        while(elem[1] == negElem):
            negElem = random.choice(entitys)
        elem[1] = negElem
        negList.append(elem[0] + '\t' + elem[1]  + '\t' + elem[2]+ '\n')
for x in negList:
    negData.write(x)
"""

#Split Negative Data into 10 subparts
"""
random.seed(1120129310980234603)
data = open("WN18/negData.txt", "r")
data1 = open("WN18/split1/negData.txt", "w")
data2 = open("WN18/split2/negData.txt", "w")
data3 = open("WN18/split3/negData.txt", "w")
data4 = open("WN18/split4/negData.txt", "w")
data5 = open("WN18/split5/negData.txt", "w")
data6 = open("WN18/split6/negData.txt", "w")
data7 = open("WN18/split7/negData.txt", "w")
data8 = open("WN18/split8/negData.txt", "w")
data9 = open("WN18/split9/negData.txt", "w")
data10 = open("WN18/split10/negData.txt", "w")

#data = open("WN18/data.txt", "r")
dataList = data.read().split('\n')
random.shuffle(dataList)
splitLen = len(dataList)/10
counter = 1
splitNo = 1

for x in dataList:
    if(counter == 1):
        print(x)
    if(splitNo==1):
        data1.write(x+"\n")
    if(splitNo==2):
        data2.write(x+"\n")
    if(splitNo==3):
        data3.write(x+"\n")
    if(splitNo==4):
        data4.write(x+"\n")
    if(splitNo==5):
        data5.write(x+"\n")
    if(splitNo==6):
        data6.write(x+"\n")
    if(splitNo==7):
        data7.write(x+"\n")
    if(splitNo==8):
        data8.write(x+"\n")
    if(splitNo==9):
        data9.write(x+"\n")
    if(splitNo==10):
        data10.write(x+"\n")
    counter += 1
    if(counter == splitLen):
        counter = 1
        splitNo += 1
data1.close()
data2.close()
data3.close()
data4.close()
data5.close()
data6.close()
data7.close()
data8.close()
data9.close()
data10.close()
"""

#Split Code into PSL representation

if __name__ == "__main__":
    main()
