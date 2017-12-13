#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 14:23:44 2017

@author: hiske
"""
import numpy as np
import re
from dataClass import data


def createParamDict(content, iStart, iEnd):
    targetDict = {}
    for i in range(iStart, iEnd):
        if content[i][1] is not '*':
            [key, value] = content[i].strip().rsplit(':', 1)
            key = key.lstrip('\\')
            value = value.strip()
            targetDict[key] = value
    return(targetDict)


def getParameters(filePath):
    with open(filePath, "r", errors='ignore') as dataFile:
        content = dataFile.readlines()
    # identify separate image files
    index = [x for x in range(len(content))
             if content[x].strip() == "\*Ciao image list"
             or content[x].strip() == "\*File list end"]
    # read in general settings dictionary
    general = createParamDict(content, 0, index[0])
    channelInfo = []
    # read in chanel settings dictionary
    for i in range(0, len(index)-1):
        channelInfo.append(createParamDict(content, index[i], index[i+1]))
    return(general, channelInfo)


def getData(filePath, offset, length, nLines, nPoints):
    with open(filePath, "rb") as cc:
        cc.seek(offset)
        channelData = np.fromstring(cc.read(length), np.int16).astype(float)
        channelData = np.array(np.reshape(channelData, (nLines, nPoints)))
        return(channelData)


def createChannelDict(filePath):
    # read in dictionary with general settings
    # and list of dictionaries with channel settings
    general, channelInfo = getParameters(filePath)
    # extract relevant parameters from general settings dictionary
    extent = float(general['Scan Size'].split()[0])
    extentUnit = general['Scan Size'].split()[1]
    nLines = int(general['Lines'])
    nPoints = int(general['Samps/line'])
    Zsens = float(general['@Sens. ZsensSens'].split()[-2])
    ZsensUnit = general['@Sens. ZsensSens'].split()[-1]
    # extract data from channel settings dictionary
    channels = {}
    for channel in channelInfo:
        channelName = channel['@2:Image Data']
        channelName = re.findall(r'"([^"]*)"', channelName)[0]
        offset = int(channel['Data offset'])
        length = int(channel['Data length'])
        channelData = getData(filePath, offset, length, nLines, nPoints)
        obj = channel['@2:Z scale'].split(')')[1]
        conversionFactor = obj.split()
        factor = float(conversionFactor[0])
        if len(conversionFactor) > 1:
            factorUnit = conversionFactor[1]
        if factorUnit == 'mV':
            factor *= 1e-3
            factorUnit = 'V'
        channelData *= factor/2**16
        if factorUnit == 'V':
            channelData *= Zsens
            channelUnit = ZsensUnit.split('/')[0]
        else:
            channelUnit = 'deg'
        channelData = data(channelData, u=channelUnit)
        channels[channelName] = channelData
    return(channels, extent, extentUnit)
