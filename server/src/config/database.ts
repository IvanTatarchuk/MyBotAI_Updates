import { DataSource } from 'typeorm';
import { User } from '../models/User';
import { Portfolio } from '../models/Portfolio';
import { Transaction } from '../models/Transaction';
import { Asset } from '../models/Asset';
import { TradingSession } from '../models/TradingSession';
import { AIPrediction } from '../models/AIPrediction';
import { Notification } from '../models/Notification';
import { AuditLog } from '../models/AuditLog';
import { Config } from '../models/Config';

export const AppDataSource = new DataSource({
  type: 'postgres',
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  username: process.env.DB_USERNAME || 'postgres',
  password: process.env.DB_PASSWORD || 'password',
  database: process.env.DB_NAME || 'trading_platform',
  synchronize: process.env.NODE_ENV === 'development',
  logging: process.env.NODE_ENV === 'development',
  entities: [
    User,
    Portfolio,
    Transaction,
    Asset,
    TradingSession,
    AIPrediction,
    Notification,
    AuditLog,
    Config,
  ],
  migrations: ['dist/migrations/*.js'],
  subscribers: ['dist/subscribers/*.js'],
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
  extra: {
    max: 20,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
  },
});