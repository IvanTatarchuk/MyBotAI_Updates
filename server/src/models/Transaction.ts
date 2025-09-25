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
import { User } from './User';
import { Asset } from './Asset';
import { Portfolio } from './Portfolio';

export enum TransactionType {
  BUY = 'buy',
  SELL = 'sell',
  DEPOSIT = 'deposit',
  WITHDRAWAL = 'withdrawal',
  TRANSFER = 'transfer',
  DIVIDEND = 'dividend',
  INTEREST = 'interest',
  FEE = 'fee',
  REBATE = 'rebate'
}

export enum TransactionStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  PARTIALLY_FILLED = 'partially_filled'
}

export enum OrderType {
  MARKET = 'market',
  LIMIT = 'limit',
  STOP = 'stop',
  STOP_LIMIT = 'stop_limit',
  TRAILING_STOP = 'trailing_stop',
  ICEBERG = 'iceberg',
  TWAP = 'twap'
}

export enum TimeInForce {
  GTC = 'gtc', // Good Till Cancelled
  IOC = 'ioc', // Immediate or Cancel
  FOK = 'fok', // Fill or Kill
  DAY = 'day'  // Day Order
}

@Entity('transactions')
@Index(['userId', 'createdAt'])
@Index(['assetId', 'createdAt'])
@Index(['status', 'createdAt'])
export class Transaction {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column('uuid')
  userId: string;

  @Column('uuid')
  assetId: string;

  @Column('uuid', { nullable: true })
  portfolioId?: string;

  @Column({
    type: 'enum',
    enum: TransactionType
  })
  type: TransactionType;

  @Column({
    type: 'enum',
    enum: TransactionStatus,
    default: TransactionStatus.PENDING
  })
  status: TransactionStatus;

  @Column({
    type: 'enum',
    enum: OrderType,
    nullable: true
  })
  orderType?: OrderType;

  @Column({
    type: 'enum',
    enum: TimeInForce,
    default: TimeInForce.GTC
  })
  timeInForce: TimeInForce;

  @Column({ type: 'decimal', precision: 20, scale: 8, default: 0 })
  quantity: number;

  @Column({ type: 'decimal', precision: 20, scale: 8, default: 0 })
  filledQuantity: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, nullable: true })
  limitPrice?: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, nullable: true })
  stopPrice?: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, default: 0 })
  averagePrice: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, default: 0 })
  totalAmount: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, default: 0 })
  fees: number;

  @Column({ type: 'decimal', precision: 5, scale: 4, default: 0 })
  feeRate: number;

  @Column({ nullable: true })
  externalId?: string;

  @Column({ nullable: true })
  exchange?: string;

  @Column({ type: 'jsonb', nullable: true })
  metadata?: {
    source?: string;
    ipAddress?: string;
    userAgent?: string;
    executionTime?: number;
    slippage?: number;
    marketImpact?: number;
    notes?: string;
  };

  @Column({ nullable: true })
  failureReason?: string;

  @Column({ nullable: true })
  completedAt?: Date;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @ManyToOne(() => User, user => user.transactions, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'userId' })
  user: User;

  @ManyToOne(() => Asset, asset => asset.transactions, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'assetId' })
  asset: Asset;

  @ManyToOne(() => Portfolio, portfolio => portfolio.transactions, { onDelete: 'SET NULL' })
  @JoinColumn({ name: 'portfolioId' })
  portfolio?: Portfolio;

  get isCompleted(): boolean {
    return this.status === TransactionStatus.COMPLETED;
  }

  get isPending(): boolean {
    return this.status === TransactionStatus.PENDING || this.status === TransactionStatus.PROCESSING;
  }

  get remainingQuantity(): number {
    return this.quantity - this.filledQuantity;
  }

  get fillPercentage(): number {
    if (this.quantity === 0) return 0;
    return (this.filledQuantity / this.quantity) * 100;
  }

  get netAmount(): number {
    if (this.type === TransactionType.BUY || this.type === TransactionType.DEPOSIT) {
      return this.totalAmount + this.fees;
    } else {
      return this.totalAmount - this.fees;
    }
  }
}