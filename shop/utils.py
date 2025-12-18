import uuid

def generate_order_id():
    return f'ORD-{uuid.uuid4().hex[:10].upper()}'