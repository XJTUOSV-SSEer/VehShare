#此版本未解决zfill问题

import numpy as np
import time
import sys
import datetime
import os
from scipy.sparse import csr_matrix
import re
import random
import hmac
import random
import pickle
from Crypto.Cipher import AES
import json
import string
from web3 import Web3
import json
from bplib import bp
import secrets
import math
import hmac
import hashlib
import gmpy2
from gmpy2 import mpz
import os
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
# readFileDir = "/home/node4/yangxu/ICC20/rangeStreaming/testdata/"
readFileDir = "/home/node4/yangxu/wow/rangeStreaming/dataset_4K/" # 文件路径



storage = 0
subs = os.listdir(readFileDir)
# RDH参数
g=mpz(2141434891434191460597654106285009794456474073127443963580690795002163321265105245635441519012876162226508712450114295048769820153232319693432987768769296824615642594321423205772115298200265241761445943720948512138315849294187201773718640619332629679913150151901308086084524597187791163240081868198195818488147354220506153752944012718951076418307414874651394412052849270568833194858516693284043743223341262442918629683831581139666162694560502910458729378169695954926627903314499763149304778624042360661276996520665523643147485282255746183568795735922844808611657078638768875848574571957417538833410931039120067791054495394347033677995566734192953459076978334017849678648355479176605169830149977904762004245805443987117373895433551186090322663122981978369728727863969397652199851244115246624405814648225543311628517631088342627783146899971864519981709070067428217313779897722021674599747260345113463261690421765416396528871227)
p=mpz(3268470001596555685058361448517594259852327289373621024658735136696086397532371469771539343923030165357102680953673099920140531685895962914337283929936606946054169620100988870978124749211273448893822273457310556591818639255714375162549119727203843057453108725240320611822327564102565670538516259921126103868685909602654213513456013263604608261355992328266121535954955860230896921190144484094504405550995009524584190435021785232142953886543340776477964177437292693777245368918022174701350793004000567940200059239843923046609830997768443610635397652600287237380936753914127667182396037677536643969081476599565572030244212618673244188481261912792928641006121759661066004079860474019965998840960514950091456436975501582488835454404626979061889799215263467208398224888341946121760934377719355124007835365528307011851448463147156027381826788422151698720245080057213877012399103133913857496236799905578345362183817511242131464964979)
q=mpz(93911948940456861795388745207400704369329482570245279608597521715921884786973)
S = {} # 状态表(w ---> st)
N = {} # 计数器表(w ---> c)
# AIhex=hex(int(5))
# AIhex=AIhex[2:]
# AItian="0x"+"0"*(768-len(AIhex))+AIhex
# print(AItian)
# AIhex=hex(int(2))
# AIhex=AIhex[2:]
# AItian="0x"+"0"*(768-len(AIhex))+AIhex
# print(AItian)

def strIsSmaller(abit,bbit):
    sabit = abit
    sbbit = bbit
    if(sabit[0] == ' '):
        sabit = sabit[1:]
    if(sbbit[0] == ' '):
        sbbit = sbbit[1:]

    for i in range(len(sabit)):
        if(sabit[i]<sbbit[i]):
            return True
        if(sabit[i]>sbbit[i]):
            return False
    
    return False

def stradd(abit,num):
    sabit = abit
    if(sabit[0] == ' '):
        sabit = sabit[1:]
    sabit_len = len(sabit)
    a = int(sabit,2)
    x = pow(2,sabit_len)
    a = (a+num)%x
    sabit = bin(a)[2:]
    while(len(sabit)<sabit_len):
        sabit = '0'+sabit
    # print(sabit)
    return ' '+sabit


def GetOBRC(Tr,d):
    res = []
    result= []
    a = '0'
    b = Tr
    abit = bin(int(a,10))
    bbit = bin(int(b,10))
    abit = abit[2:]
    bbit = bbit[2:]
    while(len(abit)<d):
        abit = '0'+abit
    while(len(bbit)<d):
        bbit = '0'+bbit
    # print(abit)
    # print(bbit)
    abit = ' '+abit
    bbit = ' '+bbit
    while(strIsSmaller(abit,bbit)):
        if(abit[-1] == '1'):
            res.append(abit)
        if(bbit[-1] == '0'):
            res.append(bbit)
        abit = stradd(abit,1)
        bbit = stradd(bbit,-1)
        abit = abit[:-1]
        bbit = bbit[:-1]
    if(abit == bbit):   res.append(abit)
    
    for i in res:
        i=''.join(i.split())
        strr = i.ljust(d,'*')
        result.append(strr)
    
    return result


