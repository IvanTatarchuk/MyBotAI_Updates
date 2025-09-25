import jwt from 'jsonwebtoken';
import { User } from '../models/User';
import { AppDataSource } from '../config/database';
import { logger } from '../utils/logger';

export interface JWTPayload {
  userId: string;
  email: string;
  role: string;
}

export const authMiddleware = {
  generateToken(user: User): string {
    const payload: JWTPayload = {
      userId: user.id,
      email: user.email,
      role: user.role,
    };

    return jwt.sign(payload, process.env.JWT_SECRET!, {
      expiresIn: process.env.JWT_EXPIRE || '7d',
    });
  },

  async verifyToken(token: string): Promise<User | null> {
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET!) as JWTPayload;
      
      const userRepository = AppDataSource.getRepository(User);
      const user = await userRepository.findOne({
        where: { id: decoded.userId },
        relations: ['portfolios', 'subscriptions'],
      });

      if (!user || user.isLocked) {
        return null;
      }

      return user;
    } catch (error) {
      logger.error('Token verification failed:', error);
      return null;
    }
  },

  requireAuth(resolver: any) {
    return async (parent: any, args: any, context: any, info: any) => {
      if (!context.user) {
        throw new Error('Authentication required');
      }
      return resolver(parent, args, context, info);
    };
  },

  requireRole(roles: string[]) {
    return (resolver: any) => {
      return async (parent: any, args: any, context: any, info: any) => {
        if (!context.user) {
          throw new Error('Authentication required');
        }
        if (!roles.includes(context.user.role)) {
          throw new Error('Insufficient permissions');
        }
        return resolver(parent, args, context, info);
      };
    };
  },
};