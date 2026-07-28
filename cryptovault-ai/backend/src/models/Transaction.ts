import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
  Index,
} from 'typeorm';
import { Portfolio } from './Portfolio';

export enum TransactionType {
  BUY = 'buy',
  SELL = 'sell',
  TRANSFER_IN = 'transfer_in',
  TRANSFER_OUT = 'transfer_out',
  STAKING_REWARD = 'staking_reward',
  AIRDROP = 'airdrop',
  FEE = 'fee',
}

@Entity('transactions')
@Index(['portfolioId', 'timestamp'])
@Index(['symbol', 'type'])
export class Transaction {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  portfolioId: string;

  @ManyToOne(() => Portfolio, (portfolio) => portfolio.transactions)
  @JoinColumn({ name: 'portfolioId' })
  portfolio: Portfolio;

  @Column({
    type: 'enum',
    enum: TransactionType,
  })
  type: TransactionType;

  @Column()
  symbol: string;

  @Column({ type: 'decimal', precision: 20, scale: 8 })
  amount: number;

  @Column({ type: 'decimal', precision: 20, scale: 8 })
  price: number;

  @Column({ type: 'decimal', precision: 20, scale: 8 })
  total: number;

  @Column({ type: 'decimal', precision: 20, scale: 8, default: 0 })
  fee: number;

  @Column()
  currency: string;

  @Column()
  exchange: string;

  @Column({ nullable: true })
  exchangeTransactionId: string;

  @Column({ nullable: true })
  blockchainTxHash: string;

  @Column({ nullable: true })
  walletAddress: string;

  @Column({ type: 'jsonb', nullable: true })
  metadata: {
    gasFee?: number;
    gasPrice?: number;
    gasUsed?: number;
    network?: string;
    confirmations?: number;
    notes?: string;
  };

  @Column()
  timestamp: Date;

  @Column({ default: 'completed' })
  status: 'pending' | 'completed' | 'failed' | 'cancelled';

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}