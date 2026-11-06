# TypeScript Strict Generics and Type Narrowing

## Advanced Type Narrowing Techniques
TypeScript leverages control flow analysis to narrow broad unions into specific concrete types using:
1. **Discriminated Unions:** Tagged property guarantees exhaustive `switch` cases.
2. **Custom Type Guards (`val is TargetType`):** Validates structure at runtime while narrowing compiler AST.
3. **Template Literal Types:** Enforces string patterns (e.g. `type HexColor = \`#\${string}\``).

```typescript
type ApiResponse<T> = 
  | { status: 'success'; data: T; timestamp: number }
  | { status: 'error'; message: string; code: number };

function handleResponse<T>(res: ApiResponse<T>): T {
  if (res.status === 'error') {
    throw new Error(`API Error [${res.code}]: ${res.message}`);
  }
  // TypeScript automatically narrows res to { status: 'success'; data: T }
  return res.data;
}

// Exhaustiveness checking with never type
type Shape = { kind: 'circle'; radius: number } | { kind: 'square'; size: number };

function getArea(shape: Shape): number {
  switch (shape.kind) {
    case 'circle': return Math.PI * shape.radius ** 2;
    case 'square': return shape.size ** 2;
    default:
      const _exhaustive: never = shape;
      throw new Error(`Unhandled shape: ${_exhaustive}`);
  }
}
```
