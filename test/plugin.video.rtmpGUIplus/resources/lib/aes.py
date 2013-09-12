#/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  */
#/*  AES implementation in Python, based on the PHP implementation by                              */
#/*    (c) Chris Veness 2005-2011 www.movable-type.co.uk/scripts                                   */
#/*    (c) HansMayer    2012                                                                       */
#/*    Right of free use is granted for all commercial or non-commercial use providing this        */
#/*    copyright notice is retainded. No warranty of any form is offered.                          */
#/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  */
from math import floor,ceil
from random import randint
from base64 import b64encode, b64decode
import time
class AES:
    sBox = [
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16]
    
    rCon = [
    [0x00, 0x00, 0x00, 0x00],
    [0x01, 0x00, 0x00, 0x00],
    [0x02, 0x00, 0x00, 0x00],
    [0x04, 0x00, 0x00, 0x00],
    [0x08, 0x00, 0x00, 0x00],
    [0x10, 0x00, 0x00, 0x00],
    [0x20, 0x00, 0x00, 0x00],
    [0x40, 0x00, 0x00, 0x00],
    [0x80, 0x00, 0x00, 0x00],
    [0x1b, 0x00, 0x00, 0x00],
    [0x36, 0x00, 0x00, 0x00]]
    
    def cipher(self, inp, w):
        Nb = 4
        Nr = len(w)/Nb - 1
        state= [[0 for x in range(4)] for y in range(Nb)]
        for i in range(4*Nb):
            state[i%4][int(floor(float(i)/4))] = inp[i]
                
        state = self.addRoundKey(state, w, 0, Nb)
        for rnd in range(1,Nr):
            state = self.subBytes(state, Nb)
            state = self.shiftRows(state, Nb)
            state = self.mixColumns(state, Nb)
            state = self.addRoundKey(state, w, rnd, Nb)
    
        state = self.subBytes(state, Nb)
        state = self.shiftRows(state, Nb)
        state = self.addRoundKey(state, w, Nr, Nb)
    
        output = [0]*4*Nb
        for i in range(4*Nb):
            output[i] = state[i%4][int(floor(float(i)/4))]
        return output

    def addRoundKey(self,state, w, rnd, Nb):
        for r in range(4):
            for c in range(Nb):
                state[r][c] ^= w[rnd*4+c][r]
        return state
  
    def subBytes(self, s, Nb):
        for r in range(4):
            for c in range(Nb):
                s[r][c] = self.sBox[s[r][c]]
        return s
  
    def shiftRows(self, s, Nb):
        t = [0,0,0,0]
        for r in range(1,4):
            for c in range(4): 
                t[c] = s[r][(c+r)%Nb]
            for c in range(4): 
                s[r][c] = t[c]
        return s

    def mixColumns(self, s, Nb):
        for c in range(4):
            a = [0,0,0,0]
            b = [0,0,0,0]
            for i in range(4):
                a[i] = s[i][c]
                b[i] = s[i][c]&0x80
                if b[i]:
                    b[i] = s[i][c]<<1 ^ 0x011b
                else:
                    b[i] = s[i][c]<<1
                    
            s[0][c] = b[0] ^ a[1] ^ b[1] ^ a[2] ^ a[3]
            s[1][c] = a[0] ^ b[1] ^ a[2] ^ b[2] ^ a[3]
            s[2][c] = a[0] ^ a[1] ^ b[2] ^ a[3] ^ b[3]
            s[3][c] = a[0] ^ b[0] ^ a[1] ^ a[2] ^ b[3]
        return s

    def keyExpansion(self,key):
        Nb = 4
        Nk = len(key) / 4
        Nr = Nk + 6
        w = []
        temp = [0,0,0,0]

        for i in range(Nk):
            w.append([key[4*i], key[4*i+1], key[4*i+2], key[4*i+3]])

        for i in range(Nk, Nb*(Nr+1)):
            w.append([0,0,0,0])
            for t in range(4): temp[t] = w[i-1][t]
            if i % Nk == 0:
                temp = self.subWord(self.rotWord(temp))
                for t in range(4):
                    temp[t] ^= self.rCon[i/Nk][t]
            elif Nk > 6 and i%Nk == 4:
                temp = self.subWord(temp)
            for t in range(4): 
                w[i][t] = w[i-Nk][t] ^ temp[t]
        return w
  
    def subWord(self, w):
        for i in range(4):
            w[i] = self.sBox[w[i]]
        return w
  
    def rotWord(self, w):
        tmp=w[0]
        for i in range(3):
            w[i]=w[i+1]
        w[3] = tmp
        return w
 
