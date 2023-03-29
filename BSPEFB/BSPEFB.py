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
# readFileDir = "/home/node4/yangxu/ICC20/rangeStreaming/testdata/"
readFileDir = "../rangeStreaming/dataset_2K/" # 文件路径
storage = 0

subs = os.listdir(readFileDir) # 返回输入路径下所有的文件和文件夹列表

# 公共参数
tpN = 75285740785471847697928274317260872220053075039512266400838219410235694454753 # 陷门置换: 公共参数
tpE = 65537 # 陷门置换: 公钥
tpD = 24421312592250881337416378285711107962134904078804043489873387100470794191149 # 陷门置换: 私钥
G = bp.BpGroup() # 双线性映射群
P = G.gen2() # 大数
EV = G.gen2()
w_st_c = {} # 状态表(w ---> st[])
tw = G.gen1()
tw = G.pair(tw,P)
tw_table = {}
r = 0 # 版本信息
# tp_stc = []

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545')) # 连接本地testRPC私链
# w3.middleware_onion.inject(geth_poa_middleware, layer=0)
# print(w3.eth.blockNumber)

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


########### 密钥初始化 ##########
# [输入] 无
# [输出] 1: 私钥sk_du(int) 
#        2: 公钥pk_du(int)
################################
def keygen():
	sk_du = 1 # 私钥
	# sk_du = secrets.randbelow(10)# sk_du随机整数
	pk_du = P * sk_du # 公钥
	# print(pk_du)
	return sk_du,pk_du

