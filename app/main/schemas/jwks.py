from pydantic import BaseModel
from typing import List

class JwksItem(BaseModel):
    alg: str = None
    kid: str = None
    kty: str = None
    n: str = None
    use: str = None

class Jwks(BaseModel):
    keys: List[JwksItem]
