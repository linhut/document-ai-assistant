// (c) 2026 Jose AI (https://www.linhut.cn)
// https://github.com/linhut/document-ai-assistant
// Licensed under the MIT License. See the LICENSE file for details.

import * as React from "react"
import { cn } from "@/lib/utils"

const Label = React.forwardRef<HTMLLabelElement, React.LabelHTMLAttributes<HTMLLabelElement>>(
  ({ className, ...props }, ref) => (
    <label ref={ref} className={cn("text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70", className)} {...props} />
  )
)
Label.displayName = "Label"

export { Label }
