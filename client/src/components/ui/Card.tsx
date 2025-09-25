import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hover?: boolean;
  gradient?: boolean;
  glass?: boolean;
  padding?: 'sm' | 'md' | 'lg' | 'none';
  className?: string;
}

export const Card: React.FC<CardProps> = ({
  children,
  hover = false,
  gradient = false,
  glass = false,
  padding = 'md',
  className,
  ...props
}) => {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
    none: '',
  };

  const baseClasses = cn(
    'rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 transition-all duration-300',
    paddingClasses[padding],
    {
      'hover:shadow-xl hover:scale-[1.02] hover:-translate-y-1': hover,
      'bg-gradient-to-br from-primary-50 to-purple-50 dark:from-gray-800 dark:to-gray-900': gradient,
      'glass': glass,
      'bg-white dark:bg-gray-900': !gradient && !glass,
    },
    className
  );

  return (
    <motion.div
      className={baseClasses}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      {...props}
    >
      {children}
    </motion.div>
  );
};