########### 文件解析 ##########
# [输入] 1：路径(str)
#        2: 文件名(str) 
#        3: 倒排索引(dic)
# [输出] 无
################################
def fileParser(dir,fileid,dic):
    wordset = []
    wordlist = []
    path = dir+fileid


    with open(path,"r") as f:
        for line in f.readlines():
            wordset = line.split(",")
    # print("fileID",fileid)
    # print(wordset)

    for word in wordset:
        if word not in wordlist:
            wordlist.append(word)
            if word not in dic:
                dic[word] = []
                # dic[word] = [str(fileid).zfill(16)]
                dic[word].append(str(fileid))
                # st=os.urandom(16)    #生成16位byte
                # dic[word].insert(0,st)
            else:
                dic[word].append(str(fileid))

########### 初始化阶段 ##########
# [输入] 无
# [输出] 1: owner密钥G_o(int)
#        2: user密钥G_u_1(int)
#        3: user密钥G_u_2(int)
#        4: owner密钥k1(bytes)
#        5: owner密钥k2(bytes)
################################
def setup():
	owner_ID='owner1'  # 初始化owner ID
	owner_ID=owner_ID.encode('utf-8') # owner ID 转字节

	k1=hmac.new(b'owner1').digest() # K1 长度16
	k2=hmac.new(b'owner2').digest() # K2 长度16
	k3=hmac.new(b'owner3').digest() # K3 长度16

	G_o = hmac.new(k3, owner_ID, digestmod=hashlib.sha256).digest() # G_o <--- F(k3, id_o)
	
	G_o=int.from_bytes(G_o, byteorder='big')  # G_o 转字节 

	user_ID='user1' # 初始化user ID
	user_ID=user_ID.encode('utf-8') # user ID 转字节

	user_key_1=hmac.new(b'user_1').digest() # 生成user密钥 k_u_1
	user_key_2=hmac.new(b'user_2').digest() # 生成user密钥 k_u_2 长度16

	G_u_1 = hmac.new(user_key_1, user_ID, digestmod=hashlib.sha256).digest() # G_u_1 <--- F(k_u_1, id_u) 长度32
	G_u_2 = hmac.new(user_key_2, user_ID, digestmod=hashlib.sha256).digest() # G_u_2 <--- F(k_u_2, id_u)

	G_u_1=int.from_bytes(G_u_1, byteorder='big') # G_u_1 转字节
	G_u_2=int.from_bytes(G_u_2, byteorder='big') # G_u_2 转字节

	temp1 = gmpy2.invert(G_u_2, q) # G_u_2 求逆 
	temp2 = ((mpz(G_o) % q) * (mpz(temp1) % q)) % q 
	AI = gmpy2.powmod(g, temp2, p) # 计算 AI_o->u 
	
	AIhex=hex(int(AI))

	store_var_contract.functions.set_AL(G_u_1,AIhex).transact({#32 384
		"from": from_account,
		"gas": 3000000,
		"gasPrice": 0,
	})
	return G_o,G_u_1,G_u_2,k1,k2#Update需要这些值

# def update(Kw_File_Use,G_o,op,k1,k2,TimeString):

# 	for w in Kw_File_Use.keys():
# 		TFP_pair = [] #用于存放T f P
# 		#AES加密
# 		model = AES.MODE_ECB
# 		aes = AES.new(k2, model) 
		
# 		f = aes.encrypt(TimeString.zfill(16).encode('utf-8'))  #f最终结果
# 		print(f)
# 		TFP_pair.append(TimeString.encode())
# 		TFP_pair.append(f)
# 		# print(type(w))
# 		kw = w.encode('utf-8') # w转字节
# 		h1 = hmac.new(kw).digest() # 计算h <--- H1(w) 长度16
# 		h1 = int.from_bytes(h1, byteorder='big') # w 转 大数

# 		temp = ((mpz(h1) % q) * (mpz(G_o) % q)) % q # H1(w) * Go
# 		h = gmpy2.powmod(g, temp, p) # 计算 h <--- g^(H1 * G_o)
# 		Hhex=hex(int(h))

