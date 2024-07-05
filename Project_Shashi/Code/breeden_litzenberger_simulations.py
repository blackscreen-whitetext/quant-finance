#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from scipy.stats import norm
import scipy
from scipy.interpolate import LinearNDInterpolator
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

today = '22_Jun_2024'
S_0 = 23501
r = 0.05

CALL_DATA = []
PUT_DATA = []
DATA = []
call_files = ['Calls_27_Jun_2024_NIFTY_50_23501.csv','Calls_04_Jul_2024_NIFTY_50_23501.csv','Calls_11_Jul_2024_NIFTY_50_23501.csv','Calls_18_Jul_2024_NIFTY_50_23501.csv','Calls_25_Jul_2024_NIFTY_50_23501.csv']
put_files =['Puts_27_Jun_2024_NIFTY_50_23501.csv','Puts_04_Jul_2024_NIFTY_50_23501.csv','Puts_11_Jul_2024_NIFTY_50_23501.csv','Puts_18_Jul_2024_NIFTY_50_23501.csv','Puts_25_Jul_2024_NIFTY_50_23501.csv']
for call_file,put_file in zip(call_files,put_files):
    calls = pd.read_csv(call_file)
    puts = pd.read_csv(put_file)
    
    puts1 = puts[puts["IV"] != '-']
    
    #puts1["IV"] = puts1["IV"].astype(float)
    #puts1.dtypes
    puts1 = puts1.reset_index(drop=True)
    for i in range(len(puts1)):
        puts1.loc[i, "STRIKE"] = float(puts1.loc[i, "STRIKE"].replace(',',""))
        puts1.loc[i, "BID"] = puts1.loc[i, "BID"].replace(',',"")
        if puts1.loc[i, "BID"] == "-":
            puts1.loc[i, "BID"] = float("inf")
        puts1.loc[i, "BID"] = float(puts1.loc[i, "BID"])
        puts1.loc[i, "ASK"] = puts1.loc[i, "ASK"].replace(',',"")
        if puts1.loc[i, "ASK"] == "-":
            puts1.loc[i, "ASK"] = "inf"
        puts1.loc[i, "ASK"] = float(puts1.loc[i, "ASK"])
        puts1.loc[i, "IV"] = float(puts1.loc[i, "IV"])
    

#     plt.plot(puts1["STRIKE"], puts1["IV"])
#     plt.xlabel("STRIKE")
#     plt.ylabel("PUT_IV")
#     plt.show()
    puts1["STRIKE"] = puts1["STRIKE"].astype(float)
    puts1["IV"] = puts1["IV"].astype(float)
    puts1["EXPIRY"]= (datetime.strptime(put_file[5:16],'%d_%b_%Y')-datetime.strptime(today,'%d_%b_%Y')).total_seconds()/(60*60*24)
    puts1["TYPE"] = "PUT"
    puts1["PRICE"] = (np.array(puts1["BID"].astype(float))+np.array(puts1["ASK"].astype(float)))/2
    
    PUT_DATA.append(puts1)
    DATA.append(puts1)
    calls1 = calls[calls["IV"] != '-']
    calls1 = calls1.reset_index(drop=True)
    #puts1["IV"] = puts1["IV"].astype(float)
    #puts1.dtypes
    for i in range(len(calls1)):
        calls1.loc[i, "STRIKE"] = float(calls1.loc[i, "STRIKE"].replace(',',""))
        calls1.loc[i, "BID"] = calls1.loc[i, "BID"].replace(',',"")
        if calls1.loc[i, "BID"] == "-":
            calls1.loc[i, "BID"] = float("inf")
        calls1.loc[i, "BID"] = float(calls1.loc[i, "BID"])
        calls1.loc[i, "ASK"] = calls1.loc[i, "ASK"].replace(',',"")
        if calls1.loc[i, "ASK"] == "-":
            calls1.loc[i, "ASK"] = float("inf")
        calls1.loc[i, "ASK"] = float(calls1.loc[i, "ASK"])
        calls1.loc[i, "IV"] = float(calls1.loc[i, "IV"])

#     plt.plot(calls1["STRIKE"], calls1["IV"])
#     plt.xlabel("STRIKE")
#     plt.ylabel("CALL_IV")
#     plt.show()
    calls1["STRIKE"] = calls1["STRIKE"].astype(float)
    calls1["IV"] = calls1["IV"].astype(float)
    calls1["EXPIRY"]= (datetime.strptime(call_file[6:17],'%d_%b_%Y')-datetime.strptime(today,'%d_%b_%Y')).total_seconds()/(60*60*24)
    calls1["TYPE"] = "CALL"
    calls1["PRICE"] = (np.array(calls1["BID"].astype(float))+np.array(calls1["ASK"].astype(float)))/2
    CALL_DATA.append(calls1)
    DATA.append(calls1)
#print(CALL_DATA,PUT_DATA)
CALL_DATA = pd.concat(CALL_DATA,axis = 0).reset_index(drop=True)
PUT_DATA = pd.concat(PUT_DATA,axis = 0).reset_index(drop=True)
#print(PUT_DATA["EXPIRY"][0])
DATA = pd.concat(DATA,axis = 0).reset_index(drop=True)
#print(CALL_DATA["STRIKE"][0])
#DATA
#print(PUT_DATA)
def der2_x(price,T,K):
  ds = 1
  return (price(T,K+ds)-2*price(T,K)+price(T,K-ds))/(ds*ds)
def bsmcall(vol,T,K):
    T = T/365
    dp = (1/vol*T**0.5)*(np.log(S_0/K)+(r+0.5*vol**2)*T)
    dm = (1/vol*T**0.5)*(np.log(S_0/K)+(r-0.5*vol**2)*T)
    pk = S_0*norm.cdf(dp)-K*np.exp(-r*T)*norm.cdf(dm)
    return pk
def bsmput(vol,T,K):
    T = T/365
    dp = (1/vol*T**0.5)*(np.log(S_0/K)+(r+0.5*vol**2)*T)
    dm = (1/vol*T**0.5)*(np.log(S_0/K)+(r-0.5*vol**2)*T)
    pk = K*np.exp(-r*T)*norm.cdf(-dm)-S_0*norm.cdf(-dp)
    return pk
def call_price(ivs):
  return lambda T,K: bsmcall(ivs(T,K),T,K) 
def put_price(ivs):
  return lambda T,K: bsmput(ivs(T,K),T,K)
call_iv = DATA["IV"]
call_strike = DATA["STRIKE"]
call_expiry = DATA["EXPIRY"]
call_ivs= lambda T,K: LinearNDInterpolator(list(zip(call_expiry,call_strike)), list(call_iv))(T,K)/100
put_iv = PUT_DATA["IV"]
put_strike = PUT_DATA["STRIKE"]
put_expiry = PUT_DATA["EXPIRY"]
put_ivs= lambda T,K: LinearNDInterpolator(list(zip(put_expiry,put_strike)), list(put_iv))(T,K)/100
def pdf(T):
    return lambda S: der2_x(call_price(call_ivs),T,S) if S >= S_0 else -der2_x(put_price(put_ivs),T,S)
def cdf(pdf,stock):
    return scipy.integrate.quad(pdf,-np.inf,stock)
def sim_stock(T,q): #q- number of simulations, T- time to maturity
    PDF = pdf(T)
    simulations = [scipy.optimize.fsolve(lambda stock:cdf(PDF,stock)-uni , S_0) for uni in np.random.uniform(size = q)]
    return simulations
#print(sim_stock(5,10))

