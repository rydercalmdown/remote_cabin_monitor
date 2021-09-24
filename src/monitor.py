import os
import logging
import time
import datetime
from rtsparty import Stream
from objectdaddy import Daddy
from communicator import Communicator


class Monitor():
    """Class for monitoring the camera"""

    def __init__(self):
        """Instatiate the application"""
        logging.info('Starting application')
        self._set_defaults()
        self._setup_stream()
        self._setup_object_recognition()
        self._setup_communicator()

    def _set_defaults(self):
        """Set any application defaults"""
        self.last_detected = int(time.time())
        self.null_person_reporting_timeout_seconds = 86400
        self.from_email = os.environ['EMAIL_FROM']
        self.to_email = os.environ['EMAIL_TO']

    def _setup_communicator(self):
        """Sets up the communicator module"""
        self.communicator = Communicator()
        subject = "System Startup"
        body = f"The system was started at {str(datetime.datetime.now())}"
        self.communicator.send_email(self.from_email, self.to_email, subject, body)

    def _setup_stream(self):
        """Set up the stream to the camera"""
        logging.info('Starting local camera stream')
        self.stream = Stream()

    def _setup_object_recognition(self):
        """Set up object recognition and load models"""
        logging.info('Loading ML models')
        self.daddy = Daddy()
        self.daddy.set_callbacks(self.object_detected, self.object_expired)

    def object_detected(self, detection):
        """Callback for an object being detected"""
        logging.info(f'{detection.label} detected')
        try:
            if detection.is_person():
                self.report_person_detected()
        except Exception:
            pass

    def object_expired(self, detection):
        """Callback for an object expiring"""
        logging.info(f'{detection.label} expired')

    def report_person_detected(self):
        """Reports a person detected"""
        self.last_detected = int(time.time())
        detected_time = str(datetime.datetime.now())
        subject = "Person Detected"
        body = f"A person was detected at {detected_time}"
        self.communicator.send_email(self.from_email, self.to_email, subject, body)

    def check_for_null_timeout(self):
        """Checks for null timeout; has a person not been detected for a while?"""
        current = int(time.time())
        if current > self.last_detected + self.null_person_reporting_timeout_seconds :
            self.last_detected = current
            subject = "No People Detected"
            body = "No people were detected today."
            self.communicator.send_email(self.from_email, self.to_email, subject, body)
    
    def process_frames_from_stream(self):
        """Processes the frames from the stream"""
        while True:
            frame = self.stream.get_frame()
            if self.stream.is_frame_empty(frame):
                continue
            self.latest_frame = frame
            results, frame = self.daddy.process_frame(frame)
            self.check_for_null_timeout()

    def run(self):
        """Run the application"""
        try:
            self.process_frames_from_stream()
        except KeyboardInterrupt:
            logging.info('Exiting application')
