import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface LogoProps {
  size?: 'small' | 'medium' | 'large'
  animate?: boolean
  className?: string
}

export function Logo({ size = 'medium', animate = false, className }: LogoProps) {
  const sizeClasses = {
    small: 'w-8 h-8 text-sm',
    medium: 'w-10 h-10 text-base',
    large: 'w-12 h-12 text-lg'
  }

  const logoElement = (
    <div 
      className={cn(
        sizeClasses[size],
        "rounded-lg bg-gray-900 dark:bg-gray-100 flex items-center justify-center text-white dark:text-gray-900 font-bold shadow-sm",
        className
      )}
    >
      W
    </div>
  )

  if (animate) {
    return (
      <motion.div
        whileHover={{ scale: 1.05 }}
        animate={{ 
          rotate: [0, 5, -5, 0],
        }}
        transition={{ 
          duration: 4, 
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        {logoElement}
      </motion.div>
    )
  }

  return (
    <motion.div whileHover={{ scale: 1.05 }}>
      {logoElement}
    </motion.div>
  )
}