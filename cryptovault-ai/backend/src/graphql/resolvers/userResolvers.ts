import bcrypt from 'bcryptjs';
import { AppDataSource } from '../../config/database';
import { User } from '../../models/User';
import { authMiddleware } from '../../middleware/auth';
import { sendEmail } from '../../services/emailService';
import { generateVerificationToken, generateResetToken } from '../../utils/tokens';
import { logger } from '../../utils/logger';
import speakeasy from 'speakeasy';
import QRCode from 'qrcode';

export const userResolvers = {
  Query: {
    me: authMiddleware.requireAuth(async (_: any, __: any, context: any) => {
      return context.user;
    }),

    user: authMiddleware.requireAuth(async (_: any, { id }: any) => {
      const userRepository = AppDataSource.getRepository(User);
      return await userRepository.findOne({
        where: { id },
        relations: ['portfolios', 'subscriptions'],
      });
    }),

    users: authMiddleware.requireRole(['ADMIN'])(
      async (_: any, { limit = 10, offset = 0 }: any) => {
        const userRepository = AppDataSource.getRepository(User);
        return await userRepository.find({
          take: limit,
          skip: offset,
          relations: ['portfolios', 'subscriptions'],
        });
      }
    ),
  },

  Mutation: {
    register: async (_: any, { input }: any) => {
      const userRepository = AppDataSource.getRepository(User);
      
      try {
        // Check if user exists
        const existingUser = await userRepository.findOne({
          where: { email: input.email },
        });

        if (existingUser) {
          throw new Error('Email already registered');
        }

        // Hash password
        const hashedPassword = await bcrypt.hash(input.password, 12);

        // Create user
        const user = userRepository.create({
          ...input,
          password: hashedPassword,
          emailVerificationToken: generateVerificationToken(),
          preferences: {
            defaultCurrency: 'USD',
            timezone: 'UTC',
            notifications: {
              email: true,
              push: true,
              priceAlerts: true,
            },
          },
        });

        await userRepository.save(user);

        // Send verification email
        await sendEmail({
          to: user.email,
          subject: 'Welcome to CryptoVault AI - Verify Your Email',
          template: 'welcome',
          data: {
            name: user.firstName,
            verificationLink: `${process.env.FRONTEND_URL}/verify-email?token=${user.emailVerificationToken}`,
          },
        });

        // Generate token
        const token = authMiddleware.generateToken(user);

        logger.info(`New user registered: ${user.email}`);

        return {
          token,
          user,
        };
      } catch (error) {
        logger.error('Registration error:', error);
        throw error;
      }
    },

    login: async (_: any, { input }: any) => {
      const userRepository = AppDataSource.getRepository(User);
      
      try {
        // Find user
        const user = await userRepository.findOne({
          where: { email: input.email },
          relations: ['subscriptions'],
        });

        if (!user) {
          throw new Error('Invalid credentials');
        }

        // Check if account is locked
        if (user.isLocked) {
          throw new Error('Account is locked. Please contact support.');
        }

        // Verify password
        const validPassword = await bcrypt.compare(input.password, user.password);

        if (!validPassword) {
          // Increment login attempts
          user.loginAttempts += 1;
          
          if (user.loginAttempts >= 5) {
            user.lockedUntil = new Date(Date.now() + 30 * 60 * 1000); // Lock for 30 minutes
          }
          
          await userRepository.save(user);
          throw new Error('Invalid credentials');
        }

        // Check 2FA if enabled
        if (user.twoFactorEnabled && !input.twoFactorCode) {
          throw new Error('Two-factor authentication code required');
        }

        if (user.twoFactorEnabled) {
          const verified = speakeasy.totp.verify({
            secret: user.twoFactorSecret!,
            encoding: 'base32',
            token: input.twoFactorCode,
            window: 2,
          });

          if (!verified) {
            throw new Error('Invalid two-factor authentication code');
          }
        }

        // Reset login attempts and update last login
        user.loginAttempts = 0;
        user.lockedUntil = null;
        user.lastLoginAt = new Date();
        await userRepository.save(user);

        // Generate token
        const token = authMiddleware.generateToken(user);

        logger.info(`User logged in: ${user.email}`);

        return {
          token,
          user,
        };
      } catch (error) {
        logger.error('Login error:', error);
        throw error;
      }
    },

    updateUser: authMiddleware.requireAuth(
      async (_: any, { input }: any, context: any) => {
        const userRepository = AppDataSource.getRepository(User);
        
        try {
          const user = await userRepository.findOne({
            where: { id: context.user.id },
          });

          if (!user) {
            throw new Error('User not found');
          }

          // Update user fields
          Object.assign(user, input);
          
          await userRepository.save(user);

          logger.info(`User updated: ${user.email}`);

          return user;
        } catch (error) {
          logger.error('Update user error:', error);
          throw error;
        }
      }
    ),

    enable2FA: authMiddleware.requireAuth(
      async (_: any, __: any, context: any) => {
        const userRepository = AppDataSource.getRepository(User);
        
        try {
          const user = await userRepository.findOne({
            where: { id: context.user.id },
          });

          if (!user) {
            throw new Error('User not found');
          }

          // Generate secret
          const secret = speakeasy.generateSecret({
            name: `CryptoVault AI (${user.email})`,
            length: 32,
          });

          // Temporarily store secret
          user.twoFactorSecret = secret.base32;
          await userRepository.save(user);

          // Generate QR code
          const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url!);

          return qrCodeUrl;
        } catch (error) {
          logger.error('Enable 2FA error:', error);
          throw error;
        }
      }
    ),

    disable2FA: authMiddleware.requireAuth(
      async (_: any, { code }: any, context: any) => {
        const userRepository = AppDataSource.getRepository(User);
        
        try {
          const user = await userRepository.findOne({
            where: { id: context.user.id },
          });

          if (!user || !user.twoFactorEnabled) {
            throw new Error('Two-factor authentication not enabled');
          }

          // Verify code
          const verified = speakeasy.totp.verify({
            secret: user.twoFactorSecret!,
            encoding: 'base32',
            token: code,
            window: 2,
          });

          if (!verified) {
            throw new Error('Invalid authentication code');
          }

          // Disable 2FA
          user.twoFactorEnabled = false;
          user.twoFactorSecret = null;
          await userRepository.save(user);

          logger.info(`2FA disabled for user: ${user.email}`);

          return true;
        } catch (error) {
          logger.error('Disable 2FA error:', error);
          throw error;
        }
      }
    ),

    verifyEmail: async (_: any, { token }: any) => {
      const userRepository = AppDataSource.getRepository(User);
      
      try {
        const user = await userRepository.findOne({
          where: { emailVerificationToken: token },
        });

        if (!user) {
          throw new Error('Invalid verification token');
        }

        user.emailVerified = true;
        user.emailVerificationToken = null;
        await userRepository.save(user);

        logger.info(`Email verified for user: ${user.email}`);

        return true;
      } catch (error) {
        logger.error('Email verification error:', error);
        throw error;
      }
    },

    requestPasswordReset: async (_: any, { email }: any) => {
      const userRepository = AppDataSource.getRepository(User);
      
      try {
        const user = await userRepository.findOne({
          where: { email },
        });

        if (!user) {
          // Don't reveal if email exists
          return true;
        }

        // Generate reset token
        const resetToken = generateResetToken();
        user.passwordResetToken = resetToken;
        user.passwordResetExpires = new Date(Date.now() + 3600000); // 1 hour
        await userRepository.save(user);

        // Send reset email
        await sendEmail({
          to: user.email,
          subject: 'Reset Your CryptoVault AI Password',
          template: 'password-reset',
          data: {
            name: user.firstName,
            resetLink: `${process.env.FRONTEND_URL}/reset-password?token=${resetToken}`,
          },
        });

        logger.info(`Password reset requested for: ${user.email}`);

        return true;
      } catch (error) {
        logger.error('Password reset request error:', error);
        throw error;
      }
    },

    resetPassword: async (_: any, { token, newPassword }: any) => {
      const userRepository = AppDataSource.getRepository(User);
      
      try {
        const user = await userRepository.findOne({
          where: {
            passwordResetToken: token,
          },
        });

        if (!user || !user.passwordResetExpires || 
            user.passwordResetExpires < new Date()) {
          throw new Error('Invalid or expired reset token');
        }

        // Hash new password
        user.password = await bcrypt.hash(newPassword, 12);
        user.passwordResetToken = null;
        user.passwordResetExpires = null;
        await userRepository.save(user);

        logger.info(`Password reset for user: ${user.email}`);

        return true;
      } catch (error) {
        logger.error('Password reset error:', error);
        throw error;
      }
    },

    deleteAccount: authMiddleware.requireAuth(
      async (_: any, { password }: any, context: any) => {
        const userRepository = AppDataSource.getRepository(User);
        
        try {
          const user = await userRepository.findOne({
            where: { id: context.user.id },
          });

          if (!user) {
            throw new Error('User not found');
          }

          // Verify password
          const validPassword = await bcrypt.compare(password, user.password);

          if (!validPassword) {
            throw new Error('Invalid password');
          }

          // Soft delete or anonymize user data
          user.email = `deleted_${user.id}@cryptovault.ai`;
          user.firstName = 'Deleted';
          user.lastName = 'User';
          user.password = '';
          user.deletedAt = new Date();
          await userRepository.save(user);

          logger.info(`Account deleted: ${context.user.id}`);

          return true;
        } catch (error) {
          logger.error('Delete account error:', error);
          throw error;
        }
      }
    ),
  },

  User: {
    fullName: (user: User) => `${user.firstName} ${user.lastName}`,
    
    currentSubscription: async (user: User) => {
      if (user.subscriptions && user.subscriptions.length > 0) {
        return user.subscriptions
          .filter(sub => sub.status === 'ACTIVE')
          .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())[0];
      }
      return null;
    },
  },
};