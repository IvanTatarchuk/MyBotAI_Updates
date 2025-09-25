import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  OneToMany,
  JoinColumn,
  Index,
} from 'typeorm';
import { User } from './User';
import { Asset } from './Asset';
import { Transaction } from './Transaction';

@Entity('portfolios')
@Index(['userId', 'assetId'], { unique: true })
export class Portfolio {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column('uuid')
  userId: string;

  @Column('uuid')
  assetId: string;

  @Column({ type: 'decimal', precision: 20, scale: 8, default: 0 })
  quantity: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, default: 0 })
  averagePrice: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, default: 0 })
  totalInvested: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, default: 0 })
  currentValue: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, default: 0 })
  unrealizedPnL: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, default: 0 })
  unrealizedPnLPercentage: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, default: 0 })
  realizedPnL: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, default: 0 })
  realizedPnLPercentage: number;

  @Column({ type: 'decimal', precision: 15, scale: 2, default: 0 })
  totalFees: number;

  @Column({ default: true })
  isActive: boolean;

  @Column({ nullable: true })
  lastUpdatedAt?: Date;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @ManyToOne(() => User, user => user.portfolios, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'userId' })
  user: User;

  @ManyToOne(() => Asset, asset => asset.portfolios, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'assetId' })
  asset: Asset;

  @OneToMany(() => Transaction, transaction => transaction.portfolio)
  transactions: Transaction[];

  get marketValue(): number {
    return this.quantity * this.currentValue;
  }

  get totalReturn(): number {
    return this.unrealizedPnL + this.realizedPnL;
  }

  get totalReturnPercentage(): number {
    if (this.totalInvested === 0) return 0;
    return (this.totalReturn / this.totalInvested) * 100;
  }
}