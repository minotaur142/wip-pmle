#helper functions
import numpy as np
import pandas as pd

def add_constant(X):
    if isinstance(X, np.ndarray):
        intercept = np.ones((X.shape[0], 1))
        X = np.concatenate((intercept, X), axis=1)
    elif isinstance(X, pd.DataFrame):
        intercept = pd.Series(1,name='const',index=X.index)
        X = pd.concat([intercept,X],axis=1)
    else:
        raise TypeError("Data must be pandas dataframe or numpy array")
    return X

def sigmoid_pred(X, weights):
    z = np.dot(X,weights)
    sig =  1/(1 + np.exp(-1*z))
    sig = np.clip(sig,.000001,.999999)
    return sig

def hat_diag(X,weights):
    Xt = X.transpose()

    #Get diagonal of error
    y_pred = sigmoid_pred(X,weights)
    W = np.diag(y_pred*(1-y_pred))

    #Calculate Fisher Information Matrix
    I = np.linalg.multi_dot([Xt,W,X]) 
    
    #Get Diagonal of Hat Matrix
    hat = np.linalg.multi_dot([W**0.5,X,np.linalg.inv(I),Xt,W**0.5])
    hat_diag = np.diag(hat)
    return hat_diag

def return_full_rank(A):
    det = np.linalg.det(A)
    if det == 0:
        factorization = np.linalg.qr(A)[1]
        zeros = np.zeros(A.shape[1])
        not_redundant = [row for row in range(factorization.shape[0])\
                         if sum(factorization[row,:]!=zeros)==0]
        return A[not_redundant]

def information_matrix(X,weights):
    Xt = X.transpose()

    #Get diagonal of error
    y_pred = sigmoid_pred(X,weights)
    W = np.diag(y_pred*(1-y_pred))

    #Calculate Fisher Information Matrix
    I = np.linalg.multi_dot([Xt,W,X])
    return I

def predict_proba(X,weights):
    preds = sigmoid_pred(X,weights)
    return preds

def predict(X,weights):
    preds = sigmoid_pred(X,weights).round()
    return preds

def FLIC(X,weights):
    eta = np.dot(X,weights)
    target = y-eta
    b0_model = sm.OLS(target,np.ones(y.shape[0])).fit()
    b0 = b0_model.params[0]
    weights = np.insert(weights,0,b0)
    return weights

def FLAC_aug(X,y,weights):
    init_rows = X.shape[0]
    hat_diag = hat_diag(X,weights)
    aug_sample_weights = pd.Series(np.concatenate([np.ones(init_rows),hat_diag/2,hat_diag/2]))

    X = X.append(X).append(X)
    X['pseudo_data']=0
    X['pseudo_data'][init_rows:]=1
    y = y.append(y).append(1-y)
    X.const[init_rows:] = 0
    return X, y, aug_sample_weights
                        
def FLAC_pred_aug(X):
    init_rows = X.shape[0]
    X['pseudo_data']=0
    return X

def LU_inv(A):
    n = A.shape[0]
    id_matrix = np.identity(n)
    L, U = scipy.linalg.lu(A,permute_l=True)
    inv = np.ones([n,n])
    for col in range(n):
        z = np.linalg.solve(L,id_matrix[:,col])
        x = np.linalg.solve(U,z)
        inv[:,col] = x
    return inv