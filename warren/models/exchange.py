from pydantic import BaseModel


class BaseExchange(BaseModel):
    name: str


class UniswapV2Exchange(BaseExchange):
    factory_address: str
    router_address: str


class UniswapV3Exchange(BaseExchange):
    pool_address: str
    router_address: str    
    quoter_address: str


uniswap_v3_quoter = UniswapV3Exchange(
    pool_address="0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8",
    router_address="0xE592427A0AEce92De3Edee1F18E0157C05861564",    
    quoter_address="0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"   
)


uniswap_v3_quoter_v2 = UniswapV3Exchange(
    pool_address="0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8",
    router_address="0xE592427A0AEce92De3Edee1F18E0157C05861564",    
    quoter_address="0x61fFE014bA17989E743c5F6cB21bF9697530B21e"   
)


uniswap_v2_router01 = UniswapV2Exchange(
    factory_address="0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
    router_address="0xf164fC0Ec4E93095b804a4795bBe1e041497b92a"
)


uniswap_v2_router02 = UniswapV2Exchange(
    factory_address="0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
    router_address="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
)


pancakeswap = UniswapV2Exchange(
    factory_address="0x1097053Fd2ea711dad45caCcc45EfF7548fCB362",
    router_address="0xEfF92A263d31888d860bD50809A8D171709b7b1c"
)


sushiswap = UniswapV2Exchange(
    factory_address="0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac",
    router_address="0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
)