# 		t = Web3.keccak(hexstr=Hhex)#计算
# 		# t_lable = t_lable.encode('utf-8')
# 		st_1=hmac.new(b'st_1').digest()#预定义
# 		global N
# 		if N.get(kw) == None:
# 			N[kw] = np.size(Kw_File_Use[w])
# 		else:
# 			N[kw] += np.size(Kw_File_Use[w])
# 		print(kw,"的index个数为",N[kw])
# 		store_var_contract.functions.set_N(t,N[kw]).transact({
# 			"from": from_account,
# 			"gas": 3000000,
# 			"gasPrice": 0,
# 		})
# 		for ind in Kw_File_Use[w]:
# 			vc_pair = []
# 			# print(ind)
# 			#对于一个ind
# 			global S
# 			if S.get(kw) == None:
# 				st_1=hmac.new(b'st_1').digest()
# 			else:
# 				st_1 = S[kw]
			
# 			#暂时设置的随机性
# 			st = secrets.randbelow(100)
# 			st = hmac.new(str(st).encode()).digest()
# 			S[kw] = st
# 			l = Web3.keccak(("0".encode()+st ).zfill(32))
# 			l = Web3.keccak(("0".encode()+st ).zfill(32))#保证时间
			
# 			v1 = (st_1).zfill(32)
# 			v0 = Web3.keccak(("1".encode()+st ).zfill(32))
# 			# print('------------------- v1 -----------------')
# 			# print(v1)
# 			# print('------------------- v1[0] -----------------')
# 			# print(v1[12])

# 			# #这部分时间应该减去
# 			# while(v1[0]!=48):#防止zfill生成错误
# 			# 	v1 = ((ind+"and").encode()+st_1).zfill(32)
			
# 			v = bytes(a ^ b for a,b in zip(v0,v1))
# 			vc_pair.append(v)

# 			#对称加密求出c
# 			aes1 = AES.new(k1, model)
# 			c = aes1.encrypt((op+ind).zfill(16).encode())
# 			# print(c)
# 			vc_pair.append(c)

# 			store_var_contract.functions.set_I(l,vc_pair).transact({#32 数组
# 				"from": from_account,
# 				"gas": 3000000,
# 				"gasPrice": 0,
# 			}) 
		
# 		t = Web3.keccak(hexstr=Hhex)#测时间专用
# 		P = bytes(a ^ b for a,b in zip(t,st.zfill(32)))#p前面已经有定义是大数 改用P
# 		TFP_pair.append(P)

# 		store_var_contract.functions.set_I(t,TFP_pair).transact({#32 32
# 			"from": from_account,
# 			"gas": 3000000,
# 			"gasPrice": 0,
# 		})


