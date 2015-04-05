import numpy as NP
#import SymbolData
from skimage.morphology import disk, binary_closing
from skimage.filter import rank
from skimage.transform import rescale
from sklearn import preprocessing
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import pickle

# This is a skeleton of a file that will contain functions for various features.

def features(symbols):
    return list(map ( (lambda symbol: symbolFeatures(symbol)), symbols))

# Linear Interpolation
#def interp( x12, y12, t):
#    x = x12[0] * (1- t) + x12[1] * t
#    y = y12[0] * (1 -t) + y12[1] * t
#    return (x, y)

# Create an image from a symbol
#def getImg(symbol):
#       xs = NP.array([])
#       ys = NP.array([])
#
#       for i in range(len(symbol.strokes)):
#           for j in range(len(symbol.strokes[i].xs)-1):
#               for t in NP.linspace(0,1,30):
#                   x,y = interp(symbol.strokes[i].xs[j:j+2],symbol.strokes[i].ys[j:j+2],t)
#                   xs = NP.append(xs,x)
#                   ys = NP.append(ys,y)
#       I = NP.zeros((round(max(symbol.ys()))+1,round(max(symbol.xs()))+1))
#
##       assert(len(xs)==len(ys))
#       for i in range(len(xs)):
#           I[max(symbol.ys())-round(ys[i])][round(xs[i])] = 1
#
#       I = rank.mean(I, selem=disk(1))
#       
#       for i in range(I.shape[0]):
#           for j in range(I.shape[1]):
#               if(I[i][j]>0.5):
#                   I[i][j]=1
#       print("getimg: ", i, " ", j)
#       return I

def getImg(symbol):
    I = Image.new("L",(round(max(symbol.xs()))+1,round(max(symbol.ys()))+1))
    for stroke in symbol.strokes:
        p = stroke.asPoints()
        draw = ImageDraw.Draw(I)
        draw.line(p,fill=255)  
    img = NP.asarray(list(I.getdata()))
    img = NP.reshape(img,(I.size[1],I.size[0]))
    img = img/img.max()
    img = rank.mean(img, selem=disk(1))
    img = binary_closing(img,selem=disk(1))
    img = img/img.max()
    scale = max(img.shape)/img.shape[0]
    if(scale!=1):
        img = rescale(img,scale)
    img[img>=0.5] = 1
    img[img<0.5] = 0
    return(img)

# Show image for the symbol
def showImg(symbol):
    plt.figure()
    I = NP.flipud(getImg(symbol))
    plt.imshow(I)
    plt.gray()
    plt.show()
    
# Get the features from a symbol
def symbolFeatures(symbol):
    f = NP.array([])
    
    #Call feature functions here like so:
#    f = NP.append(f,xmean(symbol))
#    f = NP.append(f,ymean(symbol))
##    f = NP.append(f,xvar(symbol))
##    f = NP.append(f,yvar(symbol))
#    f = NP.append(f,getStatFeatures(symbol))
#    f = NP.append(f,numstrokes(symbol))    
    
    I = getImg(symbol)
#    fkiFeat = getFKIfeatures(I)
#    fki = getMeanStd(fkiFeat)
#    f = NP.append(f,fki)
    RWTHFeat = getRWTHfeatures(I,5,30)
    RWTH = getMeanStd(RWTHFeat)
    f = NP.append(f,RWTH)
#    f = NP.append(f,aspratio(I))
    
    #the minimum, basic scaling needed for many classifiers to work corectly.
    f_scaled = preprocessing.scale(f)
    # would have put PCA here, but that doesn't play nice with the way it needs to be used.
    return f_scaled

# Some really simple global properties to start us off.
    
def xmean(symbol):
    return [NP.mean(symbol.xs())]

def ymean(symbol):
    return [NP.mean(symbol.ys())]

#def xvar(symbol):
#    return [NP.var(symbol.xs())]
#
#def yvar(symbol):
#    return [NP.var(symbol.ys())]

def aspratio(I):
    return [I.shape[0]/I.shape[1]]
    
def numstrokes(symbol):
    return[len(symbol.strokes)]

def getStatFeatures(symbol):
    pts = NP.asarray(symbol.points()).T
    f = NP.array([])
    
    if pts.shape[1] > 1:
        cov = NP.cov(pts)
        eig = NP.linalg.eig(cov)
        ind = NP.argsort(eig[0])
        eigVal = eig[0][ind]
        eigVec = eig[1].T
        eigVecSort = eigVec[ind]
        f = NP.append(f,cov[0])
        f = NP.append(f,cov[1][1])
        f = NP.append(f,eigVal)
        f = NP.append(f,eigVecSort)
    else:
        f = NP.zeros((9))
    
    return f
    
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
            if(y>1):
                if(I[y-1][x]!= I[y-2][x]):
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


## RWTH Features
def getRWTHfeatures(I,w,dim):
    [H,W] = I.shape
    if(W<w):        #prevent error for very small width images
        w = W

    if(W<2 and H<30):   #if the image is less than the feature dimentsion
        f = NP.zeros((w*H,30))
    else:
        win = NP.zeros((W-w+1,H*w))

        for i in range(W-w+1):
        #Vertical repositioning
            y = NP.arange(H)
            y = NP.reshape(y,(H,1))
            y = NP.repeat(y,w,axis=1)
            vCtr = NP.sum(NP.multiply(y,I[:,i:i+w]))
            n = NP.count_nonzero(I[:,i:i+w])
            if n==0:
                vCtr = H/2
            else:
                vCtr /= n       # Vertical centeroid
            vCtr = round(vCtr)
            J = NP.zeros((H,w))
            if (vCtr-H/2)>=0:
                J[0:3*H/2-vCtr,:] = I[vCtr-H/2:,i:i+w]
            else:
                J[H/2-vCtr:,:] = I[0:H/2+vCtr,i:i+w]
            win[i] = NP.reshape(J,(1,J.size))

        pca = PCA(n_components=dim)
        pca.fit(win)
        f = pca.components_
        f = f.T
    return(f)


## Get Mean and Variance of features
def getMeanStd(f):
    mean = NP.mean(f, axis=0)
    std = NP.std(f, axis=0)
    feat = NP.append(mean,std)
    return(feat)
    

def pickleFeatures(feat, filename):
    with open(filename, 'wb') as f:
        pickle.dump(feat, f, pickle.HIGHEST_PROTOCOL)
        #note that this may cause problems if you try to unpickle with an older version.


def unpickleFeatures(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
