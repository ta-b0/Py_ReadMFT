import sys
import re
import math
import binascii
import os

#f.seek(offset,from_what):
	#from_what=0 -> 先頭から,default
	#from_what=1 -> 現在の場所から
	#from_what=2 -> 終端から


####AttributeHeader
def read_AttributeHeader(f):
	Attribute_read = ""
	#print('Func AttributeHeader')
	AttributeType_OffsetToTheName = f.read(int('b',16)) # 先頭からOffsetToTheNameまで読み込む
	AttributeType_OffsetToTheName = ByteToStr(AttributeType_OffsetToTheName)
	Attribute_read = AttributeType_OffsetToTheName
	#print(">>>>>",end="")
	#print(Attribute_read)
	#print(AttributeType_OffsetToTheName)
	ResidentFlag = AttributeType_OffsetToTheName[16:18]
	#print('str_ResidentFlag(hex):',end="")
	#print(ResidentFlag)
	Name_length = AttributeType_OffsetToTheName[18:20]
	#print('str_Name_length(hex):',end="")
	#print(Name_length)
	OffsetToTheName = AttributeType_OffsetToTheName[20:22]
	#print('str_OffsetToTheName(hex):',end="")
	#print(OffsetToTheName)

	if ResidentFlag == '00':
		temp = f.read(int('d',16))
		temp = ByteToStr(temp) #AttributeHeader+0x18まで読み込み
		#print(temp)
		Attribute_read = Attribute_read + temp
		#print(Attribute_read)
		if OffsetToTheName == '00':
			AttributeHeader = Resident_NoName(Attribute_read)
		else:
			TheAttributesName = ByteToStr(f.read(2*int(Name_length,16)))
			Attribute_read = Attribute_read + TheAttributesName
			AttributeHeader = Resident_Named(Attribute_read)
	else:
		temp = f.read(int('35',16))
		temp = ByteToStr(temp) #AttributeHeader+0x40まで読み込み
		#print(temp)
		Attribute_read = Attribute_read + temp
		#print(Attribute_read)
		if OffsetToTheName == '00':
			AttributeHeader = NonResident_NoName(Attribute_read)
		else:
			TheAttributesName = ByteToStr(f.read(2*int(Name_length,16)))
			Attribute_read = Attribute_read + TheAttributesName
			AttributeHeader = Resident_Named(Attribute_read)
			AttributeHeader = NonResident_Named(Attribute_read)
	return AttributeHeader

def Resident_NoName(str_a):
	#print('Resident_NoName')
	AttributeHeader = {
		"AttributeType" : str_a[0:8],
		"Length" : str_a[8:16],
		"ResidentFlag" : str_a[16:18],
		"NameLength" : str_a[18:20],
		"OffsetToTheName" : str_a[20:24],
		"Flags" : str_a[24:28],
		"AtributeId" : str_a[28:32],
		"LengthOfTheAttribute" : str_a[32:40],
		"OffsetToTheAttribute" : str_a[40:44],
		"IndexedFlag" : str_a[44:46],
		"Padding" : str_a[46:48],
	}
	return AttributeHeader

def Resident_Named(str_a):
	#print('Resident_Named')
	AttributeHeader = {
		"AttributeType" : str_a[0:8],
		"Length" : str_a[8:16],
		"ResidentFlag" : str_a[16:18],
		"NameLength" : str_a[18:20],
		"OffsetToTheName" : str_a[20:24],
		"Flags" : str_a[24:28],
		"AtributeId" : str_a[28:32],
		"LengthOfTheAttribute" : str_a[32:40],
		"OffsetToTheAttribute" : str_a[40:44],
		"IndexedFlag" : str_a[44:46],
		"Padding" : str_a[46:48],
		"TheAttributesName" : str_a[48:]
	}
	return AttributeHeader

