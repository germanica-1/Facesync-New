import RPi.GPIO as GPIO
import time

# GPIO pin config
BUZZER_PIN = 19

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)

def buzz(duration=0.5, repeat=1, interval=0.2):
    """Buzz pattern for UNKNOWN face"""
    for _ in range(repeat):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(interval)

def buzz_success():
    """Buzz pattern for MATCHED face (short–long chirp)"""
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(0.3)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def cleanup():
    """Cleanup GPIO pins"""
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.cleanup()
