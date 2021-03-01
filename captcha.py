import hashlib
import json
import string

import config

with open(config.user_verification.questions) as f:
    questions = json.load(f)

def get_mixin(user_id):
    return hex(user_id)[2:].zfill(8)[:8]

def get_index(user_id):
    return int.from_bytes(hashlib.sha256(str(user_id).encode()).digest(), byteorder="big") % len(questions)

def get_instructions(user_id):
    idx = get_index(user_id)
    return f"""Your verification question is: *{questions[idx]['q']}*
Verify your answer by sending me `!verify <answer>` (without the `<>`)"""

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
    reference = questions[index]["a"]
    if isinstance(reference, str):
        return checksum == transform(user_id, reference)
    return checksum in [transform(user_id, answer) for answer in reference]
