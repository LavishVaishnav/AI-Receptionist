import sqlite3
import time
import random
import threading
import math


class TimeoutException(Exception):
    pass


class AIReception:
    def __init__(self):
        self.state = "initial"
        self.db_connection = sqlite3.connect("emergency_db.sqlite")
        self.cursor = self.db_connection.cursor()
        self.create_index()

    def create_index(self):
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_emergency_type ON emergencies (emergency_type)"
        )
        self.db_connection.commit()

    def start_conversation(self):
        print(
            "\nHello, This is an AI Receptionist! Are you having an emergency or would you like to leave a message?"
        )
        response = input("Your response: ").lower()
        self.handle_initialresponse(response)

    def handle_initialresponse(self, response):
        if "emergency" in response:
            self.state = "emergency"
            self.handle_emergency()
        elif "message" in response:
            self.state = "message"
            self.handle_message()
        else:
            print(
                "\nI don't understand that. Please let me know if it's an emergency or a message."
            )
            self.start_conversation()

    def handle_emergency(self):
        print("\nWhat is the emergency?")
        emergency_response = input("Your emergency: ").lower()
        emergency_instruction = self.query_emergency_db(emergency_response)

        if "I don't have instructions" in emergency_instruction:
            eta = self.calculate_eta()
            print(
                f"\nI don't have specific instructions for this emergency.\nDr. Adrin will be coming to your location in approximately {eta} minutes."
            )
            self.ask_additional_help()

            return
        print(
            "\nI am checking what you should do immediately.\nMeanwhile, can you tell me where you are located?"
        )

        location = input("Your location: ")
        eta = self.calculate_eta()

        print(
            f"\nDr. Adrin will be coming to your location in approximately {eta} minutes."
        )
        print(
            "\nIf you are worried that the arrival will be too late, please type 'the arrival will be too late'.\nOtherwise wait for 15 Seconds, I will assume you are following the instructions."
        )

        try:
            arrival_concern = self.input_with_timeout("Your input: ", 15)
            if arrival_concern == "the arrival will be too late":
                print(
                    f"\nI understand you're worried the doctor may arrive in some time.\nMeanwhile, you should {emergency_instruction}."
                )
            else:
                print(f"\nPlease follow these steps: {emergency_instruction}")

        except TimeoutException:
            print(f"\nPlease follow these steps: {emergency_instruction}")

        self.ask_additional_help()

        self.schedule_followUp()

    def input_with_timeout(self, prompt, timeout):
        def worker():
            self.user_input = input(prompt)
            self.timeout_event.set()

        self.user_input = None
        self.timeout_event = threading.Event()
        input_thread = threading.Thread(target=worker)
        input_thread.start()
        self.timeout_event.wait(timeout)

        if self.timeout_event.is_set():
            return self.user_input
        else:
            raise TimeoutException

    def ask_additional_help(self):
        print(
            "\nMay I help you with anything else? Or You can also leave a message for Dr. Adrin while he is on the way."
        )
        additional_response = input("Your response: ").lower()

        if "message" in additional_response or "leave a message" in additional_response:
            self.handle_message()
        else:
            print("\nThank you for your patience. Dr. Adrin will be with you shortly.")

    def handle_message(self):
        print("\nPlease leave your message for Dr. Adrin.")
        message_response = input("Your message: ").lower()
        print(f"\nThanks for the message. We will forward it to Dr. Adrin.")

    def query_emergency_db(self, emergency):
        print("\nChecking what to do immediately for the emergency...")
        time.sleep(15)
        self.cursor.execute(
            "SELECT instructions FROM emergencies WHERE emergency_type = ?",
            (emergency,),
        )

        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return "I don't have instructions for this emergency. please wait till Dr. Adrin reaches you or give me more clarity."

    def calculate_eta(self):
        # Generate random latitude and longitude within 10km radius
        def generate_random_coordinates(center_lat, center_lon, radius_km):
            radius_in_degrees = radius_km / 111
            u = random.random()
            v = random.random()
            w = radius_in_degrees * math.sqrt(u)
            t = 2 * math.pi * v
            x = w * math.cos(t)
            y = w * math.sin(t)
            new_lat = center_lat + x
            new_lon = center_lon + y
            return new_lat, new_lon

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = (
                math.sin(dlat / 2) ** 2
                + math.cos(math.radians(lat1))
                * math.cos(math.radians(lat2))
                * math.sin(dlon / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c
            return distance

        center_lat, center_lon = 12.9716, 77.5946

        # Generate random coordinates for doctor and patient
        doctor_lat, doctor_lon = generate_random_coordinates(center_lat, center_lon, 10)
        patient_lat, patient_lon = generate_random_coordinates(
            center_lat, center_lon, 10
        )

        # Calculate distance between doctor and patient
        distance_km = haversine(doctor_lat, doctor_lon, patient_lat, patient_lon)

        average_speed_kmph = 40

        eta = (distance_km / average_speed_kmph) * 60

        return round(eta)

    def schedule_followUp(self, delay=300):
        threading.Timer(delay, self.followUp_message).start()

    def followUp_message(self):
        print(
            "\nThis is a follow-up message. How are you feeling now?\nHas the situation improved or do you need further assistance?"
        )

    def close(self):
        self.db_connection.close()


def run_receptionist():
    try:
        receptionist = AIReception()
        receptionist.start_conversation()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        receptionist.close()


if __name__ == "__main__":
    conversation_thread = threading.Thread(target=run_receptionist)
    conversation_thread.start()
    conversation_thread.join()