#/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  */
#/*  AES counter (CTR) mode implementation in Python, based on the PHP implementation by           */
#/*    (c) Chris Veness 2005-2011 www.movable-type.co.uk/scripts                                   */
#/*    (c) HansMayer    2012                                                                       */
#/*    Right of free use is granted for all commercial or non-commercial use providing this        */
#/*    copyright notice is retainded. No warranty of any form is offered.                          */
#/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  */
  
class AESCtr(AES):
    def urs(self, a, b):
        a &= 0xffffffff
        b &= 0x1f
        if a&0x80000000 and b>0:
            a = (a>>1) & 0x7fffffff
            a = a >> (b-1)
        else:
            a = (a>>b)
        return a
        
    def encrypt(self, plaintext, password, nBits):
        blockSize = 16
        if not nBits in [128,192,256]:
            return
        
        nBytes = nBits/8
        pwBytes = []
        
        for i in range(nBytes):
            if i > len(password)-1:
                pwBytes.append(0)
            else:
                pwBytes.append(ord(password[i])&0xff)
            
        key = self.cipher(pwBytes, self.keyExpansion(pwBytes))
        key = key + key[0:nBytes-16]
        
        counterBlock = [0]*16
        nonce = int(floor(time.time()*1000))
        nonceMs = nonce%1000
        nonceSec = int(floor(float(nonce)/1000))
        nonceRnd = randint(0,0xffff)
        
        for i in range(2): 
            counterBlock[i] = self.urs(nonceMs, i*8) & 0xff
        for i in range(2): 
            counterBlock[i+2] = self.urs(nonceRnd, i*8) & 0xff
        for i in range(4): 
            counterBlock[i+4] = self.urs(nonceSec, i*8) & 0xff
        
        ctrTxt = ''
        for i in range(8): ctrTxt += chr(counterBlock[i])

        keySchedule = self.keyExpansion(key)
        
        blockCount = int(ceil(float(len(plaintext))/blockSize))
        ciphertxt = [0]*blockCount
        
        for b in range(blockCount):
            for c in range(4): 
                counterBlock[15-c] = self.urs(b, c*8) & 0xff
            for c in range(4): 
                counterBlock[15-c-4] = self.urs(b/0x100000000, c*8)

            cipherCntr = self.cipher(counterBlock, keySchedule)
            if b < blockCount-1:
                blockLength = blockSize
            else:
                blockLength = (len(plaintext)-1)%blockSize+1
                
            cipherByte = [0]*blockLength
            for i in range(blockLength):
                cipherByte[i] = chr(cipherCntr[i] ^ ord(plaintext[b*blockSize+i]))
        
            ciphertxt[b] = ''.join(cipherByte)
        
        return b64encode(ctrTxt + ''.join(ciphertxt))
        
# decrypt() doesn't work correctly, feel free to fix it

#    def decrypt(self, ciphertext, password, nBits):
#        blockSize = 16
#       if not nBits in [128,192,256]:
#            return
#        ciphertext = b64decode(ciphertext)
#        
#        nBytes = nBits/8
#        pwBytes = []
#        
#        for i in range(nBytes): pwBytes.append(ord(password[i])&0xff)
#        key = self.cipher(pwBytes, self.keyExpansion(pwBytes))
#        key = key + key[0:nBytes-16]
#       
#        counterBlock = [0]*16
#        ctrTxt = ciphertext[0:8]
#        for i in range(8): counterBlock.append(ord(ctrTxt[1]))
#        
#        keySchedule = self.keyExpansion(key)
#        
#        nBlocks = int(ceil(float(len(ciphertext)-8)/blockSize))
#        
#        ct = []
#        for b in range(nBlocks): ct.append(ciphertext[8+b*blockSize:(8+b*blockSize)+16])
#        ciphertext = ct
#
#        plaintxt = []
#        for b in range(nBlocks):
#            for c in range(4): counterBlock[15-c] = self.urs(b, c*8)&0xff
#            for c in range(4): counterBlock[15-c-4] = self.urs((b+1)/0x100000000-1, c*8)&0xff
#            
#            cipherCntr = self.cipher(counterBlock, keySchedule)
#            plaintxtByte = []
#            for i in range(len(ciphertext[b])):
#                plaintxtByte.append(cipherCntr[i] ^ ord(ciphertext[b][i]))
#                plaintxtByte[i] = chr(plaintxtByte[i])
#            plaintxt.append(''.join(plaintxtByte))
#        
#        plaintext = ''.join(plaintxt)
#        return plaintext