from json import dump, dumps, load, loads
from os import getenv, makedirs, path
from socket import gethostbyname, gethostname
from sys import exit as sys_exit
from threading import Thread
from time import time as get_current_timestamp

from cryptography.fernet import Fernet
from flask import Flask, Response, render_template
from flask_cors import CORS
from matplotlib.pyplot import axis, close, imshow, show, title
from pyautogui import press
from qrcode import QRCode, constants
from selenium import webdriver
from selenium.webdriver.common.by import By

FLASK_APP = Flask(__name__)
CORS(FLASK_APP)

AUTODARTS_SITE = "https://play.autodarts.io/"
AUTODARTS_LOGIN_SITE = "https://login.autodarts.io/"

DATA_PATH = f"{getenv("TEMP")}/autoautodarts"
DATA_FILE = "data.txt"
GAMES_FILE = "games.json"

KEY_PATH = f"{getenv("APPDATA")}/D4RT2"
KEY_FILE = "key.txt"

# Referenzed games with their button because the url containts "-"'s
GAMES = {
    "x01": "/html/body/div[1]/div/div[2]/div/div/div[2]/div[1]/div/div/a",
    "cricket": "/html/body/div[1]/div/div[2]/div/div/div[2]/div[1]/div/a",
    "bermuda": "/html/body/div[1]/div/div[2]/div/div/div[2]/div[2]/div/a[1]",
    "shanghai": "/html/body/div[1]/div/div[2]/div/div/div[2]/div[2]/div/a[2]",
    "gotcha": "/html/body/div[1]/div/div[2]/div/div/div[2]/div[2]/div/a[3]",
    "around": "/html/body/div[1]/div/div[2]/div/div/div[2]/div[3]/div/a[1]",
    "round": "/html/body/div[1]/div/div[2]/div/div/div[2]/div[3]/div/a[2]",
    "random": "/html/body/div[1]/div/div[2]/div/div/div[2]/div[3]/div/a[3]",
    "count": "/html/body/div[1]/div/div[2]/div/div/div[2]/div[3]/div/a[4]",
    "segment": "/html/body/div[1]/div/div[2]/div/div/div[2]/div[3]/div/a[5]",
    "bobs": "/html/body/div[1]/div/div[2]/div/div/div[2]/div[3]/div/a[6]",
}

email = ""
password = ""
key = ""


def get_html_element(
    driver, reference, timeout=2, by=By.XPATH, multiple_elements=False
):
    start_time = get_current_timestamp()
    while True:
        try:
            if multiple_elements:
                return driver.find_elements(by, reference)
            else:
                return driver.find_element(by, reference)
        except:
            if get_current_timestamp() - start_time >= timeout:
                return 1


def login(driver) -> int:
    """_summary_

    Returns:
        int: 0 = Success | 1 = Failed because no internet or outdated version | 2 = Failed bacause data was wrong
    """
    login_status = 0

    driver.get(AUTODARTS_SITE)

    email_input = get_html_element(
        driver, "/html/body/div[1]/div[2]/div/div/div[1]/div/form/div[1]/input", 5
    )
    password_input = get_html_element(
        driver, "/html/body/div[1]/div[2]/div/div/div[1]/div/form/div[2]/div/input"
    )

    email_input.send_keys(email)
    password_input.send_keys(password)

    login_button = get_html_element(
        driver, "/html/body/div[1]/div[2]/div/div/div[1]/div/form/div[4]/input[2]"
    ).click()

    if email_input == 1 or password_input == 1 or login_button == 1:
        login_status = 1
    elif get_html_element(driver, "/html/body/div[1]/div/div[2]", 3) == 1:
        login_status = 2

    return login_status


def set_login_data():
    email = input("E-Mail:")
    password = input("Password:")

    data = "{" + f'"email":"{email}","password":"{password}"' + "}"

    with open(f"{DATA_PATH}/{DATA_FILE}", "wb") as login_data:
        login_data.write(fernet.encrypt(data.encode()))

    return email, password


def manage_games(cmd):
    cmd = cmd.lower().split(" ")

    try:
        action = cmd[0]
        selected_game = cmd[1]
        game_name = cmd[2]
        settings = cmd[3:]
    except:
        # If you are removing an preset @game_name is actually @selected_game
        if not action and not selected_game:
            return

    if action == "+":
        if selected_game not in GAMES:
            return
        elif selected_game not in games:
            games[selected_game] = {}

    if action == "+":
        if game_name not in games[selected_game]:
            games[selected_game][game_name] = settings
    elif action == "-":
        for game_type in games:
            if selected_game in games[game_type]:
                del games[game_type][selected_game]
                break

    with open(f"{DATA_PATH}/{GAMES_FILE}", "w") as games_file:
        dump(games, games_file)