########### 更新阶段 ##########
# [输入] 1: 倒排索引Kw_File_Use(dic)
#        2: owner密钥G_o(int)
#        3: 操作符op(str)
#        4: owner密钥k1(bytes)
#        5: owner密钥k2(bytes)
#        6: 更新时间戳TimeString(str)
# [输出] 发送信息给只能合约进行存储
##############################
def update(Kw_File_Use,G_o,op,k1,k2,TimeString):
	global N,S,storage

	Nkw_batch=[] #用于存放 index Numbersum

	t_batch=[] # byte类型t列表
	TFP_pair = [] # byte类型(T,f,P)列表
	lent = 0 # t数量计数器

	l_batch = [] # byte类型l列表
	vc_pair = [] # byte类型(v,c)列表
	lenl = 0 # l数量计数器

	for w in Kw_File_Use.keys(): # 遍历每个关键字
		storage = storage + 4
		model = AES.MODE_ECB # AES加密model
		aes = AES.new(k2, model) # AES加密密钥
		f1 = TimeString.zfill(16).encode('utf-8')
		while f1[0]!=48: #############################################
			print(11111111111111111111111)
			f1 = TimeString.zfill(16).encode('utf-8')
			# print(f1)
		f = aes.encrypt(f1) # 计算 f <--- F(k_o^2,T)
		# print(f)
		TFP_pair.append(TimeString.encode()) # 将byte类型T放入TFP_pair_batch中
		TFP_pair.append(f) # 将byte类型f放入TFP_pair_batch中
		# print(type(w))
		kw = w.encode('utf-8') # w转字节
		h1 = hmac.new(kw).digest() # 计算h <--- H1(w) 长度16
		h1 = int.from_bytes(h1, byteorder='big') # w转大数

		temp = ((mpz(h1) % q) * (mpz(G_o) % q)) % q # H1(w) * G_o
		h = gmpy2.powmod(g, temp, p) # 计算 h <--- g^(H1 * G_o)
		Hhex=hex(int(h)) # h转16进制hex

		t = Web3.keccak(hexstr=Hhex) # 计算 t<--- H2(h)
		# t_lable = t_lable.encode('utf-8')
		st_1=hmac.new(b'st_1').digest()#第一次时的定义

		#维护N index

		if N.get(kw) == None:
			N[kw] = np.size(Kw_File_Use[w]) # 获取关键字对应ind数量
		else:
			N[kw] += np.size(Kw_File_Use[w]) # 更新关键字对应ind数量
		# print(kw,"的index个数为",N[kw])
		
		Nkw_batch.append(N[kw]) # 将int类型N[kw]放入Nkw_batch中
		lent += 1 # l的数量增加

		for ind in Kw_File_Use[w]: # 遍历关键字w对应的每个ind
			storage = storage + 3
			# 维护状态表S[w] = st
			if S.get(kw) == None:
				st_1=hmac.new(b'st_1').digest() # 初始化上一个状态st_1
			else:
				st_1 = S[kw] # 获取上一个状态st_1
			
			#暂时设置的随机性
			st = secrets.randbelow(10000000) # 随机生成当前状态st 
			st = hmac.new(str(st).encode()).digest() # l <--- H3(st)
			S[kw] = st # 更新状态表

			l1 = "0".encode()*16+st # 填充st
			while(l1[0]!=48):#防止zfill生成错误
				print(2222222222222222222222222)
				l1 = "0".encode()*16+st
			
			l = Web3.keccak(l1) # 计算 l <--- H3(st)
			
			v1 = "0".encode()*16+st_1 # 填充st_1
			while(v1[0]!=48):
				print(33333333333333333333333333)
				v1 = "0".encode()*16+st_1 # 填充st_1
			# print(len(st_1))
			# print(v1)
			# print(v1[0])
			# while(v1[0]!=48):
			# 	v1 = (st_1).zfill(32)
			# 	print(st_1)
			# 	print(v1)
			# 	print(v1[0])
			
			v0_temp = ("1".encode()+st ).zfill(32) # 计算1||st
			while(v0_temp[0]!=48):
				print(555555555555555555555)
				v0_temp = ("1".encode()+st ).zfill(32)
			v0 = Web3.keccak(v0_temp) # 计算 H3(1||st)


			# print('------------------- v1 -----------------')
			# print(v1)
			# print('------------------- v1[0] -----------------')
			# print(v1[12])

			# #这部分时间应该减去
			# while(v1[0]!=48):#防止zfill生成错误
			# 	v1 = ((ind+"and").encode()+st_1).zfill(32)
			
			v = bytes(a ^ b for a,b in zip(v0,v1)) # 计算 v <--- H3(st|1) \oplus st^{-1}
			vc_pair.append(v) # 将byte类型v放入vc_pair中

			#对称加密求出c
			aes1 = AES.new(k1, model) # AES加密密钥
			c = (op+ind).encode().zfill(16) # 填充 op||ind
			while(c[0]!=48): # 防止zfill生成错误
				print(4444444444444444444444444444)
				c = (op+ind).encode().zfill(16)
			# print(c)
			c = aes1.encrypt(c) # AES加密，计算 c <--- Enc(k_o, op||ind)
			vc_pair.append(c) # 将byte类型c放入vc_pair中
			l_batch.append(l) # 将byte类型l放入l_batch中
			lenl += 1 # 更新l数量计数器

		# t = Web3.keccak(hexstr=Hhex)#测时间专用
		t_batch.append(t) # 将byte类型t放入t_batch中
		# print(t)
		st1 = "0".encode()*16+st # 填充st
		# print(st1)
		# while(st1[0]!=48):#防止zfill生成错误
		# 	st1 = st.zfill(32)
		P = bytes(a ^ b for a,b in zip(t,st1)) # 计算P <--- H4(h) \oplus st
		TFP_pair.append(P)  # 将byte类型P放入TFP_pair_batch中
	
	print("Starting sending information to smart contract!")
	# 批处理开始
	batch = 50 # 每次批处理的量
	# print("lent: " + str(lent))
	# print("lent: " + str(lenl))
	# print("Total: " + str(2*lent + lenl))


	# 批量存储byte类型t列表t_batch, int类型N[kw]列表Nkw_batch和byte类型(T,f,P)列表TFP_pair
	for i in range(1,int(lent/batch)+1):
		#setN key：t   value： N
		store_var_contract.functions.set_Nbatch(batch,t_batch[(i-1)*batch:i*batch],Nkw_batch[(i-1)*batch:i*batch]).transact({
			"from": from_account,
			"gas": 6000000,
			"gasPrice": 0,
		})
		# print("success")
		#setI1 key：t   value： T f p
		store_var_contract.functions.set_I1_batch(batch,t_batch[(i-1)*batch:i*batch],TFP_pair[(i-1)*3*batch:i*3*batch]).transact({
			"from": from_account,
			"gas": 6000000,
			"gasPrice": 0,
		})		
	i = int(lent/batch)
	# 剩下的余数部分
	# print(lent%batch)
	store_var_contract.functions.set_Nbatch(lent%batch,t_batch[i*batch:],Nkw_batch[i*batch:]).transact({
			"from": from_account,
			"gas": 6000000,
			"gasPrice": 0,
		})
	store_var_contract.functions.set_I1_batch(lent%batch,t_batch[i*batch:],TFP_pair[i*3*batch:]).transact({
		"from": from_account,
		"gas": 6000000,
		"gasPrice": 0,
	})	

	# 批量存储byte类型l列表l_batch, byte类型(v,c)列表vc_pair
	for i in range(1,int(lenl/batch)+1):
		#setI2 key：l   value： v c
		store_var_contract.functions.set_I2_batch(batch,l_batch[(i-1)*batch:i*batch],vc_pair[(i-1)*2*batch:i*2*batch]).transact({
			"from": from_account,
			"gas": 6000000,
			"gasPrice": 0,
		})	
	i = int(lenl/batch)
	store_var_contract.functions.set_I2_batch(lenl%batch,l_batch[i*batch:],vc_pair[i*2*batch:]).transact({
		"from": from_account,
		"gas": 6000000,
		"gasPrice": 0,
	})
	print("finished!")
					
			
