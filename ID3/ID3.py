# -*- coding: utf8 -*-
import numpy as np
import pandas as pd
from math import log
from treelib import *
from pythonds.basic.stack import Stack
from pythonds.trees.binaryTree import BinaryTree
from sklearn import preprocessing
import re

# ------------------------- 数据集 --------------------------- #
df = pd.read_csv('E:/Machine Learning/Algorithm implementation/Data/ID3_1.csv',encoding="GBK")
df.info()

# 处理数据集
df.age = np.where(df.age == "青年",np.where(df.age == "中年",2,3),1)
df.loan = np.where(df.loan == "一般",1,
                   np.where(df.loan == "好",2,3))

df.work = np.where(df.work == "是",1,0)
df.hourse = np.where(df.hourse == "是",1,0)
df['class'] = np.where(df['class'] == "是",1,0)

for i in np.arange(len(df.columns)):
    df.ix[:,i] = df.ix[:,i].astype('category')

df = df[['class','work','hourse','loan','age']]


# 信息增益算法 -----------------------------------------------------
def order_Y(data,y):
    df = data.copy()
    df['label'] = df[y]
    df = df.drop([y],axis=1)
    return df


# 特征分裂向量
def feature_split(df,y):
    feature_split_num = []

    # Y类别个数
    class_categories_num = len(df[y].cat.categories)

    for i in np.arange(0,(len(df.columns) - 1)):

        # 特征类别个数
        features_categories_num = len(df[df.columns[i]].cat.categories)

        Vec = np.zeros(shape=(features_categories_num,class_categories_num))
        for j in np.arange(0,len(df[df.columns[i]].cat.categories)):
            a = ((df[df.columns[i]] == df[df.columns[i]].cat.categories[j]) & (df[y] == df[y].cat.categories[0])).sum()
            b = ((df[df.columns[i]] == df[df.columns[i]].cat.categories[j]) & (df[y] == df[y].cat.categories[1])).sum()
            Vec[j] = np.array([[a,b]],dtype='float64')

        feature_split_num.append(Vec)

    return feature_split_num


# 数据集D的经验熵
def entropy(Di_vec):
    D = Di_vec.sum()
    if D == 0:
        p_vec = np.zeros(shape=(np.shape(Di_vec)))
    else:
        p_vec = Di_vec / D
    h_vec = np.array([])

    for p in p_vec:
        if p != 0:
            h = p * log(p,2)
            h_vec = np.append(h_vec,h)
        else:
            h_vec = np.append(h_vec,0)
    H = -(h_vec.sum())

    return (H)


# 特征A对数据集D的条件熵
def con_entroy(Di_vec,Aik_vec):
    H_Di = np.array([])
    P_Di = np.array([])
    for D_i in Aik_vec:
        H_Di = np.append(H_Di,entropy(D_i))
        P_Di = np.append(P_Di,(D_i.sum() / Di_vec.sum()))
    H_DA = (H_Di * P_Di).sum()

    return (H_DA)


# 特征A的信息增益
def gain(Di_vec,Aik_vec):
    gain = entropy(Di_vec) - con_entroy(Di_vec,Aik_vec)

    return (gain)


# 计算每个特征的信息增益，并取最大值
def gain_max(df,y):
    gain_vec = np.zeros(shape=((len(df.columns) - 1),1))

    feature_split_num = feature_split(df,y)

    # Y类别个数
    Di_vec = np.array(df[y].value_counts())

    # 计算各特征信息增益
    for i in np.arange(0,len(feature_split_num)):
        gain_vec[i] = gain(Di_vec,feature_split_num[i])

    # 选取信息增益最大的特征
    return [df.columns[gain_vec.argmax()],gain_vec.max()]


# 训练 ---------------------------------------------------------
def Decision_Tree(DTree,y,delta,max_class_in_D,par_description = ''):
    for key,value in DTree.items():

        subTree = {}

        if isinstance(value,pd.DataFrame):
            df = value

            # 判断是否信息增益达到阈值
            if (len(df.columns) - 1) >= 1 and gain_max(df,y)[1] >= delta:
                split_feature_name = gain_max(df,y)[0]

                for cat in np.unique(df[split_feature_name]):

                    df_split_temp = df[df[split_feature_name] == cat].drop(split_feature_name,axis=1)
                    description = ' '.join([str(split_feature_name),'=',str(cat)])

                    par_description = description

                    if (len(df_split_temp[y].unique()) != 1) and (df_split_temp.empty != True):

                        currentTree = {description: df_split_temp}
                        currentValue = Decision_Tree(currentTree,y,delta,max_class_in_D,par_description)

                        subTree.update(currentValue)

                    else:

                        if (len(df_split_temp[y].unique()) == 1):
                            leaf_node = df_split_temp[y].values[0]

                        if (df_split_temp.empty == True):
                            leaf_node = max_class_in_D

                        subTree.update({description: leaf_node})

            elif (len(df.columns) - 1) < 1:
                leaf_node = df[y].values[0]

                subTree = leaf_node

            elif gain_max(df,y)[1] < delta:
                leaf_node = max_class_in_D

                subTree = leaf_node

            DTree[key] = subTree

        else:
            print("Data is not a DataFrame!")

    return DTree


