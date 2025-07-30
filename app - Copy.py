from flask import Flask, render_template, request, redirect, url_for, flash
import threading
import pywhatkit as kit
import pygame
import time
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

user_passcode = None  
MASTER_KEY = "9999"  
TIMEOUT = 10
emergency_active = False
alert_sent = False
timer = None
repeating_alert_timer = None  
message_loop_active = False  

PHONE_NUMBERS = ["+918431011609"]

USER_LOCATIONS = [
    (12.82949, 77.58576),
    (12.82949, 77.58941),
    (12.82868, 77.58941),
    (12.82868, 77.58756)
]

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/activate', methods=['POST'])
def activate():
    global emergency_active, alert_sent
    emergency_active = True
    alert_sent = False
    return redirect(url_for('set_passcode'))

@app.route('/set_passcode', methods=['GET', 'POST'])
def set_passcode():
    global user_passcode

    if request.method == 'POST' and 'new_passcode' in request.form:
        user_passcode = request.form['new_passcode']
        return redirect(url_for('reenter_passcode'))  

    return render_template('set_passcode.html')

@app.route('/reenter_passcode')
def reenter_passcode():
    global timer, alert_sent, message_loop_active
    if timer is None and not alert_sent:
        timer = threading.Timer(TIMEOUT, timeout_handler)
        timer.start()
    message_loop_active = True  
    return render_template('index3.html')

@app.route('/verify_reenter_passcode', methods=['POST'])
def verify_reenter_passcode():
    global emergency_active, timer, alert_sent, repeating_alert_timer, message_loop_active
    passcode = request.form['passcode']

    if passcode == user_passcode:
        emergency_active = False
        message_loop_active = False  
        
        if timer:
            timer.cancel()
            timer = None
        if repeating_alert_timer:
            repeating_alert_timer.cancel()
            repeating_alert_timer = None
        
        return redirect(url_for('index'))  
    else:
        if not alert_sent:
            alert_sent = True
            if timer:
                timer.cancel()
                timer = None
            play_emergency_sound()  
            return redirect(url_for('send_alert'))
        else:
            return render_template('index3.html')

@app.route('/verify_master_key', methods=['POST'])
def verify_master_key():
    global emergency_active, alert_sent, message_loop_active, timer, repeating_alert_timer

    entered_key = request.form['master_key']
    if entered_key == MASTER_KEY:
        emergency_active = False
        alert_sent = False
        message_loop_active = False
        
        if timer:
            timer.cancel()
            timer = None
        if repeating_alert_timer:
            repeating_alert_timer.cancel()
            repeating_alert_timer = None
        
        return redirect(url_for('set_passcode'))
    else:
        flash("Incorrect Master Key! Try again.", "error")
        return redirect(url_for('reenter_passcode'))

def play_emergency_sound():
    pygame.mixer.init()
    pygame.mixer.music.load(r'C:\Users\Abhinav S  Bhat\OneDrive\Desktop\pp\activate message.mp3')
    pygame.mixer.music.play()

def play_beep_sound():
    pygame.mixer.init()
    pygame.mixer.music.load(r'C:\Users\Abhinav S  Bhat\OneDrive\Desktop\pp\beep.mp3')
    pygame.mixer.music.play()

def timeout_handler():
    global alert_sent
    if not alert_sent:
        play_emergency_sound()  
        send_alert()

@app.route('/send_alert')
def send_alert():
    global alert_sent, repeating_alert_timer, message_loop_active
    alert_sent = True

    selected_location = random.choice(USER_LOCATIONS)
    location_link = f"https://www.google.com/maps/search/?api=1&query={selected_location[0]},{selected_location[1]}"
    
    message = (
        f"⚠ Emergency Alert\n\n"
        f"I am currently in a dangerous situation and urgently need assistance.\n\n"
        f"📍 Location: {location_link}\n\n"
        f"Please respond immediately or alert the authorities.\n"
        f"Thank you for your support.\n\n"
    )

    try:
        send_whatsapp_message_sequence(PHONE_NUMBERS, message)

        threading.Timer(40, play_beep_sound).start()
        if emergency_active and message_loop_active:
            repeating_alert_timer = threading.Timer(10, send_alert)
            repeating_alert_timer.start()

        return render_template('alert.html')
    except Exception as e:
        return f"Error sending WhatsApp message: {str(e)}"

def send_whatsapp_message_sequence(phone_numbers, message, retries=3):
    initial_wait_time = 15  
    time.sleep(initial_wait_time) 
    
    for number in phone_numbers:
        for attempt in range(retries):
            try:
                kit.sendwhatmsg_instantly(number, message, wait_time=10)
                time.sleep(10)  
                break  
            except Exception:
                time.sleep(5) 

if __name__ == "__main__":
    app.run(debug=True)