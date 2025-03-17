# AptAi - Advanced Aptos Blockchain Analytics

Advanced AI-powered SDK for DeFi & NFT analytics on Aptos

## Installation

```bash
pip install aptai
```

## Requirements

- Python 3.11+
- Groq API key

## Quick Start

```python
import aptai

aptai.init(
    groq_api_key="your_groq_api_key",
    system_prompt="Custom AI system prompt", 
    max_tokens=200,                          
    temperature=0.7                          
)

# Get token prices and analytics
apt_price = aptai.get_price("aptos")
print(apt_price)

# Get detailed wallet analysis
wallet_info = aptai.get_detailed_wallet("wallet_address")
print(wallet_info)

# Get NFT collection data
nft_data = aptai.get_nft_data("collection_address")
print(nft_data)

# AI-powered market analysis
analysis = aptai.ai_analysis("What's driving APT price today?")
print(analysis)
```

## Core Features

### Real-Time Analytics
- Multi-source price tracking (DexScreener, CoinGecko)
- Historical price data with volatility metrics
- Transaction volume analysis
- Market sentiment tracking

### Comprehensive Wallet Tracking
- Token balances and holdings
- NFT portfolio analysis
- Transaction history
- DeFi interaction tracking
- Risk assessment

### NFT Analytics
- Cross-marketplace data (Topaz, Souffl3)
- Collection statistics
- Floor price tracking
- Ownership analysis
- Volume metrics

### AI Integration
- Market trend analysis
- Price predictions
- Custom market queries
- Automated insights
- Risk assessment

## Contact

- X: [@Teckdegen](https://x.com/Teckdegen)
- Telegram: [@Teck_degen](https://t.me/Teck_degen)

## License

MIT License