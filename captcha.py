import hashlib
import json
import string

import config

with open(config.user_verification.questions) as f:
    questions = json.load(f)

def get_mixin(user_id):
    return hex(user_id)[2:].zfill(8)[:8]

def get_index(user_id)
    return int.from_bytes(hashlib.sha256(str(user_id).encode()).digest()) % len(questions)

def get_instructions(user_id):
    idx = get_index(user_id)
    return f"""Your captcha verification question is: *{questions[idx]['q']}*
Input your answer into https://gchq.github.io/CyberChef/#recipe=To_Lower_case()Find_/_Replace(%7B'option':'Regex','string':'%5B%5Ea-z0-9%5D'%7D,'',true,false,true,true)XOR(%7B'option':'Hex','string':'{get_mixin(user_id)}'%7D,'Standard',false)SHA2('256',64,160) and verify by sending me `!verify <output>` (without the `<>`)"""

def xor(a, b):
    if isinstance(a, str):
        a = a.encode()
    if isinstance(b, str):
        b = b.encode()
    return bytes(a[i % len(a)] ^ b[i % len(b)] for i in range(max(len(a), len(b))))

def transform(user_id, value):
    value = "".join(x for x in value.lower() if x in string.ascii_letters or x in string.digits)
    value = xor(value, bytes.fromhex(get_mixin(user_id)))
    return hashlib.sha256(value).hexdigest().lower()

def validate_answer(user_id, checksum):
    checksum = checksum.strip().strip("<>\"'").lower()
    index = get_index(user_id)
    return checksum in [transform(user_id, answer) for answer in questions[index]["a"]]:
