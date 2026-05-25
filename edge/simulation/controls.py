import time

class Controls:
    def __init__(self):
        self.steering = 0
        self.throttle = 0
        self.brake = 0
        self.last_remote_time = 0

        self.connection_alive = True
        self.safe_mode = False

    def apply_remote_command(self, command):
        if self.safe_mode:
            print("🚫 Commande ignorée (SAFE MODE)")
            return

        self.steering = command.get("steering", 0)
        self.throttle = command.get("throttle", 0)
        self.brake = command.get("brake", 0)
        self.last_remote_time = time.time()
        self.connection_alive = True

        print("🎮 Commande distante appliquée:", command)

    def emergency_stop(self):
        self.steering = 0
        self.throttle = 0
        self.brake = 1
        self.last_remote_time = time.time()
        print("🛑 Emergency stop activé")

    def update_keyboard_fallback(self):
        if self.safe_mode:
            self.emergency_stop()
            return

        if not self.connection_alive:
            self.emergency_stop()
            return