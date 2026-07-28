import { ethers } from 'ethers';
import Web3 from 'web3';
import { logger } from '../utils/logger';

export class BlockchainService {
  private providers: Map<string, ethers.Provider | Web3> = new Map();

  constructor() {
    this.initializeProviders();
  }

  private initializeProviders() {
    // Ethereum
    this.providers.set(
      'ethereum',
      new ethers.JsonRpcProvider(process.env.ETHEREUM_RPC_URL || 'https://eth-mainnet.g.alchemy.com/v2/demo')
    );

    // Binance Smart Chain
    this.providers.set(
      'bsc',
      new ethers.JsonRpcProvider('https://bsc-dataseed.binance.org/')
    );

    // Polygon
    this.providers.set(
      'polygon',
      new ethers.JsonRpcProvider('https://polygon-rpc.com/')
    );

    // Arbitrum
    this.providers.set(
      'arbitrum',
      new ethers.JsonRpcProvider('https://arb1.arbitrum.io/rpc')
    );
  }

  async getTransaction(chain: string, txHash: string) {
    try {
      const provider = this.providers.get(chain) as ethers.Provider;
      
      if (!provider) {
        throw new Error(`Chain ${chain} not supported`);
      }

      const tx = await provider.getTransaction(txHash);
      const receipt = await provider.getTransactionReceipt(txHash);

      return {
        hash: tx?.hash,
        from: tx?.from,
        to: tx?.to,
        value: tx?.value ? ethers.formatEther(tx.value) : '0',
        gasPrice: tx?.gasPrice ? ethers.formatUnits(tx.gasPrice, 'gwei') : '0',
        gasUsed: receipt?.gasUsed?.toString(),
        status: receipt?.status === 1 ? 'success' : 'failed',
        blockNumber: receipt?.blockNumber,
        confirmations: tx?.confirmations,
      };
    } catch (error) {
      logger.error(`Error fetching transaction ${txHash} on ${chain}:`, error);
      throw error;
    }
  }

  async getBalance(chain: string, address: string) {
    try {
      const provider = this.providers.get(chain) as ethers.Provider;
      
      if (!provider) {
        throw new Error(`Chain ${chain} not supported`);
      }

      const balance = await provider.getBalance(address);
      return ethers.formatEther(balance);
    } catch (error) {
      logger.error(`Error fetching balance for ${address} on ${chain}:`, error);
      throw error;
    }
  }

  async getTokenBalance(chain: string, tokenAddress: string, walletAddress: string) {
    try {
      const provider = this.providers.get(chain) as ethers.Provider;
      
      if (!provider) {
        throw new Error(`Chain ${chain} not supported`);
      }

      const abi = [
        'function balanceOf(address owner) view returns (uint256)',
        'function decimals() view returns (uint8)',
        'function symbol() view returns (string)',
      ];

      const contract = new ethers.Contract(tokenAddress, abi, provider);
      
      const [balance, decimals, symbol] = await Promise.all([
        contract.balanceOf(walletAddress),
        contract.decimals(),
        contract.symbol(),
      ]);

      return {
        balance: ethers.formatUnits(balance, decimals),
        decimals,
        symbol,
      };
    } catch (error) {
      logger.error(`Error fetching token balance:`, error);
      throw error;
    }
  }

  async sendTransaction(chain: string, transaction: any) {
    try {
      const provider = this.providers.get(chain) as ethers.Provider;
      
      if (!provider) {
        throw new Error(`Chain ${chain} not supported`);
      }

      // In production, would use secure wallet management
      const wallet = new ethers.Wallet(transaction.privateKey, provider);
      
      const tx = await wallet.sendTransaction({
        to: transaction.to,
        value: ethers.parseEther(transaction.value),
        gasPrice: transaction.gasPrice ? ethers.parseUnits(transaction.gasPrice, 'gwei') : undefined,
      });

      await tx.wait();

      return {
        hash: tx.hash,
        from: tx.from,
        to: tx.to,
        value: transaction.value,
        status: 'confirmed',
      };
    } catch (error) {
      logger.error(`Error sending transaction on ${chain}:`, error);
      throw error;
    }
  }

  async estimateGas(chain: string, transaction: any) {
    try {
      const provider = this.providers.get(chain) as ethers.Provider;
      
      if (!provider) {
        throw new Error(`Chain ${chain} not supported`);
      }

      const gasEstimate = await provider.estimateGas({
        to: transaction.to,
        value: ethers.parseEther(transaction.value || '0'),
        data: transaction.data || '0x',
      });

      const gasPrice = await provider.getFeeData();

      return {
        gasLimit: gasEstimate.toString(),
        gasPrice: gasPrice.gasPrice ? ethers.formatUnits(gasPrice.gasPrice, 'gwei') : '0',
        maxFeePerGas: gasPrice.maxFeePerGas ? ethers.formatUnits(gasPrice.maxFeePerGas, 'gwei') : '0',
        maxPriorityFeePerGas: gasPrice.maxPriorityFeePerGas ? ethers.formatUnits(gasPrice.maxPriorityFeePerGas, 'gwei') : '0',
      };
    } catch (error) {
      logger.error(`Error estimating gas on ${chain}:`, error);
      throw error;
    }
  }
}