def ID3(data,y,delta=0.005):
    # 标准化数据集
    data = order_Y(data,y)
    y = 'label'

    DTree = {}

    max_class_in_D = data[y].value_counts().argmax()  # D中实例最大的类

    if gain_max(data,y)[1] >= delta :
        split_feature_name = gain_max(data,y)[0]

        # 初次分裂
        for cat in np.unique(data[split_feature_name]):

            # cat = 1
            data_split_temp = data[data[split_feature_name] == cat].drop(split_feature_name,axis=1)
            description = ' '.join([str(split_feature_name),'=',str(cat)])

            currentValue = data_split_temp

            if gain_max(data_split_temp,y)[1] < delta:
                currentValue = max_class_in_D

            if (len(data_split_temp[y].unique()) == 1):
                currentValue = data[y].values[0]

            if data_split_temp.empty == True:
                currentValue = max_class_in_D

            currentTree = {description: currentValue}
            DTree.update(currentTree)

    return Decision_Tree(DTree,y,delta,max_class_in_D)


# 预测 ---------------------------------------------------------
def most_leaf_node(tree):
    global leaf_node

    for value in tree.values():
        if isinstance(value,dict):
            most_leaf_node(value)
        else:
            leaf_node.append(value)

    return max(set(leaf_node),key=leaf_node.count)


def most_class(tree):
    leaf_node = []
    return most_leaf_node(tree)


def ID3_predict_one(DTree,row_data):
    for keys,values in DTree.items():
        T_key = keys
        T_value = values

        T_key_list = re.split('(=|<|<=|>|>=|!=)',T_key)
        split_feature = T_key_list[0].strip()
        split_feature_oper = T_key_list[1].strip()
        split_feature_value = T_key_list[2].strip()

        if str(row_data[split_feature]) == split_feature_value:
            if isinstance(T_value, dict):
                return ID3_predict_one(T_value, row_data)
            else:
                return T_value


def ID3_predict(DTree,new_data):
    predict_Y = []

    most_leaf = most_class(DTree)

    for row_data in new_data.iterrows():

        row_data_series = row_data[1]

        pre_y = ID3_predict_one(DTree, row_data_series)
        if pre_y == None:
            pre_y = most_leaf

        predict_Y.append(pre_y)

    return (predict_Y)

pre_Y = ID3_predict(model_DT, train_test)

# --------------------------------- 测试 -------------------------------------- #
# Kaggle Titanic Data
train = pd.read_csv('E:/GitHub/Algorithms/Data/train.csv')
train['set'] = 'train'

test = pd.read_csv('E:/GitHub/Algorithms/Data/test.csv')
test['Survived'] = np.full((test.shape[0], 1), 1, dtype=int)
test = test[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp','Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked']]
test['set'] = 'test'

data = pd.concat([train,test])

data = data.drop(['PassengerId','Name','Ticket','Cabin'],axis=1)

# 1
data.ix[:,'Survived'] = data.ix[:,'Survived'].astype('category')

# 2
data['Pclass'].value_counts()
data.ix[:,'Pclass'] = data.ix[:,'Pclass'].astype('category')

# 3
data['Sex'].value_counts()
data.Sex = np.where(data.Sex == "male",1,2)
data.ix[:,'Sex'] = data.ix[:,'Sex'].astype('category')

# 4
data['Age'] = data['Age'].fillna(np.mean(data['Age']))
data.Age = np.where(data.Age <= 10,1,
                    np.where(data.Age <= 20,2,
                             np.where(data.Age <= 30,3,
                                      np.where(data.Age <= 40,4,
                                               np.where(data.Age <= 50,5,6)))))
data.ix[:,'Age'] = data.ix[:,'Age'].astype('category')

# 5
data['SibSp'].value_counts()
data.ix[:,'SibSp'] = data.ix[:,'SibSp'].astype('category')

# 6
any(pd.isnull(data['Parch']))
data['Parch'].value_counts()
data.ix[:,'Parch'] = data.ix[:,'Parch'].astype('category')

# 7
pd.isnull(['Fare'])
data['Fare'] = data['Fare'].fillna(np.mean(data['Fare']))

data.Fare.describe()

data.Fare = np.where(data.Fare <= 7,1,
                     np.where(data.Fare <= 15,2,
                              np.where(data.Fare <= 32,3,
                                       np.where(data.Fare <= 50,4,
                                                np.where(data.Fare <= 80,5,6)))))
data.ix[:,'Fare'] = data.ix[:,'Fare'].astype('category')

# 8
any(pd.isnull(data['Embarked']))
data['Embarked'] = data['Embarked'].fillna(data.Embarked.value_counts()[0])
data.Embarked = np.where(data.Embarked == 'S',1,
                         np.where(data.Embarked == 'C',2,3))
data.ix[:,'Embarked'] = data.ix[:,'Embarked'].astype('category')



train = data[data['set']=='train']
train = train.drop(['set'],axis = 1)
test = data[data['set']=='test']
test = test.drop(['set','Survived'],axis = 1)

# ----------------
why_none = train_test.iloc[61]

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

train_train, train_test = train_test_split(train,test_size = 0.4, random_state=0)

model_DT = ID3(data=train_train, y='Survived', delta=0.005)

pre_Y = ID3_predict(model_DT, train_test)



pre_dt = pd.DataFrame({'Y':train_test['Survived'],'pre_Y':pre_Y})
pre_dt['Y'].cat.categories

pre_dt.ix[:,'pre_Y'] = pre_dt.ix[:,'pre_Y'].astype('category')
pre_dt['pre_Y'].cat.categories



roc_auc_score(pre_dt.Y, pre_dt.pre_Y)


pre_Y = ID3_predict(model_DT, test)
submit = pd.DataFrame({'PassengerId':np.arange(892,1310),'Survived':pre_Y})
submit.ix[:,'Survived'] = submit.ix[:,'Survived'].astype('category')
submit['Survived'].cat.categories

submit.to_csv('E:/GitHub/Algorithms/submit.csv',index = False)

