"use client";

/**
 * AnimatedStamp — Wraps TariffStamp with a "stamp press" animation.
 *
 * Animation sequence per stamp (staggered):
 * 1. Start invisible + scaled up (1.8x) + slight rotation
 * 2. Slam down quickly (scale → 1.0, opacity → 1) with spring physics
 * 3. Brief overshoot (scale 0.95 → 1.0) to simulate impact
 *
 * The stagger creates a satisfying "stamp stamp stamp" cascade effect.
 */

import { motion } from "framer-motion";
import type { TariffType } from "@/lib/types";
import { TariffStamp } from "./TariffStamp";

interface AnimatedStampProps {
  tariffType: TariffType;
  rate?: number | null;
  applied?: boolean;
  size?: "full" | "compact";
  index?: number;
  className?: string;
}

export function AnimatedStamp({
  tariffType,
  rate,
  applied = true,
  size = "full",
  index = 0,
  className = "",
}: AnimatedStampProps) {
  return (
    <motion.div
      initial={{
        opacity: 0,
        scale: 1.8,
        rotate: -15 + index * 8,
      }}
      animate={{
        opacity: 1,
        scale: 1,
        rotate: 0,
      }}
      transition={{
        type: "spring",
        stiffness: 600,
        damping: 20,
        mass: 0.8,
        delay: 0.3 + index * 0.25, // Stagger each stamp
      }}
      className={className}
    >
      <TariffStamp
        tariffType={tariffType}
        rate={rate}
        applied={applied}
        size={size}
        index={index}
      />
    </motion.div>
  );
}
