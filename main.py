from web3 import Web3
from ABI_config import ABI_Uniswap_v2_Pair, ABI_Uniswap_v2_Factory
from config import INFURA_ID

# Подключение к Ethereum узлу через Infura
infura_url = f'https://mainnet.infura.io/v3/{INFURA_ID}'
web3 = Web3(Web3.HTTPProvider(infura_url))

if not web3.is_connected():
    print("Failed to connect to Ethereum network")
    exit()

print("Connected to Ethereum network")
print("Current block number:", web3.eth.block_number)

# Контракты Uniswap v2
uniswap_v2_router_address = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'  # Адрес Uniswap V2 Factory
uniswap_v2_router_abi = ABI_Uniswap_v2_Factory  # ABI Uniswap V2 Factory

# Подключение к контракту Uniswap V2 Factory
uniswap_v2_factory = web3.eth.contract(address=uniswap_v2_router_address, abi=uniswap_v2_router_abi)

# Пулы
pools = [
    '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc',  # ETH/USDC pool
    '0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11'  # ETH/DAI pool
]

# ABI для пары Uniswap V2
pair_abi = ABI_Uniswap_v2_Pair  # ABI Uniswap V2 Pair


def get_reserves(pool_address):
    pool_contract = web3.eth.contract(address=pool_address, abi=pair_abi)
    return pool_contract.functions.getReserves().call()


def get_tokens(pool_address):
    pool_contract = web3.eth.contract(address=pool_address, abi=pair_abi)
    token0 = pool_contract.functions.token0().call()
    token1 = pool_contract.functions.token1().call()
    return token0, token1


def get_price(reserves, token0, token1):
    # Определяем, какой из токенов является WETH
    if token0 == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2':  # WETH
        reserve_eth = reserves[0]
        reserve_other = reserves[1]
    elif token1 == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2':  # WETH
        reserve_eth = reserves[1]
        reserve_other = reserves[0]
    else:
        raise ValueError("WETH token not found in the pool")

    if reserve_eth == 0:
        return 0

    return reserve_other / reserve_eth


# Получаем резервы и цены для двух пулов
reserves_pool1 = get_reserves(pools[0])
reserves_pool2 = get_reserves(pools[1])

tokens_pool1 = get_tokens(pools[0])
tokens_pool2 = get_tokens(pools[1])

# Выводим отладочную информацию
print(f"Резервы первого пула: {reserves_pool1}")
print(f"Токены первого пула: {tokens_pool1}")

print(f"Резервы второго пула: {reserves_pool2}")
print(f"Токены второго пула: {tokens_pool2}")

price_pool1 = get_price(reserves_pool1, tokens_pool1[0], tokens_pool1[1])
price_pool2 = get_price(reserves_pool2, tokens_pool2[0], tokens_pool2[1])

# Вычисляем разницу в цене в процентах
if price_pool1 == 0 or price_pool2 == 0:
    price_difference_percentage = 0
else:
    price_difference_percentage = abs(price_pool1 - price_pool2) / ((price_pool1 + price_pool2) / 2) * 100

# Выводим результаты
print(f"Адрес первого пула: {pools[0]}")
print(f"Цена в первом пуле: {price_pool1:.6f} USDC/ETH")

print(f"Адрес второго пула: {pools[1]}")
print(f"Цена во втором пуле: {price_pool2:.6f} DAI/ETH")

print(f"Разница в цене: {price_difference_percentage:.2f}%")

if price_difference_percentage > 0.5:
    print("Возможна арбитражная возможность!")