########### 搜索阶段 ##########
# [输入] 1: 搜索关键字w(str)
#        2: user密钥G_u_1(int)
#        3: user密钥G_u_2(int)
#        4: owner密钥k1(bytes)
#        5: owner密钥k2(bytes)
#        6: 更新时间戳TimeString(str)
#        7: 搜索时间集合TimePair(str)
# [输出] 发送信息给只能合约进行存储
##############################
def search(w,G_u_1,G_u_2,k1,k2,TimeString,TimePair):
	#tk[] 多个可能time计算的tk值 
	tk = []
	model = AES.MODE_ECB # AES加密模式
	aes = AES.new(k2, model) # AES加密密文
	for time in TimePair: # 遍历Tm
		for i in range(alpha):
			#查出*的位置然后拼接
			if time[i]=='*':
				time = time[:i]+TimeString[i:]
				break
		# print(time)
		f1=time.zfill(16).encode() # 填充T_m
		while f1[0]!=48:
			f1 = time.zfill(16).encode()
			print(22222222222222222222222222222)
		tk.append(aes.encrypt(f1)) # 计算 tk <--- \hat{F}(k_o,T_m)
		# print(aes.encrypt(f1)) 

	#与update H1保持一致
	w = w.encode('utf-8') # w转byte
	h = hmac.new(w).digest() # 计算H1(w)
	h = int.from_bytes(h, byteorder='big') # w 转大数

	hk = ((mpz(h) % q) * (mpz(G_u_2) % q)) % q # 计算tk <--- h *G_u_2
	hk=int(hk)
	# print(G_u_1,hk)
	hx = store_var_contract.functions.search(alpha,G_u_1,hk,tk).transact({
		"from": from_account,
		"gas": 6000000,
		"gasPrice": 0,
	})
	result = store_var_contract.functions.retrieve0().call()
	print("Result size: ", len(result))
	#解密
	# model = AES.MODE_ECB
	# aes = AES.new(k1, model) 	
	# for ciphertext in result:
	# 	f = aes.decrypt(ciphertext[:16])
	# 	print(f)

	# result = store_var_contract.functions.retrieve2().call()
	# print(result)

	# # result = store_var_contract.functions.retrieve1().call()
	# # print(result)
	# print('--------------判断在智能合约上能不能匹配---------')
	# result = store_var_contract.functions.retrieve2().call()
	# print(result)
	# # print('---------------t ?= t------------------------')
	# # result = store_var_contract.functions.retrieve4().call()
	# # print(result)
	# print('---------------智能合约算T-----------')
	# result = store_var_contract.functions.retrieve5().call()
	# print(result)

