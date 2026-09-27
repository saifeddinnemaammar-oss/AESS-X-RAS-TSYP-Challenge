"""Main Executor orchestrator node."""
import time
import logging
import argparse
import sys

from .config import EXECUTOR_ID
from .mission_planner import MissionPlanner
from .beacon_navigator import BeaconNavigator
from .event_verifier import EventVerifier
from .lora_handler import ExecutorLoRa
from .status_monitor import StatusMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExecutorNode:
    def __init__(self, sim_mode=False):
        self.sim_mode = sim_mode
        self.state = "IDLE"
        
        self.planner = MissionPlanner()
        self.lora = ExecutorLoRa()
        self.navigator = BeaconNavigator(self.lora)
        self.verifier = EventVerifier()
        self.monitor = StatusMonitor()
        
    def run(self):
        logger.info(f"Starting Executor Node {EXECUTOR_ID}")
        self.lora.start()
        
        try:
            while True:
                if self.monitor.should_abort():
                    self.state = "RETURNING"
                
                if self.state == "IDLE":
                    self.state = "BRIEFING"
                    
                elif self.state == "BRIEFING":
                    mission = self.lora.receive_mission_from_ona()
                    self.planner.receive_mission(mission)
                    self.lora.send_ack_to_ona()
                    self.state = "READY"
                    
                elif self.state == "READY":
                    self.state = "ENTERING"
                    
                elif self.state == "ENTERING":
                    logger.info("Entering mission area.")
                    self.state = "NAVIGATING"
                    
                elif self.state == "NAVIGATING":
                    target = self.planner.get_next_target()
                    if not target:
                        logger.info("All targets processed.")
                        self.state = "RETURNING"
                        continue
                        
                    logger.info(f"Navigating to {target}")
                    success = self.navigator.home_to_beacon(target)
                    if success:
                        self.state = "VERIFYING"
                        self.current_target = target
                    else:
                        self.planner.mark_failed(target, "unreachable")
                        
                elif self.state == "VERIFYING":
                    # Mock sensor readings
                    readings = {'thermal_max': 37.0, 'mq2': 100, 'mq7': 50}
                    b_data = self.planner.chain.get(self.current_target, {})
                    verified, t, conf = self.verifier.verify_event(b_data, readings)
                    self.lora.upload_verification(self.current_target, verified)
                    self.planner.mark_completed(self.current_target)
                    self.state = "ACTING"
                    
                elif self.state == "ACTING":
                    logger.info("Performing action (drop payload / mark).")
                    self.state = "NAVIGATING"
                    
                elif self.state == "RETURNING":
                    logger.info("Returning to ONA.")
                    self.state = "DONE"
                    
                elif self.state == "DONE":
                    logger.info("Mission complete. Shutting down.")
                    break
                    
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interrupted by user.")
        finally:
            self.lora.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sim', action='store_true', help="Run in simulation mode")
    args = parser.parse_args()
    
    node = ExecutorNode(sim_mode=args.sim)
    node.run()
