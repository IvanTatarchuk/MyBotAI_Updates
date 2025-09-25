import { DataSource } from 'typeorm';
import { User } from '../models/User';
import { Portfolio } from '../models/Portfolio';
import { Transaction } from '../models/Transaction';
import { Subscription } from '../models/Subscription';
import { logger } from '../utils/logger';

export const AppDataSource = new DataSource({
  type: 'postgres',
  url: process.env.DATABASE_URL,
  synchronize: process.env.NODE_ENV === 'development',
  logging: process.env.NODE_ENV === 'development',
  entities: [User, Portfolio, Transaction, Subscription],
  migrations: ['src/migrations/*.ts'],
  subscribers: ['src/subscribers/*.ts'],
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

export const connectDatabase = async () => {
  try {
    await AppDataSource.initialize();
    logger.info('Database connection established');
  } catch (error) {
    logger.error('Database connection failed:', error);
    throw error;
  }
};