def NonResident_NoName(str_a):
	#print('NonResident_NoName')
	AttributeHeader = {
		"AttributeType" : str_a[0:8],
		"Length" : str_a[8:16],
		"ResidentFlag" : str_a[16:18],
		"NameLength" : str_a[18:20],
		"OffsetToTheName" : str_a[20:24],
		"Flags" : str_a[24:28],
		"AttributeId" : str_a[28:32],
		"StartingVCN" : str_a[32:48],
		"LastVCN" : str_a[48:64],
		"OffsetToTheDataRuns" : str_a[64:68],
		"CompressionUnitSize" : str_a[68:72],
		"Padding" : str_a[72:80],
		"AllocatedSizeOfTheAttribute" : str_a[80:96],
		"RealSizeOfTheAttribute" : str_a[96:112],
		"InitializedDatSizeOfTheStream" : str_a[112:128],
		"LengthOfTheAttribute" : str('00')
	}
	return AttributeHeader

def NonResident_Named(str_a):
	#print('NonResident_Named')
	AttributeHeader = {
		"AttributeType" : str_a[0:8],
		"Length" : str_a[8:16],
		"ResidentFlag" : str_a[16:18],
		"NameLength" : str_a[18:20],
		"OffsetToTheName" : str_a[20:24],
		"Flags" : str_a[24:28],
		"AttributeId" : str_a[28:32],
		"StartingVCN" : str_a[32:48],
		"LastVCN" : str_a[48:64],
		"OffsetToTheDataRuns" : str_a[64:68],
		"CompressionUnitSize" : str_a[68:72],
		"Padding" : str_a[72:80],
		"AllocatedSizeOfTheAttribute" : str_a[80:96],
		"RealSizeOfTheAttribute" : str_a[96:112],
		"InitializedDatSizeOfTheStream" : str_a[112:128],
		"TheAttributesName" : str_a[128:],
		"LengthOfTheAttribute" : str('00')
	}
	return AttributeHeader
####End_AttributeHeader
####Attributes
def isAttribute(f,AttributeType,LengthOfTheAttribute): #AttributeType=str(e.g: 10000000)
	LengthOfTheAttribute = StrToList(LengthOfTheAttribute)
	LengthOfTheAttribute = LittleEndian(LengthOfTheAttribute)
	LengthOfTheAttribute = ListToStr(LengthOfTheAttribute)
	LengthOfTheAttribute = int(LengthOfTheAttribute,16)
	#print(">>>>LengthOfTheAttribute:",end="")
	#print(LengthOfTheAttribute)
	if AttributeType == '10000000':
		Attribute10(f,LengthOfTheAttribute)
	elif AttributeType == '30000000':
		Attribute30(f,LengthOfTheAttribute)
	elif AttributeType == '80000000':
		Attribute80(f,LengthOfTheAttribute)
	return 0

def Attribute10(f,LengthOfTheAttribute):
	#print('>>>>>>>>>>Attribute10')
	f.read(LengthOfTheAttribute)
	return 0

def Attribute30(f,LengthOfTheAttribute):
	#print('>>>>>>>>>>Attribute30')
	f.read(LengthOfTheAttribute)
	FullByteLine = LengthOfTheAttribute // 16
	#print(FullByteLine)
	PaddingLength =  16 - (LengthOfTheAttribute - FullByteLine*16)
	#print(PaddingLength)
	f.read(PaddingLength)
	return 0

