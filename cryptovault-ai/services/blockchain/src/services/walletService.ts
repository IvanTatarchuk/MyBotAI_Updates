import { ethers } from 'ethers';
import { encrypt, decrypt } from '../utils/crypto';
import { logger } from '../utils/logger';

export class WalletService {
  async createWallet(userId: string, chain: string) {
    try {
      const wallet = ethers.Wallet.createRandom();
      
      // Encrypt private key before storing
      const encryptedPrivateKey = encrypt(wallet.privateKey);
      
      // In production, store in secure database
      const walletData = {
        userId,
        chain,
        address: wallet.address,
        publicKey: wallet.publicKey,
        encryptedPrivateKey,
        createdAt: new Date(),
      };

      logger.info(`Created wallet for user ${userId} on ${chain}: ${wallet.address}`);

      return {
        address: wallet.address,
        chain,
        // Never return private key in response
      };
    } catch (error) {
      logger.error('Error creating wallet:', error);
      throw error;
    }
  }

  async importWallet(userId: string, privateKey: string, chain: string) {
    try {
      const wallet = new ethers.Wallet(privateKey);
      
      // Encrypt private key before storing
      const encryptedPrivateKey = encrypt(privateKey);
      
      // In production, store in secure database
      const walletData = {
        userId,
        chain,
        address: wallet.address,
        publicKey: wallet.publicKey,
        encryptedPrivateKey,
        imported: true,
        createdAt: new Date(),
      };

      logger.info(`Imported wallet for user ${userId} on ${chain}: ${wallet.address}`);

      return {
        address: wallet.address,
        chain,
      };
    } catch (error) {
      logger.error('Error importing wallet:', error);
      throw error;
    }
  }

  async getWallets(userId: string) {
    try {
      // In production, fetch from database
      const wallets = []; // Placeholder
      
      return wallets.map(w => ({
        address: w.address,
        chain: w.chain,
        createdAt: w.createdAt,
      }));
    } catch (error) {
      logger.error('Error fetching wallets:', error);
      throw error;
    }
  }

  async signTransaction(userId: string, walletAddress: string, transaction: any) {
    try {
      // In production, fetch encrypted private key from database
      // and decrypt it
      const encryptedPrivateKey = ''; // Fetch from DB
      const privateKey = decrypt(encryptedPrivateKey);
      
      const wallet = new ethers.Wallet(privateKey);
      
      if (wallet.address.toLowerCase() !== walletAddress.toLowerCase()) {
        throw new Error('Wallet address mismatch');
      }

      const signedTx = await wallet.signTransaction(transaction);
      
      return {
        signedTransaction: signedTx,
        from: wallet.address,
      };
    } catch (error) {
      logger.error('Error signing transaction:', error);
      throw error;
    }
  }

  async signMessage(userId: string, walletAddress: string, message: string) {
    try {
      // In production, fetch encrypted private key from database
      const encryptedPrivateKey = ''; // Fetch from DB
      const privateKey = decrypt(encryptedPrivateKey);
      
      const wallet = new ethers.Wallet(privateKey);
      
      if (wallet.address.toLowerCase() !== walletAddress.toLowerCase()) {
        throw new Error('Wallet address mismatch');
      }

      const signature = await wallet.signMessage(message);
      
      return {
        signature,
        address: wallet.address,
      };
    } catch (error) {
      logger.error('Error signing message:', error);
      throw error;
    }
  }

  async exportWallet(userId: string, walletAddress: string, password: string) {
    try {
      // Additional authentication would be required
      // This is simplified for demo
      
      // Fetch encrypted private key
      const encryptedPrivateKey = ''; // Fetch from DB
      const privateKey = decrypt(encryptedPrivateKey);
      
      const wallet = new ethers.Wallet(privateKey);
      
      if (wallet.address.toLowerCase() !== walletAddress.toLowerCase()) {
        throw new Error('Wallet address mismatch');
      }

      // Encrypt wallet with user's password
      const encryptedJson = await wallet.encrypt(password);
      
      return {
        encryptedWallet: encryptedJson,
      };
    } catch (error) {
      logger.error('Error exporting wallet:', error);
      throw error;
    }
  }
}