########### 更新过程 ##########
# [输入] 1: 公钥pk_du(int)
#        2: 操作符op(str) 
#        3: 倒排索引表Kw_File_Use(dic)
#        4: 状态表w_st_c(dic)
# [输出] 发送信息给只能合约进行存储
##############################
def update(pk_du,op,Kw_File_Use,w_st_c):
	
	global r , storage
	r = r + 1 # 更新版本信息r
	#r = secrets.randbelow(pow(2, 128))
	global EV
	EV = P * r # 计算EV <--- r * P
	
	bytesw_table=[] # byte类型关键字w列表
	strst1_table=[] # byte类型st
	lenw = 0 # 关键字数量计数器

	st1_table=[] # byte类型状态st列表
	stint_table=[] # int类型状态st列表
	lenstint = 0 # st数量计数器
	
	addst_table=[] # byte类型add_st列表
	valst_table=[] # int类型val_st列表
	lenst = 0 # (add_st,val_st)数量计数器
	
	addind_table=[] # byte类型add_ind列表
	valind_table=[] # byte类型val_ind列表
	lenind = 0 # (add_ind,val_ind)数量计数器

	addtw_table=[] # byte类型addtw列表
	valtw_table=[] # byte类型valtw列表
	lentw = 0 # (add_tw,val_tw)数量计数器

	storage = storage + 4

	for w in Kw_File_Use.keys(): # 遍历每个关键字
		storage = storage + 2
		if w_st_c.get(w) == None:
			st_0 = random.randint(1,1000) # 随机生成初始状态
			c = 0 # 计数器初始化为1
		else:
			st_0,c=w_st_c[w] # 从状态表中取出当前状态st_0和计数器值c

		# 伪随机置换补充时间
		k = secrets.randbelow(pow(2, 128))
		st_1 = pow(st_0, tpD, tpN) # 通过陷门置换计算下一个状态st_1
		# global tp_stc
		# tp_stc.append(st_1)
		# print("st_1",st_1)
		w_st_c[w] = st_1 , c+1 # 更新状态表

		# 传入st2int st_1 与 int值对应 方便solidity计算
		# ！！！！！！！切记不能先转string再转int 直接int转hex！！！！
		st_int = int(st_1) # 获得int类型st
		st_1 = str(st_1)[:32].encode() # 获得byte类型st
		
		# 批处理塞入数据
		st1_table.append(st_1) # 将int类型st放入st1_table中
		stint_table.append(st_int) # 将byte类型st放入stint_table中
		lenstint = lenstint + 1 # 更新st数量计数器
		# store_var_contract.functions.set_st(st_1,st_int).transact({
		# 	"from": from_account,
		# 	"gas": 3000000,
		# 	"gasPrice": 0,
		# })

		add_st = Web3.keccak(st_1) # 计算Hash 1得到add_st: add_(st^w) <--- h1(st^w)
		temp = Web3.keccak(st_1) # 计算Hash 2得到temp: temp <--- h2(st^w)
		val_st = len(Kw_File_Use[w]) # 获取该关键字对应的ind个数val_st
		addst_table.append(add_st) # 将byte类型add_st放入addst_table中
		valst_table.append(val_st) # 将int类型val_st放入valst_table中
		lenst = lenst+1 # 更新(add_st,val_st)数量计数器
		# tx_hash=store_var_contract.functions.set_edb1(add_st,val_st).transact({
		# 	"from": from_account,
		# 	"gas": 3000000,
		# 	"gasPrice": 0,
		# })
		j = 1
		for ind in Kw_File_Use[w]: # 遍历w对应的每个ind
			EI = Web3.keccak((r * pk_du).export() + w.encode()) # 计算 H1(r*PK_{du} || w)
			# print("EI    ",EI)
			EI = bytes(a ^ b for a, b in zip(EI,(op+ind).zfill(32).encode())) # 计算 EI <--- H1(r*PK_{du} || w) \oplus (op ||| ind)
			
			# if(w == "e"):
			# 	print("EI    ",EI)
			add_ind = Web3.keccak(hexstr = hex(st_int+j)) # 计算 add_ind <--- h3(st^w || j)
			temp = Web3.keccak(hexstr = hex(st_int+j)) # 计算 h4(st^w || j)

			#val_ind EI^add
			val_ind = bytes(a ^ b for a, b in zip(temp,EI)) # 计算 val_ind <--- (j||EI_ind) \oplus h4(st^w || j)
			addind_table.append(add_ind) # 将byte类型add_ind放入addind_table中
			valind_table.append(val_ind) # 将byte类型val_ind放入valind_table中
			lenind = lenind + 1 # 更新(add_ind,val_ind)数量计数器
			# tx_hash=store_var_contract.functions.set_edb(add_ind,val_ind).transact({
			# 	"from": from_account,
			# 	"gas": 3000000,
			# 	"gasPrice": 0,
			# })
			j = j + 1 
		temp = G.hashG1(w.encode()) #  eH0 大数的hash运算 byte->G2
		global tw 
		global tw_table
		tw = G.pair(temp,r * pk_du) # 计算陷门 t_w <--- e(H0(w),r*PK_{du})
		tw_table[w] = tw
		add_tw = Web3.keccak(tw.export()) # 计算 add_tw <--- H2(t_w)  注: H2 大数hash G->int 智能合约需要能计算H2
		# print("add_tw",add_tw)
		temp = Web3.keccak(tw.export()) # 计算 H3(t_w)
		val_tw = bytes(a ^ b for a, b in zip(temp,st_1)) # 计算 val_tw <--- H3(t_w) \oplus st^w  H2与H3一致 看作一个hash 是否需要多做一次hash 来保证时间？
		# print(len(temp))
		# print("val_tw",val_tw)
		# print("st",st_1)
		#智能合约上传函数 
		bytesw_table.append(w.zfill(32).encode()) # 将byte类型w放入bytesw_table中
		strst1_table.append(str(st_1)[:32].encode()) # 将byte类型st_1放入strst1_table中
		lenw = lenw + 1 # 更新关键字数量计数器
		# tx_hash=store_var_contract.functions.set_st1(w.zfill(32).encode(),str(st_1)[:32].encode()).transact({
		# 	"from": from_account,
		# 	"gas": 3000000,
		# 	"gasPrice": 0,
		# })

		addtw_table.append(add_tw) # 将byte类型add_tw放入addtw_table中
		valtw_table.append(val_tw) # 将byte类型val_tw放入valtw_table中
		lentw = lentw + 1 # 更新(add_tw,val_tw)数量计数器
		# tx_hash=store_var_contract.functions.set_edb(add_tw,val_tw).transact({
		# 	"from": from_account,
		# 	"gas": 3000000,
		# 	"gasPrice": 0,
		# })
		
	# 批处理开始
	batch = 50 # 每次批处理的量
	print("Total: " + str(lenstint + lenst + lenind + lentw + lenw))

	# 批量存储byte类型状态st列表st1_table和int类型状态st列表stint_table
	for i in range(1,int(lenstint/batch)+1):
		store_var_contract.functions.batch_stint(batch,st1_table[(i-1)*batch : i*batch],stint_table[(i-1)*batch : i*batch]).transact({
			"from": from_account,
			"gas": 6000000,
			"gasPrice": 0,
		})
	i = int(lenstint/batch)
	store_var_contract.functions.batch_stint(lenstint%batch,st1_table[i*batch:],stint_table[i*batch:]).transact({
		"from": from_account,
		"gas": 6000000,
		"gasPrice": 0,
	})

	# 批量存储byte类型addst_table列表和int类型valst_table列表
	for i in range(1,int(lenst/batch)+1):
		store_var_contract.functions.batch_st(batch,addst_table[(i-1)*batch:i*batch],valst_table[(i-1)*batch:i*batch]).transact({
			"from": from_account,
			"gas": 6000000,
			"gasPrice": 0,
		})
	i = int(lenst/batch)
	store_var_contract.functions.batch_st(lenst%batch,addst_table[i*batch:],valst_table[i*batch:]).transact({
		"from": from_account,
		"gas": 6000000,
		"gasPrice": 0,
	})

	# 批量存储byte类型addind_table列表和byte类型valind_table列表
	for i in range(1,int(lenind/batch)+1):
		store_var_contract.functions.batch_ind(batch,addind_table[(i-1)*batch:i*batch],valind_table[(i-1)*batch:i*batch]).transact({
			"from": from_account,
			"gas": 6000000,
			"gasPrice": 0,
		})
	i = int(lenind/batch)
	store_var_contract.functions.batch_ind(lenind%batch,addind_table[i*batch:],valind_table[i*batch:]).transact({
		"from": from_account,
		"gas": 6000000,
		"gasPrice": 0,
	})

	# 批量存储byte类型addtw_table列表和byte类型valtw_table列表
	for i in range(1,int(lentw/batch)+1):
		store_var_contract.functions.batch_tw(batch,addtw_table[(i-1)*batch:i*batch],valtw_table[(i-1)*batch:i*batch]).transact({
			"from": from_account,
			"gas": 6000000,
			"gasPrice": 0,
		})
	i = int(lentw/batch)
	store_var_contract.functions.batch_tw(lentw%batch,addtw_table[i*batch:],valtw_table[i*batch:]).transact({
		"from": from_account,
		"gas": 6000000,
		"gasPrice": 0,
	})

	# 批量存储byte类型bytesw_table列表和byte类型strst1_table列表
	for i in range(1,int(lenw/batch)+1):
		store_var_contract.functions.batch_st1(batch,bytesw_table[(i-1)*batch:i*batch],strst1_table[(i-1)*batch:i*batch]).transact({
			"from": from_account,
			"gas": 6000000,
			"gasPrice": 0,
		})
	i = int(lenw/batch)
	store_var_contract.functions.batch_st1(lenw%batch,bytesw_table[i*batch:],strst1_table[i*batch:]).transact({
		"from": from_account,
		"gas": 6000000,
		"gasPrice": 0,
	})




