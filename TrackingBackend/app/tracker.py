from __future__ import annotations
from .logger import get_logger
from .config import EyeTrackConfig
from app.processes import EyeProcessor, Camera
from multiprocessing.managers import SyncManager
from queue import Queue
from .types import EyeID, EyeData
import cv2

logger = get_logger()


class Tracker:
    def __init__(self, eye_id: EyeID, config: EyeTrackConfig, osc_queue: Queue[EyeData], manager: SyncManager):
        # IPC stuff
        self.manager = manager
        self.image_queue: Queue[cv2.Mat] = self.manager.Queue()
        self.osc_queue: Queue[EyeData] = osc_queue
        # --------------------------------------------------------
        self.eye_id = eye_id
        self.config = config
        self.eye_config = (self.config.left_eye, self.config.right_eye)[bool(self.eye_id.value)]  # god i love python
        # processes
        self.camera = Camera(self.eye_config, self.eye_id, self.image_queue)
        self.eye_processor = EyeProcessor(self.image_queue, self.osc_queue, self.config.algorithm, self.eye_id)

    def start(self) -> None:
        self.camera.start()
        self.eye_processor.start()

    def stop(self) -> None:
        self.camera.stop()
        self.eye_processor.stop()

    def restart(self) -> None:
        self.camera.restart()
        self.eye_processor.restart()
