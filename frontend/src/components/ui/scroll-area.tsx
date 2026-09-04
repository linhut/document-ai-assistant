// (c) 2026 Jose AI (https://www.linhut.cn)
// https://github.com/linhut/document-ai-assistant
// Licensed under the MIT License. See the LICENSE file for details.

import * as React from "react"
import { cn } from "@/lib/utils"

const ScrollArea = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, children, ...props }, ref) => (
    <div ref={ref} className={cn("relative overflow-auto", className)} {...props}>
      {children}
    </div>
  )
)
ScrollArea.displayName = "ScrollArea"

export { ScrollArea }
