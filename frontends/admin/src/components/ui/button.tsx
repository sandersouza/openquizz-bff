import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "@/lib/utils";

const variantClasses = {
  default: "button-default",
  destructive: "button-destructive",
  outline: "button-outline",
  secondary: "button-secondary",
  ghost: "button-ghost",
  link: "button-link",
} as const;

const sizeClasses = {
  default: "button-size-default",
  sm: "button-size-sm",
  lg: "button-size-lg",
  icon: "button-size-icon",
} as const;

type Variant = keyof typeof variantClasses;
type Size = keyof typeof sizeClasses;

function Button({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"button"> & {
  variant?: Variant;
  size?: Size;
  asChild?: boolean;
}) {
  const Comp = asChild ? Slot : "button";
  return (
    <Comp
      data-slot="button"
      className={cn(
        "button",
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    />
  );
}

export { Button };
