import threading

class ScanResultsStore:
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()

    def set(self, session_id, data):
        with self._lock:
            self._data[session_id] = data

    def get(self, session_id):
        with self._lock:
            return self._data.get(session_id)

    def delete(self, session_id):
        with self._lock:
            if session_id in self._data:
                del self._data[session_id]

scan_store = ScanResultsStore()
