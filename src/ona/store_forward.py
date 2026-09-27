"""
Store-and-forward queue for connectivity drops
"""
import sqlite3
import threading
import time
import os
import logging

class StoreForwardQueue:
    def __init__(self, db_path="/var/lib/living_map/queue.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.lock = threading.Lock()
        self._init_db()
        
    def _init_db(self):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS queue
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          timestamp REAL,
                          topic TEXT,
                          payload TEXT,
                          priority INTEGER,
                          sent INTEGER)''')
            conn.commit()
            conn.close()
            
    def enqueue(self, topic: str, payload_json: str, priority: int = 0):
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute("INSERT INTO queue (timestamp, topic, payload, priority, sent) VALUES (?, ?, ?, ?, 0)",
                          (time.time(), topic, payload_json, priority))
                conn.commit()
                conn.close()
            except Exception as e:
                logging.error(f"Enqueue failed: {e}")
                
    def drain(self, uplink_manager):
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute("SELECT id, topic, payload FROM queue WHERE sent=0 ORDER BY priority DESC, timestamp ASC")
                rows = c.fetchall()
                for row in rows:
                    if uplink_manager.is_connected():
                        import json
                        success = uplink_manager._publish(row[1], json.loads(row[2]))
                        if success:
                            c.execute("UPDATE queue SET sent=1 WHERE id=?", (row[0],))
                            conn.commit()
                    else:
                        break
                conn.close()
            except Exception as e:
                logging.error(f"Drain failed: {e}")
                
    def get_queue_depth(self) -> int:
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM queue WHERE sent=0")
                count = c.fetchone()[0]
                conn.close()
                return count
            except:
                return 0
                
    def prune_expired(self, max_age_hours=24):
        with self.lock:
            try:
                cutoff = time.time() - (max_age_hours * 3600)
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute("DELETE FROM queue WHERE timestamp < ? OR sent=1", (cutoff,))
                conn.commit()
                conn.close()
            except Exception as e:
                logging.error(f"Prune failed: {e}")