# def update(pk_du,op,Kw_File_Use,w_st_c):
# 	for w in Kw_File_Use.keys():
# 		for ind in Kw_File_Use[w]:
# 			global r 
# 			r = r + 1
# 			#r = secrets.randbelow(pow(2, 128))
# 			global EV
# 			EV = P * r

# 			if w_st_c.get(w) == None:
# 				st_0 = 3
# 				#st_0 = secrets.randbelow(pow(2, 128))# lamda随机生成字符串
# 				c = 0
# 			else:
# 				st_0,c=w_st_c[w]

# 			#伪随机置换
# 			k = secrets.randbelow(pow(2, 128))
# 			st_1 = pow(st_0, tpD, tpN)
# 			# global tp_stc
# 			# tp_stc.append(st_1)
			

# 			# print("st_1",st_1)
# 			w_st_c[w] = st_1,c+1
# 			st_1 = str(st_1)[:32].encode()
# 			add_st = Web3.keccak(st_1)#h1
# 			temp = Web3.keccak(st_1)#h2
# 			val_st = bytes(a ^ b for a, b in zip(("1"+str(k)).zfill(32).encode(),temp))#需要填充至32字节
# 			# print("val_st",val_st)

# 			EI = Web3.keccak((r * pk_du).export() + w.encode())#H1 大数的hash运算  G->int
# 			# print("EI    ",EI)
# 			EI = bytes(a ^ b for a, b in zip(EI,(op+ind).zfill(32).encode()))
# 			# print("EI    ",EI)
# 			add_ind = Web3.keccak(st_1)#h3
# 			temp = Web3.keccak(st_1)#h4
# 			val_ind = bytes(a ^ b for a, b in zip(temp,EI))

# 			temp = G.hashG1(w.encode()) #H0 大数的hash运算 byte->G2
# 			global tw
# 			tw = G.pair(temp,r * pk_du) 
			
# 			tw_table[w] = tw
			
