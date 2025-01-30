import time
from collections import deque
from typing import Dict

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_windows: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if user_id not in self.user_windows:
            return
        user_deque = self.user_windows[user_id]
        cutoff = current_time - self.window_size
        # Видаляємо всі записи, які старіші за поточне вікно
        while user_deque and user_deque[0] <= cutoff:
            user_deque.popleft()
        # Якщо вікно порожнє, видаляємо користувача
        if not user_deque:
            del self.user_windows[user_id]

    def can_send_message(self, user_id: str) -> bool:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        user_deque = self.user_windows.get(user_id, deque())
        return len(user_deque) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        current_time = time.time()
        allowed = self.can_send_message(user_id)
        if allowed:
            if user_id not in self.user_windows:
                self.user_windows[user_id] = deque()
            self.user_windows[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        user_deque = self.user_windows.get(user_id, deque())
        if len(user_deque) < self.max_requests:
            return 0.0
        else:
            earliest_time = user_deque[0]
            time_remaining = earliest_time + self.window_size - current_time
            return max(0.0, time_remaining)

def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)
    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    import random
    random.seed(42)
    test_rate_limiter()