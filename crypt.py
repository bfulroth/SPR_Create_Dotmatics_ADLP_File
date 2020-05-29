import os
from cryptography.fernet import Fernet


class Crypt:

    def __init__(self):

        self.key = os.getenv('KEY')
        self.key_bytes = bytearray(self.key, 'utf-8')
        self.f = Fernet(self.key_bytes)

        self.token = b'gAAAAABelKD258g-GXgybV__' \
                     b'Q51l4eouesDb7Frhfqf9XvSXZ0J1lZePSExmxZmneUINXpkc76mKTXnNeOfcmChruG1C_QaZnQ=='
