import datetime as dt
from pydantic import BaseModel, Field
from typing import Optional

class TokenPair(BaseModel):
    tokenAddress: str
    marketCap: float
    liquidity: dict
    holders: int
    volume: float
    trending_rank: int
    # Ajout du champ pour le temps de création, mappé depuis "pairCreatedAt"
    pair_created_at: Optional[dt.datetime] = Field(None, alias="pairCreatedAt")
