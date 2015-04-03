import numpy as NP
#import SymbolData
from skimage.morphology import disk
from skimage.filters import rank
from sklearn import preprocessing
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# This is a skeleton of a file that will contain functions for various features.

def features(symbols):
    return list(map ( (lambda symbol: symbolFeatures(symbol)), symbols))



# Linear Interpolation
def interp( x12, y12, t):
    x = x12[0] * (1- t) + x12[1] * t
    y = y12[0] * (1 -t) + y12[1] * t
    return (x, y)

# Create an image from a symbol
def getImg(symbol):
       xs = NP.array([])
       ys = NP.array([])

       for i in range(len(symbol.strokes)):
           for j in range(len(symbol.strokes[i].xs)-1):
               for t in NP.linspace(0,1,30):
                   x,y = interp(symbol.strokes[i].xs[j:j+2],symbol.strokes[i].ys[j:j+2],t)
                   xs = NP.append(xs,x)
                   ys = NP.append(ys,y)
       I = NP.zeros((max(symbol.ys())+1,max(symbol.xs())+1))

       for i in range(len(xs)):
           I[max(symbol.ys())-int(ys[i])][int(xs[i])] = 1

       I = rank.mean(I, selem=disk(1))
       
       for i in range(I.shape[0]):
           for j in range(I.shape[1]):
               if(I[i][j]>0.5):
                   I[i][j]=1
       return I

# Show image for the symbol
def showImg(symbol):
    plt.figure()
    I = getImg(symbol)
    plt.imshow(I)
    plt.gray()
    plt.show()
    
# Get the features from a symbol
def symbolFeatures(symbol, n_pca = None):
    f = NP.array([])
    
    #Call feature functions here like so:
    f = NP.append(f,xmean(symbol))
    f = NP.append(f,ymean(symbol))
    f = NP.append(f,xvar(symbol))
    f = NP.append(f,yvar(symbol))
    I = getImg(symbol)
    fkiFeat = getFKIfeatures(I)
    fki = getMeanStd(fkiFeat)
    f = NP.append(f,fki)

    #the minimum, basic scaling needed for many classifiers to work corectly.
    f_scaled = preprocessing.scale(f)
    # would have put PCA here, but that doesn't play nice with the way it needs to be used.
    return f_scaled

# Some really simple global properties to start us off.
    
def xmean(symbol):
    return [NP.mean(symbol.xs())]

def ymean(symbol):
    return [NP.mean(symbol.ys())]

def xvar(symbol):
    return [NP.var(symbol.xs())]

def yvar(symbol):
    return [NP.var(symbol.ys())]

## FKI Features 
def getFKIfeatures(I):
    [H,W] = I.shape
    c4ant = H+1
    c5ant = 0
    f = NP.zeros((W,9)) # 
    for x in range(W):
        c1=0; c2=0; c3=0; c4=H+1; c5=0; c6=H+1; c7=0; c8=0; c9=0;
        for y in range(H):
            if(I[y][x]==1):
                c1+=1       # number of white pixels in the column
                c2+=y       # center of gravity of the column
                c3+=y**2    # second order moment of the column
                if(y<c4):
                    c4=y    # position of the upper contour in the column
                if(y>c5):
                    c5=y    # position of the lower contour in the column
            if(y>1 & I[y-1][x]!= I[y-2][x]):
                c8+=1       # Number of black-white transitions in the column
        
        c2 /= H
        c3 /= H**2
        
        for y in range(c4+1,c5):
            if(I[y][x]==1):
                c9+=1       # Number of white pixels between the upper and lower contours
        
        if(x+1<W):
            for y in range(H):
                if(I[y-1][x+1]==1):
                    if(y<c6):
                        c6=y     
                    if(y>c7):
                        c7=y
                    
        c6 = (c6-c4ant)/2 # Orientation of the upper contour in the column
        c7 = (c7-c5ant)/2 # Orientation of the lower contour in the column
        c4ant = c4
        c5ant = c5
        f[x] = NP.array([c1,c2,c3,c4,c5,c6,c7,c8,c9])
    return f

## Get Mean and Variance of FKI features
def getMeanStd(f):
    mean = NP.mean(f, axis=0)
    std = NP.std(f, axis=0)
    feat = NP.append(mean,std)
    return(feat)
    
## RWTH Features
#def getRWTHfeatures(I,w):
#    [W,H] = I.shape
#    for i in range(W):
        