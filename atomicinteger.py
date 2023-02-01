from threading import Lock


class AtomicInteger():
    def __init__(self, value=0):
        self._value = int(value)
        self._lock = Lock()

    def increment_and_get(self):
        with self._lock:
            self._value += 1
            return self._value

    def decrement_and_get(self):
        with self._lock:
            self._value -= 1
            return self._value

    @property
    def value(self):
        with self._lock:
            return self._value

    @value.setter
    def set_value(self, val):
        with self._lock:
            self._value = int(val)
            return self._value


if __name__ == '__main__':
    ai = AtomicInteger(5)
    print(ai.value)
