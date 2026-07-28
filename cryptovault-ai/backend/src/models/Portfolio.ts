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
import { Transaction } from './Transaction';

@Entity('portfolios')
@Index(['userId', 'name'])
export class Portfolio {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  name: string;

  @Column({ nullable: true })
  description: string;

  @Column()
  userId: string;

  @ManyToOne(() => User, (user) => user.portfolios)
  @JoinColumn({ name: 'userId' })
  user: User;

  @Column({ type: 'jsonb', default: {} })
  holdings: {
    [symbol: string]: {
      amount: number;
      averageBuyPrice: number;
      currentPrice: number;
      value: number;
      profitLoss: number;
      profitLossPercentage: number;
      lastUpdated: Date;
    };
  };

  @Column({ type: 'decimal', precision: 20, scale: 8, default: 0 })
  totalValue: number;

  @Column({ type: 'decimal', precision: 20, scale: 8, default: 0 })
  totalCost: number;

  @Column({ type: 'decimal', precision: 20, scale: 8, default: 0 })
  totalProfitLoss: number;

  @Column({ type: 'decimal', precision: 10, scale: 2, default: 0 })
  totalProfitLossPercentage: number;

  @Column({ default: 'USD' })
  baseCurrency: string;

  @Column({ type: 'jsonb', nullable: true })
  performance: {
    day: number;
    week: number;
    month: number;
    quarter: number;
    year: number;
    allTime: number;
  };

  @Column({ type: 'jsonb', nullable: true })
  riskMetrics: {
    volatility: number;
    sharpeRatio: number;
    beta: number;
    maxDrawdown: number;
    valueAtRisk: number;
  };

  @Column({ default: false })
  isPublic: boolean;

  @Column({ nullable: true })
  publicUrl: string;

  @Column({ type: 'jsonb', nullable: true })
  alerts: {
    priceAlerts: Array<{
      symbol: string;
      condition: 'above' | 'below';
      price: number;
      enabled: boolean;
    }>;
    portfolioAlerts: Array<{
      type: 'value' | 'profitLoss';
      condition: 'above' | 'below';
      value: number;
      enabled: boolean;
    }>;
  };

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @OneToMany(() => Transaction, (transaction) => transaction.portfolio)
  transactions: Transaction[];
}