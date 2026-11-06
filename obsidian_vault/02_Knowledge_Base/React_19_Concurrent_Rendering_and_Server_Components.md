# React 19 Concurrent Rendering and Server Components

## Key Primitives in React 19
- **`useActionState`:** Simplifies form handling by managing pending states, return values, and form actions natively.
- **`useOptimistic`:** Displays immediate UI updates before network confirmation, automatically rolling back on failure.
- **`use` Hook:** Resolves promises and contexts directly inside components during render.

```tsx
import { useOptimistic } from 'react';

export function CommentList({ comments, addCommentAction }: { comments: Comment[]; addCommentAction: (c: string) => Promise<void> }) {
  const [optimisticComments, setOptimisticComments] = useOptimistic(
    comments,
    (state, newText: string) => [...state, { id: Date.now(), text: newText, sending: true }]
  );

  return (
    <div>
      {optimisticComments.map(c => (
        <p key={c.id} style={{ opacity: c.sending ? 0.6 : 1 }}>{c.text}</p>
      ))}
      <form action={async (formData) => {
        const text = formData.get('comment') as string;
        setOptimisticComments(text);
        await addCommentAction(text);
      }}>
        <input name="comment" required />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```
