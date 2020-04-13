import os
from cryptography.fernet import Fernet

key = os.getenv('KEY')
f = Fernet(key)
token = b'gAAAAABelFcFgskl4vIUgWAjqZpJ9bAIqE-LKvjRCopMBNTQU8q6EQAi5UXKnTaLm94tsYH0DqCeEaeedVqMsgbZqfp_JB_moA=='