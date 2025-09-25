import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@apollo/server/express4';
import { createServer } from 'http';
import { logger } from './utils/logger';
import { connectDatabase } from './config/database';
import { typeDefs, resolvers } from './graphql';
import { authMiddleware } from './middleware/auth';
import { rateLimiter } from './middleware/rateLimiter';
import { errorHandler } from './middleware/errorHandler';

// Load environment variables
dotenv.config();

const app = express();
const httpServer = createServer(app);
const PORT = process.env.PORT || 4000;

async function startServer() {
  try {
    // Connect to database
    await connectDatabase();
    logger.info('Database connected successfully');

    // Apollo Server setup
    const apolloServer = new ApolloServer({
      typeDefs,
      resolvers,
      introspection: process.env.NODE_ENV === 'development',
    });

    await apolloServer.start();

    // Middleware
    app.use(cors({
      origin: process.env.FRONTEND_URL || 'http://localhost:3000',
      credentials: true,
    }));
    
    app.use(express.json({ limit: '10mb' }));
    app.use(rateLimiter);

    // Health check
    app.get('/health', (req, res) => {
      res.json({ status: 'ok', timestamp: new Date().toISOString() });
    });

    // GraphQL endpoint
    app.use(
      '/graphql',
      expressMiddleware(apolloServer, {
        context: async ({ req }) => {
          const token = req.headers.authorization?.replace('Bearer ', '');
          const user = token ? await authMiddleware.verifyToken(token) : null;
          return { user, req };
        },
      })
    );

    // Error handling
    app.use(errorHandler);

    httpServer.listen(PORT, () => {
      logger.info(`🚀 Server running at http://localhost:${PORT}`);
      logger.info(`📊 GraphQL endpoint: http://localhost:${PORT}/graphql`);
    });

  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

startServer();

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully');
  httpServer.close(() => {
    logger.info('Server closed');
    process.exit(0);
  });
});