@FLASK_APP.route("/")
def index():
    close()
    return render_template("games.html", address=gethostbyname(gethostname()))


@FLASK_APP.route("/getgames")
def getgames():
    return dumps(games)


@FLASK_APP.route("/command/<command>")
def command(command):
    manage_games(command)
    return Response(status=200)


@FLASK_APP.route("/loadgame/<game_mode>/<game_name>")
def loadgame(game_mode, game_name):
    driver.get(AUTODARTS_SITE)

    game_button = get_html_element(driver, GAMES[game_mode])
    game_button.click()

    game_settings = get_html_element(
        driver, "/html/body/div[1]/div/div[2]/div/div/div[2]/div"
    )

    settings_container = game_settings.find_elements(By.XPATH, "./*")

    ordered_settings = []

    for base_setting in settings_container[0].find_elements(By.XPATH, "./*"):
        ordered_settings.append(base_setting)

    for setting in settings_container[1:]:
        ordered_settings.append(setting)

    game_settings = games[game_mode][game_name]

    for x in range(len(ordered_settings) - len(game_settings)):
        game_settings.append(0)

    for i in range(0, len(ordered_settings)):
        current_setting = int(game_settings[i])
        if current_setting != 0:
            ordered_settings[i].find_elements(By.XPATH, "./*")[1].find_elements(
                By.XPATH, "./*"
            )[current_setting - 1].click()

    # Create Lobby button
    get_html_element(
        driver, "/html/body/div[1]/div/div[2]/div/div/div[3]/button"
    ).click()

    return Response(status=200)


@FLASK_APP.route("/startgame/<player_count>")
def startgame(player_count):
    player_count = player_count.replace(" ", "")

    try:
        player_count = int(player_count)
    except:
        return

    if player_count == 0:
        player_count = 1

    for i in range(1, player_count):
        player_name = f"Player{i}"

        # Retriving element every time so player count is corrent in lobby
        player_name_input = get_html_element(
            driver,
            "/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/input",
        )
        add_player_button = get_html_element(
            driver,
            "/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/button[1]",
        )

        player_name_input.send_keys(player_name)
        add_player_button.click()

    # Click start button
    get_html_element(
        driver,
        "/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[3]/button[1]",
        0.4,
    ).click()

    # Switch view to be able to see the board and hits
    get_html_element(
        driver,
        "/html/body/div[1]/div/div[2]/div/div/div[1]/ul/div[3]/div[2]/button[2]",
        4,
    ).click()

    return Response(status=200)


@FLASK_APP.route("/nextgame")
def nextgame():
    get_html_element(
        driver,
        "/html/body/div[1]/div/div[2]/div/div/div[5]/div/div/div[2]/button[3]",
        0.4,
    ).click()
    return Response(status=200)


def run_flask():
    FLASK_APP.run(host="0.0.0.0", port=8080)
    sys_exit()


if __name__ == "__main__":

    makedirs(DATA_PATH, exist_ok=True)
    makedirs(KEY_PATH, exist_ok=True)

    if not path.exists(f"{KEY_PATH}/{KEY_FILE}"):
        key = Fernet.generate_key().decode()

        with open(f"{KEY_PATH}/{KEY_FILE}", "w") as key_data:
            key_data.write(key)
    else:
        with open(f"{KEY_PATH}/{KEY_FILE}", "r") as key_data:
            key = key_data.read()

    fernet = Fernet(key)

    if not path.exists(f"{DATA_PATH}/{DATA_FILE}"):
        email, password = set_login_data()
    else:
        with open(f"{DATA_PATH}/{DATA_FILE}", "rb") as login_data:
            decrypted_data = loads(fernet.decrypt(login_data.read()))

            email = decrypted_data["email"]
            password = decrypted_data["password"]

    if not path.exists(f"{DATA_PATH}/{GAMES_FILE}"):
        with open(f"{DATA_PATH}/{GAMES_FILE}", "w") as games_file:
            games_file.write("{}")

    with open(f"{DATA_PATH}/{GAMES_FILE}", "r") as games_file:
        games = load(games_file)

    driver = webdriver.Chrome()

    driver.minimize_window()

    login_status = login(driver)

    while login_status == 2:
        print("!!!Invalid login data!!!")
        email, password = set_login_data()
        login_status = login(driver)

    driver.maximize_window()

    press("f11")

    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    remote_controll = QRCode(
        version=1,
        error_correction=constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    remote_controll.add_data(f"http://{gethostbyname(gethostname())}:8080")
    remote_controll.make(fit=True)

    qrcode_image = remote_controll.make_image(fill="black", back_color="white")

    imshow(qrcode_image)
    title("Remote Controll")
    axis("off")
    show()

    while True:
        pass
