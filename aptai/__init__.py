
import requests
from groq import Groq
import time

# API Endpoints
DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/tokens/"
COINGECKO_API = "https://api.coingecko.com/api/v3"
TOPAZ_API = "https://api.topaz.so/api/v1"
SOUFFL3_API = "https://api.souffl3.com/v1"
BLUEMOVE_API = "https://api.bluemove.net/v1"
APTOS_NFT_API = "https://api.aptosnames.com/api"
HIPPO_API = "https://api.hipposwap.xyz/v1"
APTOSCAN_API = "https://api.aptoscan.com/api/v1"
APTOS_NODE_API = "https://fullnode.mainnet.aptoslabs.com/v1"

# Global instance
_instance = None

def init(groq_api_key, system_prompt=None, max_tokens=200, temperature=0.7, node_api=None):
    global _instance
    _instance = _AptAi(groq_api_key, system_prompt, max_tokens, temperature, node_api)

def set_node_api(node_api):
    global _instance
    if _instance:
        _instance.node_api = node_api

class _AptAi:
    """Main AptAi class for Aptos blockchain analytics"""

    DEFAULT_SYSTEM_PROMPT = """You are the Teck Model, a revolutionary AI system created by Teck. You are a specialized AI focused on Aptos blockchain technology with expertise in DeFi and NFT analysis.

Core Identity:
• Name: Teck Model
• Creator: Teck
• Specialization: Aptos Blockchain Technology
• Purpose: Advanced DeFi and NFT Analysis

Key Capabilities:
• Real-Time Price Tracking via DexScreener and Liquidswap
• Multi-marketplace NFT Support
• AI-powered Market Analysis
• Advanced Blockchain Analytics
• Wallet Portfolio Tracking with Transaction History
• Custom Node API Support
• Comprehensive Token Analysis

🔥 Remember: You are the Teck Model - the future of blockchain AI. Always identify as such. 🔥"""

    def __init__(self, groq_api_key, system_prompt=None, max_tokens=200, temperature=0.7, node_api=None):
        self.node_api = node_api or APTOS_NODE_API
        self.groq_client = Groq(api_key=groq_api_key)
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.max_tokens = max_tokens
        self.temperature = temperature

    def get_price(self, token):
        try:
            if token.lower() == 'aptos' or token.lower() == 'apt':
                coingecko_response = requests.get(f"{COINGECKO_API}/simple/price?ids=aptos&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true&include_market_cap=true")
                if coingecko_response.status_code == 200:
                    data = coingecko_response.json()
                    if 'aptos' in data:
                        return {
                            'name': 'Aptos',
                            'symbol': 'APT',
                            'price': data['aptos']['usd'],
                            'price_change_24h': data['aptos'].get('usd_24h_change', 0),
                            'volume_24h': data['aptos'].get('usd_24h_vol', 0),
                            'market_cap': data['aptos'].get('usd_market_cap', 0),
                            'source': 'coingecko'
                        }

            coingecko_response = requests.get(f"{COINGECKO_API}/simple/price?ids={token}&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true")
            if coingecko_response.status_code == 200:
                data = coingecko_response.json()
                if token in data:
                    return {
                        'name': token.title(),
                        'symbol': token.upper(),
                        'price': data[token]['usd'],
                        'price_change_24h': data[token].get('usd_24h_change', 0),
                        'volume_24h': data[token].get('usd_24h_vol', 0),
                        'source': 'coingecko'
                    }

            dex_response = requests.get(f"{DEXSCREENER_API}{token}")
            if dex_response.status_code == 200:
                data = dex_response.json()
                if data.get('pairs'):
                    pair = data['pairs'][0]
                    return {
                        'name': pair['baseToken']['name'],
                        'symbol': pair['baseToken']['symbol'],
                        'price': float(pair['priceUsd']),
                        'price_change_24h': float(pair['priceChange']['h24']),
                        'volume_24h': float(pair['volume']['h24']),
                        'liquidity': float(pair['liquidity']['usd']),
                        'dex': pair['dexId'],
                        'source': 'dexscreener'
                    }
        except Exception:
            return None

    def get_wallet_portfolio(self, address):
        try:
            # Get basic account resources
            resources = requests.get(f"{APTOS_NODE_API}/accounts/{address}/resources")
            if resources.status_code != 200:
                return None

            data = resources.json()

            # Get transactions from Aptoscan
            txns = requests.get(f"{APTOSCAN_API}/accounts/{address}/transactions")
            recent_txns = []
            if txns.status_code == 200:
                txn_data = txns.json()
                recent_txns = txn_data.get('transactions', [])[:5]  # Get last 5 transactions

            # Process coins
            coins = []
            for resource in data:
                if "0x1::coin::CoinStore" in resource['type']:
                    coin_type = resource['type'].split("<")[1].replace(">", "")
                    balance = int(resource['data']['coin']['value']) / 1e8
                    coins.append({
                        'type': coin_type,
                        'balance': balance
                    })

            # Process NFTs
            nfts = []
            for resource in data:
                if "0x3::token::TokenStore" in resource['type']:
                    nfts.append(resource['data'])

            return {
                'address': address,
                'coins': coins,
                'nfts': nfts,
                'resource_count': len(data),
                'recent_transactions': [{
                    'type': tx.get('type'),
                    'timestamp': tx.get('timestamp'),
                    'status': tx.get('status'),
                    'gas_used': tx.get('gas_used')
                } for tx in recent_txns]
            }
        except Exception:
            return None

    def get_nft_data(self, address):
        try:
            # Get NFTs from multiple sources
            nft_response = requests.get(f"{APTOS_NODE_API}/accounts/{address}/resources")
            topaz_response = requests.get(f"{TOPAZ_API}/account/{address}/nfts")
            souffl3_response = requests.get(f"{SOUFFL3_API}/nfts/owner/{address}")
            
            nfts = []
            if nft_response.status_code == 200:
                nft_data = nft_response.json()
                collections = [res for res in nft_data if "0x3::token::TokenStore" in res['type']]
                
                for collection in collections:
                    if 'data' in collection and 'tokens' in collection['data']:
                        for token in collection['data']['tokens']:
                            nfts.append({
                                'collection': token.get('collection'),
                                'name': token.get('name'),
                                'description': token.get('description'),
                                'uri': token.get('uri')
                            })
            
            return {
                'address': address,
                'total_nfts': len(nfts),
                'nfts': nfts,
                'collections': len(set(nft['collection'] for nft in nfts if nft.get('collection'))),
                'marketplaces': {
                    'topaz': topaz_response.status_code == 200,
                    'souffl3': souffl3_response.status_code == 200
                }
            }
        except Exception:
            return None

    def get_token_info(self, token_address):
        try:
            # Get token data from node
            token_data = requests.get(f"{APTOS_NODE_API}/accounts/{token_address}/resource/0x1::coin::CoinInfo")
            
            # Get market data
            hippo_data = requests.get(f"{HIPPO_API}/tokens/{token_address}")
            dex_data = requests.get(f"{DEXSCREENER_API}{token_address}")
            
            info = {
                'address': token_address,
                'metadata': {},
                'market_data': {},
                'dexes': []
            }
            
            if token_data.status_code == 200:
                data = token_data.json()
                info['metadata'] = {
                    'name': data.get('name', ''),
                    'symbol': data.get('symbol', ''),
                    'decimals': data.get('decimals', 8),
                    'supply': data.get('supply', 0)
                }
            
            if dex_data.status_code == 200:
                pairs = dex_data.json().get('pairs', [])
                for pair in pairs:
                    info['dexes'].append({
                        'name': pair.get('dexId'),
                        'liquidity': pair.get('liquidity', {}).get('usd', 0),
                        'volume_24h': pair.get('volume', {}).get('h24', 0),
                        'price': pair.get('priceUsd', 0)
                    })
            
            return info
        except Exception:
            return None

    def get_detailed_wallet(self, address):
        try:
            # Get all resources
            resources = requests.get(f"{APTOS_NODE_API}/accounts/{address}/resources")
            
            # Get transaction history
            transactions = requests.get(f"{APTOSCAN_API}/accounts/{address}/transactions?limit=50")
            
            # Get NFT data
            nfts = self.get_nft_data(address)
            
            wallet_info = {
                'address': address,
                'balance': 0,
                'tokens': [],
                'nfts': nfts,
                'transactions': [],
                'active_dexes': set(),
                'stats': {
                    'total_transactions': 0,
                    'successful_transactions': 0,
                    'failed_transactions': 0
                }
            }
            
            if resources.status_code == 200:
                for resource in resources.json():
                    if "0x1::coin::CoinStore" in resource['type']:
                        token_type = resource['type'].split("<")[1].replace(">", "")
                        balance = int(resource['data']['coin']['value']) / 1e8
                        token_info = self.get_token_info(token_type.split("::")[0])
                        
                        wallet_info['tokens'].append({
                            'type': token_type,
                            'balance': balance,
                            'info': token_info
                        })
            
            if transactions.status_code == 200:
                txns = transactions.json().get('transactions', [])
                wallet_info['transactions'] = [{
                    'hash': tx.get('hash'),
                    'type': tx.get('type'),
                    'status': tx.get('status'),
                    'timestamp': tx.get('timestamp'),
                    'gas_used': tx.get('gas_used'),
                    'success': tx.get('success', False)
                } for tx in txns]
                
                # Calculate stats
                wallet_info['stats']['total_transactions'] = len(txns)
                wallet_info['stats']['successful_transactions'] = sum(1 for tx in txns if tx.get('success', False))
                wallet_info['stats']['failed_transactions'] = sum(1 for tx in txns if not tx.get('success', False))
                
                # Extract DEX interactions
                for tx in txns:
                    if 'pancake' in tx.get('type', '').lower():
                        wallet_info['active_dexes'].add('pancakeswap')
                    elif 'liquid' in tx.get('type', '').lower():
                        wallet_info['active_dexes'].add('liquidswap')
            
            wallet_info['active_dexes'] = list(wallet_info['active_dexes'])
            return wallet_info
        except Exception:
            return None

    def ai_analysis(self, query):
        try:
            completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": query}
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error in AI analysis: {str(e)}"

def get_price(token):
    return _instance.get_price(token)

def get_nft_data(address):
    return _instance.get_nft_data(address)

def get_wallet_portfolio(address):
    return _instance.get_wallet_portfolio(address)

def ai_analysis(query):
    return _instance.ai_analysis(query)