def Attribute80(f,LengthOfTheAttribute):
	#print('>>>>>>>>>Attribute80')
	field = ""
	LengthOfTheRun = []
	OffsetToTheStartingLCN = []
	while field != '00':
		LengthOfTheRun_value = ""
		OffsetToTheStartingLCN_value = ""

		field = ByteToStr(f.read(1))
		field_F = int(field[0],16)
		field_L = int(field[1],16)
		if field == '00':
			break
		LengthOfTheRun_value = ByteToStr(f.read(field_L))
		LengthOfTheRun_value = StrToList(LengthOfTheRun_value)
		LengthOfTheRun_value = LittleEndian(LengthOfTheRun_value)
		LengthOfTheRun_value = ListToStr(LengthOfTheRun_value)

		OffsetToTheStartingLCN_value = ByteToStr(f.read(field_F))
		OffsetToTheStartingLCN_value = StrToList(OffsetToTheStartingLCN_value)
		OffsetToTheStartingLCN_value = LittleEndian(OffsetToTheStartingLCN_value)
		OffsetToTheStartingLCN_value = ListToStr(OffsetToTheStartingLCN_value)

		LengthOfTheRun.append(LengthOfTheRun_value)
		OffsetToTheStartingLCN.append(OffsetToTheStartingLCN_value)


	OffsetToTheStartingLCN  = [f'{n:x}' for n in [isMinus(int(n, 16)) for n in OffsetToTheStartingLCN]]

	for i in range(len(OffsetToTheStartingLCN)):
		OffsetToTheStartingLCN[i] = int(OffsetToTheStartingLCN[i],16)
		LengthOfTheRun[i] = int(LengthOfTheRun[i],16)

	f.seek(0)
	#print('hogeeeeeeeee')
	#print(OffsetToTheStartingLCN)
	#print(LengthOfTheRun)
	for i in range(len(LengthOfTheRun)):
		if i == 0:
			offset = OffsetToTheStartingLCN[0]
		else:
			offset = offset + OffsetToTheStartingLCN[i]
		f.seek(offset*4096,0)
		#with open(r'G:\MFT','ab') as f_mft:
		with open('MFT','ab') as f_mft:
			for k in range(4096):
				f_mft.write(f.read(LengthOfTheRun[i]))
	return 0

####End_Attribute	


def read_MFT(f,Int_BytesPerCluster_Top):
	#FileRecoadの読み込み
	f.seek(Int_BytesPerCluster_Top,0)
	#a = f.read(512)
	#print_hex(a)
	#10 00 00 00
	b = f.read(int('16',16))
	#print_hex(b)
	byte_raw_FireRecoad_OffsetToTheFirstAttribute = b[-2:]
	#print('hoge')
	#print_hex(byte_raw_FireRecoad_OffsetToTheFirstAttribute)
	byte_new_FireRecoad_OffsetToTheFirstAttribute = LittleEndian(byte_raw_FireRecoad_OffsetToTheFirstAttribute)
	#print('fuga')
	byte_new_FireRecoad_OffsetToTheFirstAttribute = ByteToStr(byte_new_FireRecoad_OffsetToTheFirstAttribute)
	byte_new_FireRecoad_OffsetToTheFirstAttribute = int(byte_new_FireRecoad_OffsetToTheFirstAttribute,16)
	#print(hex(byte_new_FireRecoad_OffsetToTheFirstAttribute))
	#print(byte_new_FireRecoad_OffsetToTheFirstAttribute)
	skip_to_AttributeHeader = byte_new_FireRecoad_OffsetToTheFirstAttribute - int('16',16)
	#print(hex(skip_to_AttributeHeader))
	temp = f.read(skip_to_AttributeHeader)
	#10 00 00 00
	AttributeHeader = read_AttributeHeader(f)
	#print(AttributeHeader)
	isAttribute(f,AttributeHeader["AttributeType"],AttributeHeader["LengthOfTheAttribute"])
	#30 00 00 00
	#print('30 00 00 00')
	AttributeHeader = read_AttributeHeader(f)
	#print(AttributeHeader)
	isAttribute(f,AttributeHeader["AttributeType"],AttributeHeader["LengthOfTheAttribute"])
	#80 00 00 00
	AttributeHeader = read_AttributeHeader(f)
	#print(AttributeHeader)
	isAttribute(f,AttributeHeader["AttributeType"],AttributeHeader["LengthOfTheAttribute"])	


def LogicalClusterOfMFT(f,BytesPerCluster):
	f.seek(48,0)
	bytes_a = f.read(8)
	#print(bytes_a)
	#print("Debug:LogicalClusterOfMFT")
	#print_hex(bytes_a)
	list_a = get_hex(bytes_a)
	LogicalClusterOfMFT_Cruster =  ListToStr(LittleEndian(list_a))
	LogicalClusterOfMFT_Cruster = hex_StrToInt(LogicalClusterOfMFT_Cruster)
	Int_BytesPerCluster_Top = LogicalClusterOfMFT_Cruster * int(BytesPerCluster)
	return Int_BytesPerCluster_Top


