"""Mission planning and management for Executor."""
import logging
from .config import PRIORITY_VICTIM, PRIORITY_FIRE, PRIORITY_GAS, PRIORITY_CHECKPOINT

logger = logging.getLogger(__name__)

class MissionPlanner:
    def __init__(self):
        self.chain = {}  # beacon_id -> beacon_data
        self.mission_state = "IDLE"
        self.priority_queue = []
        self.visited = set()
        self.failed = set()

    def receive_mission(self, mission_data):
        self.chain = mission_data
        self.mission_state = "BRIEFED"
        self.build_priority_queue()
        logger.info(f"Mission received with {len(self.chain)} beacons.")

    def build_priority_queue(self):
        # Sort targets by priority
        targets = []
        for b_id, b_data in self.chain.items():
            b_type = b_data.get('type', 0)
            priority = PRIORITY_CHECKPOINT
            if b_type == 1: priority = PRIORITY_VICTIM
            elif b_type == 2: priority = PRIORITY_FIRE
            elif b_type == 3: priority = PRIORITY_GAS
            targets.append((priority, b_id))
        
        # Sort descending by priority
        targets.sort(key=lambda x: x[0], reverse=True)
        self.priority_queue = [t[1] for t in targets]

    def get_next_target(self):
        for b_id in self.priority_queue:
            if b_id not in self.visited and b_id not in self.failed:
                return b_id
        return None

    def mark_completed(self, beacon_id):
        self.visited.add(beacon_id)
        logger.info(f"Marked beacon {beacon_id} as completed.")

    def mark_failed(self, beacon_id, reason):
        self.failed.add(beacon_id)
        logger.warning(f"Marked beacon {beacon_id} as failed: {reason}")

    def replan(self):
        logger.info("Replanning route...")
        # Simple replan: just get next target from queue that isn't failed/visited
        pass

    def get_return_chain(self):
        # Return sequence from current position using pointers
        # Assuming chain structure has 'next_id' pointing towards home or similar
        logger.info("Building return chain.")
        return []
