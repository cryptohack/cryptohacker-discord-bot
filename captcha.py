import hashlib
import json
import string

import config

with open(config.user_verification.questions) as f:
    questions = json.load(f)

def get_index(user_id):
    return int.from_bytes(hashlib.sha256(str(user_id).encode()).digest(), byteorder="big") % len(questions)

def get_instructions(user_id):
    idx = get_index(user_id)
    return f"""Your verification question is: *{questions[idx]['q']}*
Verify your answer by sending me `!verify <answer>` (without the `<>`)"""

def clean(value):
    return "".join(x for x in value.lower() if x in string.ascii_letters or x in string.digits)

def validate_answer(user_id, checksum):
    checksum = clean(checksum)
    index = get_index(user_id)
    reference = questions[index]["a"]
    if isinstance(reference, str):
        return checksum == clean(reference)
    return checksum in [clean(answer) for answer in reference]
