import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  OneToMany,
  Index,
} from 'typeorm';
import { Portfolio } from './Portfolio';
import { Transaction } from './Transaction';
import { AIPrediction } from './AIPrediction';

export enum AssetType {
  CRYPTOCURRENCY = 'cryptocurrency',
  STOCK = 'stock',
  FOREX = 'forex',
  COMMODITY = 'commodity',
  INDEX = 'index',
  ETF = 'etf',
  BOND = 'bond',
  DERIVATIVE = 'derivative'
}

export enum AssetStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  DELISTED = 'delisted',
  SUSPENDED = 'suspended'
}

@Entity('assets')
@Index(['symbol'], { unique: true })
@Index(['type', 'status'])
export class Asset {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  symbol: string;

  @Column()
  name: string;

  @Column({ nullable: true })
  fullName?: string;

  @Column({
    type: 'enum',
    enum: AssetType
  })
  type: AssetType;

  @Column({
    type: 'enum',
    enum: AssetStatus,
    default: AssetStatus.ACTIVE
  })
  status: AssetStatus;

  @Column({ type: 'decimal', precision: 20, scale: 8, default: 0 })
  currentPrice: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, default: 0 })
  marketCap: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, default: 0 })
  volume24h: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, default: 0 })
  change24h: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, default: 0 })
  change24hPercentage: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, nullable: true })
  high24h?: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, nullable: true })
  low24h?: number;

  @Column({ type: 'decimal', precision: 20, scale: 8, default: 0 })
  circulatingSupply: number;

  @Column({ type: 'decimal', precision: 20, scale: 8, nullable: true })
  totalSupply?: number;

  @Column({ type: 'decimal', precision: 20, scale: 8, nullable: true })
  maxSupply?: number;

  @Column({ type: 'decimal', precision: 5, scale: 4, default: 0 })
  priceChange1h: number;

  @Column({ type: 'decimal', precision: 5, scale: 4, default: 0 })
  priceChange7d: number;

  @Column({ type: 'decimal', precision: 5, scale: 4, default: 0 })
  priceChange30d: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, nullable: true })
  allTimeHigh?: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, nullable: true })
  allTimeLow?: number;

  @Column({ nullable: true })
  logoUrl?: string;

  @Column({ nullable: true })
  website?: string;

  @Column({ nullable: true })
  whitepaper?: string;

  @Column({ nullable: true })
  github?: string;

  @Column({ type: 'text', nullable: true })
  description?: string;

  @Column({ type: 'jsonb', nullable: true })
  metadata?: {
    decimals?: number;
    contractAddress?: string;
    blockchain?: string;
    algorithm?: string;
    consensus?: string;
    launchDate?: string;
    exchanges?: string[];
    social?: {
      twitter?: string;
      telegram?: string;
      discord?: string;
      reddit?: string;
    };
    technical?: {
      hashrate?: number;
      difficulty?: number;
      blockTime?: number;
      blockSize?: number;
    };
  };

  @Column({ default: true })
  isTradable: boolean;

  @Column({ default: false })
  isFeatured: boolean;

  @Column({ type: 'decimal', precision: 5, scale: 2, default: 0 })
  volatility: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, default: 0 })
  liquidity: number;

  @Column({ nullable: true })
  lastPriceUpdate?: Date;

  @Column({ nullable: true })
  lastVolumeUpdate?: Date;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @OneToMany(() => Portfolio, portfolio => portfolio.asset)
  portfolios: Portfolio[];

  @OneToMany(() => Transaction, transaction => transaction.asset)
  transactions: Transaction[];

  @OneToMany(() => AIPrediction, prediction => prediction.asset)
  predictions: AIPrediction[];

  get displayName(): string {
    return this.fullName || this.name;
  }

  get isPositiveChange(): boolean {
    return this.change24hPercentage >= 0;
  }

  get priceFormatted(): string {
    return this.currentPrice.toFixed(8);
  }

  get marketCapFormatted(): string {
    if (this.marketCap >= 1e12) {
      return `$${(this.marketCap / 1e12).toFixed(2)}T`;
    } else if (this.marketCap >= 1e9) {
      return `$${(this.marketCap / 1e9).toFixed(2)}B`;
    } else if (this.marketCap >= 1e6) {
      return `$${(this.marketCap / 1e6).toFixed(2)}M`;
    } else {
      return `$${this.marketCap.toFixed(2)}`;
    }
  }

  get volumeFormatted(): string {
    if (this.volume24h >= 1e12) {
      return `$${(this.volume24h / 1e12).toFixed(2)}T`;
    } else if (this.volume24h >= 1e9) {
      return `$${(this.volume24h / 1e9).toFixed(2)}B`;
    } else if (this.volume24h >= 1e6) {
      return `$${(this.volume24h / 1e6).toFixed(2)}M`;
    } else {
      return `$${this.volume24h.toFixed(2)}`;
    }
  }
}