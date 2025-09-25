import rateLimit from 'express-rate-limit';
import { Request, Response } from 'express';

export const rateLimiter = rateLimit({
  windowMs: (parseInt(process.env.RATE_LIMIT_WINDOW || '15') * 60 * 1000), // 15 minutes
  max: parseInt(process.env.RATE_LIMIT_MAX || '100'), // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req: Request): string => {
    // Use user ID if authenticated, otherwise use IP
    const userId = req.headers['x-user-id'] as string;
    return userId || req.ip || 'unknown';
  },
  skip: (req: Request): boolean => {
    // Skip rate limiting for certain paths
    const skipPaths = ['/health', '/metrics'];
    return skipPaths.includes(req.path);
  },
});

export const apiRateLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 30, // limit each IP to 30 API requests per minute
  message: 'API rate limit exceeded. Please upgrade your plan for higher limits.',
  standardHeaders: true,
  legacyHeaders: false,
});