abi_build_index = """
[
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"name": "N",
		"outputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "retrieve2",
		"outputs": [
			{
				"name": "",
				"type": "int256[]"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "len",
				"type": "uint256"
			},
			{
				"name": "add",
				"type": "bytes32[]"
			},
			{
				"name": "val",
				"type": "uint256[]"
			}
		],
		"name": "set_Nbatch",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "len",
				"type": "uint256"
			},
			{
				"name": "add",
				"type": "bytes32[]"
			},
			{
				"name": "val",
				"type": "bytes32[]"
			}
		],
		"name": "set_I1_batch",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "add",
				"type": "uint256"
			},
			{
				"name": "val",
				"type": "bytes"
			}
		],
		"name": "set_AL",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "result1",
		"outputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "retrieve0",
		"outputs": [
			{
				"name": "",
				"type": "bytes32[]"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "add",
				"type": "bytes32"
			},
			{
				"name": "val",
				"type": "uint256"
			}
		],
		"name": "set_N",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"name": "AL",
		"outputs": [
			{
				"name": "",
				"type": "bytes"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "alpha",
				"type": "uint256"
			},
			{
				"name": "G_u_1",
				"type": "uint256"
			},
			{
				"name": "Hk",
				"type": "uint256"
			},
			{
				"name": "Tk",
				"type": "bytes32[]"
			}
		],
		"name": "search",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "len",
				"type": "uint256"
			},
			{
				"name": "add",
				"type": "bytes32[]"
			},
			{
				"name": "val",
				"type": "bytes32[]"
			}
		],
		"name": "set_I2_batch",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "pp",
		"outputs": [
			{
				"name": "",
				"type": "bytes"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "g",
				"type": "bytes"
			},
			{
				"name": "x",
				"type": "uint256"
			},
			{
				"name": "p",
				"type": "bytes"
			}
		],
		"name": "expmod",
		"outputs": [
			{
				"name": "",
				"type": "bytes"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"name": "M",
		"outputs": [
			{
				"name": "",
				"type": "int256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"name": "R",
		"outputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	}
]
"""

print("--------------Initialization--------")
# 随机选取一个账户地址
from_account = w3.toChecksumAddress(w3.eth.accounts[0])
print(w3.eth.accounts[0])
abi_build_index = json.loads(abi_build_index)

# 智能合约信息
store_var_contract = w3.eth.contract(
	address=w3.toChecksumAddress('0xEE7df917410b67AbD7b46B31Ba48a05814131656'),
	abi=abi_build_index)

# phex = hex(int(p))
# print(q)
# phex=phex[2:]
# ptian="0x"+"0"*(768-len(phex))+phex
# store_var_contract.functions.setP(ptian.encode()).transact({
# 	"from": from_account,
# 	"gas": 3000000,
# 	"gasPrice": 0,
# })

# 读取数据集
# count = 0
Kw_File_Use ={} # 倒排索引表 
for sub in subs: # 遍历读取每个文件
	fileParser(readFileDir,sub,Kw_File_Use)
	# count = count + 1
	# if count > 1000:
	# 	break
print(len(Kw_File_Use))

# 初始化过程
print("--------------Setup Procedure--------") 
# phex = hex(int(p))
# tx = store_var_contract.functions.setP(phex).transact({
#                 "from": from_account,
#                 "gas": 3000000,
#                 "gasPrice": 0,
# })
# 初始化生成owner和user密钥
G_o,G_u_1,G_u_2,k1,k2= setup()
# print(phex)

# if __name__ == "__main__":
#     alpha = 3  # 二进制字串长度
#     Tr = '6' # 查询时刻
#     res = GetOBRC(Tr,alpha)


# 更新过程
print("--------------Update Procedure--------")
updateTimestamp = "{0:b}".format(6) # 更新时间戳
update_time_start = time.time() # 记录开始时间
update(Kw_File_Use,G_o,"AND",k1,k2,updateTimestamp)
update_time_end = time.time() # 记录结束时间
print('Storage: '+ str(storage))

print("----------------Update time---------------")
update_time = update_time_end - update_time_start
print(str(update_time)+' s')


# update_one_entry(Kw_File_Use,G_o)
# print(Kw_File_Use["a"])
# print(Kw_File_Use['956'])
# print(Kw_File_Use["956"])

# 搜索过程
print("--------------Search Procedure--------")
alpha = 3  # 二进制字串长度 \alpha
keyword = "ee" # 查询关键字
searchTimestamp = '6' # 查询时刻
res = GetOBRC(searchTimestamp,alpha)

search_time_start = time.time() # 记录开始时间
search(keyword,G_u_1,G_u_2,k1,k2,updateTimestamp,res)
search_time_end = time.time() # 记录结束时间
print("----------------Search time---------------")
search_time = search_time_end - search_time_start
print(str(search_time)+' s')











