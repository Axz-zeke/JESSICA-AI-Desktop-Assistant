# TanStack Query Caching and Optimistic Updates

## Asynchronous State Management
TanStack Query (React Query v5) abstracts network cache invalidation, deduplication, and background refetching away from local state.
- **`staleTime`:** Duration data remains fresh before background refetch occurs.
- **`gcTime` (Garbage Collection):** Duration unused cache entries remain in memory before disposal.

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query';

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (updatedUser: User) => {
      const res = await fetch(`/api/user/${updatedUser.id}`, {
        method: 'PUT',
        body: JSON.stringify(updatedUser),
      });
      return res.json();
    },
    onMutate: async (newUser) => {
      // Cancel outbound queries
      await queryClient.cancelQueries({ queryKey: ['user', newUser.id] });
      const previousUser = queryClient.getQueryData(['user', newUser.id]);
      // Optimistically update cache
      queryClient.setQueryData(['user', newUser.id], newUser);
      return { previousUser };
    },
    onError: (err, newUser, context) => {
      // Rollback on failure
      queryClient.setQueryData(['user', newUser.id], context?.previousUser);
    },
    onSettled: (data, err, variables) => {
      queryClient.invalidateQueries({ queryKey: ['user', variables.id] });
    },
  });
}
```