def load_SectorPerCluster(f):
	a = f.read(1) # 13(BytesPerSector)+1=14
	SectorPerCluster_code = fetch_hex(a,1,1)
	SectorPerCluster = int(SectorPerCluster_code)
	return SectorPerCluster

def load_BytesPerSector(f):
	a = f.read(13)
	BytesPerSector_code = fetch_hex(a,12,13)
	if BytesPerSector_code == '0002' :
		BytesPerSector = 512
	elif BytesPerSector_code == '0004' :
		BytesPerSector = 1024
	elif BytesPerSector_code == '0008' :
		BytesPerSector =2048
	elif BytesPerSector_code == '0010' :
		BytesPerSector = 4096
	return BytesPerSector

def read(f):
	#Boot Sector
	BytesPerSector = load_BytesPerSector(f)
	print("BytesPerSector:",end="")
	print(BytesPerSector) # debug
	SectorPerCluster = load_SectorPerCluster(f)
	print("SectorPerCluster:",end="")
	print(SectorPerCluster) # debug
	BytesPerCluster = BytesPerSector * SectorPerCluster
	print("BytesPerCluster:",end="")
	print(BytesPerCluster) # debug
	Int_BytesPerCluster_Top = LogicalClusterOfMFT(f,BytesPerCluster)
	print("Start MFT's offset:",end="");print(hex(Int_BytesPerCluster_Top))
	f.seek(0,0)
	readdata = f.read(BytesPerSector)
	with open('BootSector','wb') as BootSector:
		BootSector.write(readdata)
	read_MFT(f,Int_BytesPerCluster_Top)



def diskOpenClose(DiskDir):
	with open(DiskDir,"rb") as f:
		#demo
		#a = f.read(256)
		#print_hex(a)
		read(f)


###############################################################
def isMinus(str_hex): #先頭のバイトが１のときに２の補数でマイナス値へ変換
    str_hex &= 0xffffffff
    return (str_hex ^ 0x80000000) - 0x80000000

def dictToList(str_a):
	list_a = re.split('(..)',str_a)[1::2]
	return list_a

def fetch_hex(hex,start,end):
	#start,endは0個目の要素を１番目とする(f.readと同様)
	list_16 = get_hex(hex)
	return_hex = ''
	partbinary = list_16[start-1:end]
	for i in partbinary:
		return_hex += i
	return return_hex

def get_hex(bytes_a):
	#print("debug",end="")
	#print(bytes_a)
	hex_b = bytes_a.hex()
	hex_b = hex_b.upper()
	list_16 = re.split('(..)',hex_b)[1::2]
	return list_16


def print_hex(bytes_a):
	list_16 = get_hex(bytes_a)
	start = 0
	end = 8
	c = math.ceil(len(list_16)/16)
	for i in range(c):
		k = i * 16
		print("{0:4x}".format(k),end=" ")
		print(list_16[start:end],end=" ")
		start = start + 8
		end = end + 8
		print(list_16[start:end],end=" ")
		#ASCII
		now = ListToStr(list_16[start-8:end])
		now = binascii.unhexlify(now)
		print(now)

		start = start + 8
		end = end + 8

def LittleEndian(list_a):
	list_LittleEndian_a = list_a[::-1]
	return list_LittleEndian_a

def StrToList(str_a):
	list_a = re.split('(..)',str_a)[1::2]
	return list_a

def ListToStr(list_a):
	str_return = "".join(list_a)
	return str_return

def ByteToStr(bytes_a):
	return_str_a = bytes_a.hex()
	return return_str_a

def hex_StrToInt(Str_a):
	int_return = int(Str_a,16)
	return int_return
###############################################################
args = sys.argv
def main():
	global args
	if args[1] == "1":
		DiskDir = r"\\.\F:"
	elif args[1] == "0":
		DiskDir = r"\\.\S:"
	elif args[1] == "2":
		DiskDir = r"\\.\G:"
	diskOpenClose(DiskDir)


if __name__ == "__main__":
	main()