# 			add_tw = Web3.keccak(tw.export()) #H2 大数hash G->int 智能合约需要能计算H2
# 			# print("add_tw",add_tw)
# 			temp = Web3.keccak(tw.export())
# 			val_tw = bytes(a ^ b for a, b in zip(temp,st_1)) # H2与H3一致 看作一个hash 是否需要多做一次hash 来保证时间？
# 			# print(len(temp))
# 			# print("val_tw",val_tw)
# 			# print("st",st_1)
# 			#智能合约上传函数 
# 			tx_hash=store_var_contract.functions.set_edb(add_st,val_st).transact({
# 				"from": from_account,
# 				"gas": 3000000,
# 				"gasPrice": 0,
# 			})
# 			tx_hash=store_var_contract.functions.set_edb(add_ind,val_ind).transact({
# 				"from": from_account,
# 				"gas": 3000000,
# 				"gasPrice": 0,
# 			})
# 			tx_hash=store_var_contract.functions.set_edb(add_tw,val_tw).transact({
# 				"from": from_account,
# 				"gas": 3000000,
# 				"gasPrice": 0,
# 			})
# 			tx_hash=store_var_contract.functions.set_st(w.zfill(32).encode(),str(st_1)[:32].encode()).transact({
# 				"from": from_account,
# 				"gas": 3000000,
# 				"gasPrice": 0,
# 			})



########### 生成陷门过程 ##########
# [输入] 1: 私钥sk_du(int)
#        2: 关键字w(str) 
# [输出] 搜索陷门Tw(大数)
#################################
def trapdoor(sk_du,w):
	temp = G.hashG1(w.encode())
	Tw = G.pair(temp*sk_du,EV) # 计算陷门 T_w <--- e(H0(w)*sk_{du}, EV)
	# print("tw与Tw是否相等",G.pair(temp*sk_du,EV)==tw_table[w])
	return Tw

########### 解密过程 ##########
# [输入] 1: 私钥sk_du(int)
#        2: 关键字w(str)
#        3：搜索结果 
# [输出] 无
#################################
def decrypt_mei(sk_du,w,mei):
	i = r
	for Ei in mei:
		EV_temp = i * P # 计算EV <--- r * P
		temp = sk_du * EV_temp # 计算temp <--- sk_{du} * EV
		temp = Web3.keccak(temp.export()+w.encode()) # 计算 H1(temp||w)
		opind = bytes(a ^ b for a, b in zip(temp,Ei)) # 计算 op||ind <--- H1(temp||w) \oplus EI
		# print(opind,i)
		

#abi
abi_build_index = """
[
	{
		"constant": false,
		"inputs": [
			{
				"name": "batch",
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
		"name": "batch_ind",
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
				"type": "bytes32"
			},
			{
				"name": "",
				"type": "uint256"
			}
		],
		"name": "st",
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
		"constant": false,
		"inputs": [
			{
				"name": "batch",
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
		"name": "batch_stint",
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
				"type": "bytes32"
			}
		],
		"name": "edb1",
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
		"constant": false,
		"inputs": [
			{
				"name": "batch",
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
		"name": "batch_st1",
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
				"type": "bytes32"
			}
		],
		"name": "c",
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
		"inputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"name": "st2int",
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
		"inputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"name": "edb",
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
				"name": "batch",
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
		"name": "batch_st",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "batch",
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
		"name": "batch_tw",
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
		"name": "mei",
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
		"constant": false,
		"inputs": [
			{
				"name": "w",
				"type": "bytes32"
			},
			{
				"name": "tw",
				"type": "bytes32"
			}
		],
		"name": "search",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
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
	address=w3.toChecksumAddress('0x773e2337FD4598C3005470aB9DC6F9382b40a95d'),
	abi=abi_build_index)

# 生成私钥和公钥
sk_du, pk_du = keygen() 

# 读取数据集
Kw_File_Use ={}
for sub in subs:
	# print(sub)
	fileParser(readFileDir,sub,Kw_File_Use)
# print(Kw_File_Use)

# 更新过程
print("--------------Update Procedure--------")
update_time_start = time.time() # 记录开始时间
update(pk_du,"AND",Kw_File_Use,w_st_c)
update_time_end = time.time() # 记录结束时间
print('Storage: '+ str(storage))

print("----------------Update time---------------")
update_time = update_time_end - update_time_start
print(str(update_time)+' s')

# # 搜索过程
# print("--------------Search Procedure--------")
# search_time_start = time.time() # 记录开始时间
# keyword = "aa" # 查询关键字
# print("Search keyword: ", keyword)
# # 生成陷门
# Tw = trapdoor(sk_du,keyword)

# # 智能合约搜索
# tx_hash=store_var_contract.functions.search(keyword.zfill(32).encode(),Web3.keccak(Tw.export())).transact({
# 	"from": from_account,
# 	"gas": 6000000,
# 	"gasPrice": 0,
# })

# # 返回搜索结果
# mei = store_var_contract.functions.retrieve0().call() 
# # print(mei)
# print("Result size: ", len(mei))

# # 解密出明文
# decrypt_mei(sk_du,keyword,mei)
# search_time_end = time.time() # 记录结束时间
# print("----------------Search time---------------")
# search_time = search_time_end - search_time_start
# print(str(search_time)+' s')

