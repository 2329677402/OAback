#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/10/2 下午9:16
@ Author      : Poco Ray
@ File        : aeser.py
@ Description : AES加密算法, 用于加密链接中的用户邮箱
"""

import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher(object):
    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        """加密输入的明文(raw)"""
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode())).decode('utf-8')

    def decrypt(self, enc):
        """解密输入的密文(enc)"""
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return AESCipher._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        """对输入的明文进行填充, 使其长度符合AES的块大小要求"""
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        """对解密后的明文进行去填充"""
        return s[:-ord(s[len(s) - 1:])]
