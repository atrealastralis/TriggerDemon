import sys
import json
import os
import time
import requests
import re
import base64
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QGroupBox, QFormLayout,
    QScrollArea, QLabel, QFrame, QSizePolicy, QListWidget, QListWidgetItem,
    QCheckBox, QMessageBox, QDialog, QMenu, QFileDialog
)
from PyQt6.QtGui import (
    QIcon, QColor, QTextCharFormat, QTextCursor, QClipboard,
    QPalette, QTextOption, QTextDocument, QAction, QKeySequence, QFont, QPixmap, QShortcut
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
import qtawesome as qta

servers = {}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE_PATH = os.path.join(SCRIPT_DIR, "servers.json")
ICONS_DIR = os.path.join(SCRIPT_DIR, "icons")
if not os.path.exists(ICONS_DIR):
    os.makedirs(ICONS_DIR)

COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia",
    "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium",
    "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria",
    "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad",
    "Chile", "China", "Colombia", "Comoros", "Congo (Congo-Brazzaville)", "Costa Rica", "Croatia", "Cuba", "Cyprus",
    "Czechia (Czech Republic)", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica",
    "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini",
    "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada",
    "Guatemala", "Guinea", "Guinea-Bussau", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia",
    "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati",
    "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania",
    "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania",
    "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique",
    "Myanmar (Burma)", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria",
    "North Korea", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea",
    "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis",
    "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia",
    "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia",
    "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland",
    "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago",
    "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom",
    "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
]

# Map countries to their flag-icon CSS classes (using flag-icons library)
COUNTRY_TO_FLAG_CLASS = {
    "Afghanistan": "fi-af", "Albania": "fi-al", "Algeria": "fi-dz", "Andorra": "fi-ad", "Angola": "fi-ao",
    "Antigua and Barbuda": "fi-ag", "Argentina": "fi-ar", "Armenia": "fi-am", "Australia": "fi-au", "Austria": "fi-at",
    "Azerbaijan": "fi-az", "Bahamas": "fi-bs", "Bahrain": "fi-bh", "Bangladesh": "fi-bd", "Barbados": "fi-bb",
    "Belarus": "fi-by", "Belgium": "fi-be", "Belize": "fi-bz", "Benin": "fi-bj", "Bhutan": "fi-bt",
    "Bolivia": "fi-bo", "Bosnia and Herzegovina": "fi-ba", "Botswana": "fi-bw", "Brazil": "fi-br", "Brunei": "fi-bn",
    "Bulgaria": "fi-bg", "Burkina Faso": "fi-bf", "Burundi": "fi-bi", "Cabo Verde": "fi-cv", "Cambodia": "fi-kh",
    "Cameroon": "fi-cm", "Canada": "fi-ca", "Central African Republic": "fi-cf", "Chad": "fi-td", "Chile": "fi-cl",
    "China": "fi-cn", "Colombia": "fi-co", "Comoros": "fi-km", "Congo (Congo-Brazzaville)": "fi-cg", "Costa Rica": "fi-cr",
    "Croatia": "fi-hr", "Cuba": "fi-cu", "Cyprus": "fi-cy", "Czechia (Czech Republic)": "fi-cz", "Democratic Republic of the Congo": "fi-cd",
    "Denmark": "fi-dk", "Djibouti": "fi-dj", "Dominica": "fi-dm", "Dominican Republic": "fi-do", "Ecuador": "fi-ec",
    "Egypt": "fi-eg", "El Salvador": "fi-sv", "Equatorial Guinea": "fi-gq", "Eritrea": "fi-er", "Estonia": "fi-ee",
    "Eswatini": "fi-sz", "Ethiopia": "fi-et", "Fiji": "fi-fj", "Finland": "fi-fi", "France": "fi-fr",
    "Gabon": "fi-ga", "Gambia": "fi-gm", "Georgia": "fi-ge", "Germany": "fi-de", "Ghana": "fi-gh",
    "Greece": "fi-gr", "Grenada": "fi-gd", "Guatemala": "fi-gt", "Guinea": "fi-gn", "Guinea-Bussau": "fi-gw",
    "Guyana": "fi-gy", "Haiti": "fi-ht", "Honduras": "fi-hn", "Hungary": "fi-hu", "Iceland": "fi-is",
    "India": "fi-in", "Indonesia": "fi-id", "Iran": "fi-ir", "Iraq": "fi-iq", "Ireland": "fi-ie",
    "Israel": "fi-il", "Italy": "fi-it", "Jamaica": "fi-jm", "Japan": "fi-jp", "Jordan": "fi-jo",
    "Kazakhstan": "fi-kz", "Kenya": "fi-ke", "Kiribati": "fi-ki", "Kuwait": "fi-kw", "Kyrgyzstan": "fi-kg",
    "Laos": "fi-la", "Latvia": "fi-lv", "Lebanon": "fi-lb", "Lesotho": "fi-ls", "Liberia": "fi-lr",
    "Libya": "fi-ly", "Liechtenstein": "fi-li", "Lithuania": "fi-lt", "Luxembourg": "fi-lu", "Madagascar": "fi-mg",
    "Malawi": "fi-mw", "Malaysia": "fi-my", "Maldives": "fi-mv", "Mali": "fi-ml", "Malta": "fi-mt",
    "Marshall Islands": "fi-mh", "Mauritania": "fi-mr", "Mauritius": "fi-mu", "Mexico": "fi-mx", "Micronesia": "fi-fm",
    "Moldova": "fi-md", "Monaco": "fi-mc", "Mongolia": "fi-mn", "Montenegro": "fi-me", "Morocco": "fi-ma",
    "Mozambique": "fi-mz", "Myanmar (Burma)": "fi-mm", "Namibia": "fi-na", "Nauru": "fi-nr", "Nepal": "fi-np",
    "Netherlands": "fi-nl", "New Zealand": "fi-nz", "Nicaragua": "fi-ni", "Niger": "fi-ne", "Nigeria": "fi-ng",
    "North Korea": "fi-kp", "North Macedonia": "fi-mk", "Norway": "fi-no", "Oman": "fi-om", "Pakistan": "fi-pk",
    "Palau": "fi-pw", "Palestine": "fi-ps", "Panama": "fi-pa", "Papua New Guinea": "fi-pg", "Paraguay": "fi-py",
    "Peru": "fi-pe", "Philippines": "fi-ph", "Poland": "fi-pl", "Portugal": "fi-pt", "Qatar": "fi-qa",
    "Romania": "fi-ro", "Russia": "fi-ru", "Rwanda": "fi-rw", "Saint Kitts and Nevis": "fi-kn", "Saint Lucia": "fi-lc",
    "Saint Vincent and the Grenadines": "fi-vc", "Samoa": "fi-ws", "San Marino": "fi-sm", "Sao Tome and Principe": "fi-st",
    "Saudi Arabia": "fi-sa", "Senegal": "fi-sn", "Serbia": "fi-rs", "Seychelles": "fi-sc", "Sierra Leone": "fi-sl",
    "Singapore": "fi-sg", "Slovakia": "fi-sk", "Slovenia": "fi-si", "Solomon Islands": "fi-sb", "Somalia": "fi-so",
    "South Africa": "fi-za", "South Korea": "fi-kr", "South Sudan": "fi-ss", "Spain": "fi-es", "Sri Lanka": "fi-lk",
    "Sudan": "fi-sd", "Suriname": "fi-sr", "Sweden": "fi-se", "Switzerland": "fi-ch", "Syria": "fi-sy",
    "Taiwan": "fi-tw", "Tajikistan": "fi-tj", "Tanzania": "fi-tz", "Thailand": "fi-th", "Timor-Leste": "fi-tl",
    "Togo": "fi-tg", "Tonga": "fi-to", "Trinidad and Tobago": "fi-tt", "Tunisia": "fi-tn", "Turkey": "fi-tr",
    "Turkmenistan": "fi-tm", "Tuvalu": "fi-tv", "Uganda": "fi-ug", "Ukraine": "fi-ua", "United Arab Emirates": "fi-ae",
    "United Kingdom": "fi-gb", "United States": "fi-us", "Uruguay": "fi-uy", "Uzbekistan": "fi-uz", "Vanuatu": "fi-vu",
    "Vatican City": "fi-va", "Venezuela": "fi-ve", "Vietnam": "fi-vn", "Yemen": "fi-ye", "Zambia": "fi-zm", "Zimbabwe": "fi-zw",
    "Unknown": "fi-un"
}

def load_servers():
    try:
        if os.path.exists(JSON_FILE_PATH):
            with open(JSON_FILE_PATH, "r") as f:
                data = json.load(f)
            print(f"Loaded servers: {data}")
            for server_name, server in data.items():
                if 'triggers' in server:
                    for trigger in server['triggers']:
                        if 'code' in trigger and 'trigger' not in trigger:
                            trigger['trigger'] = trigger.pop('code')
                        if 'trigger' in trigger:
                            trigger['trigger'] = str(trigger['trigger'])
                server['last_updated'] = server.get('last_updated', time.strftime("%Y-%m-%d %H:%M:%S"))
            return data
        print("No servers.json file found, starting with empty servers.")
        return {}
    except Exception as e:
        print(f"Error loading servers: {e}")
        return {}

def save_servers():
    try:
        with open(JSON_FILE_PATH, "w") as f:
            json.dump(servers, f, indent=4)
        print("Servers saved successfully.")
    except Exception as e:
        print(f"Error saving servers: {e}")
        QMessageBox.critical(None, "Error", f"Failed to save servers: {e}")

def filter_server_name(server_name):
    server_name = re.sub(r'\[\w{2}\]', '', server_name)
    server_name = re.sub(r'[\U0001F000-\U0001F9FF]', '', server_name)
    server_name = re.sub(r'→\s*discord\.gg/[^\s]*', '', server_name)
    server_name = re.sub(r'discord\.gg/[^\s]*', '', server_name)
    server_name = re.sub(r'\s*\(\w{2}\)\s*$', '', server_name)
    server_name = ' '.join(server_name.split())
    if len(server_name) > 30:
        server_name = server_name[:27] + "..."
    return server_name

def fetch_server_icon(server_id):
    url = f"https://servers.fivem.net/servers/detail/{server_id}"
    try:
        response = requests.get(url, headers={"User-Agent": "FiveMServerSearch/1.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        icon_img = soup.find("img", {"alt": "Server Icon"})
        if icon_img and icon_img.get("src"):
            icon_url = icon_img["src"]
            if not icon_url.startswith("http"):
                icon_url = f"https://servers.fivem.net{icon_url}"
            icon_data = requests.get(icon_url).content
            icon_path = os.path.join(ICONS_DIR, f"{server_id}.png")
            with open(icon_path, "wb") as f:
                f.write(icon_data)
            return icon_path
    except Exception as e:
        print(f"Failed to scrape icon for {server_id}: {e}")
    return None

def fetch_server_info(join_url):
    try:
        if join_url.startswith("fivem://connect/"):
            server_id = join_url.replace("fivem://connect/", "").split(":")[0]
        elif "cfx.re/join" in join_url:
            server_id = join_url.split("/")[-1]
        else:
            print(f"Invalid join URL format: {join_url}")
            return "Unknown Server", "0 / 0", None, "Unknown", []

        print(f"Extracted server ID: {server_id} from join URL: {join_url}")

        api_url = f"https://servers-frontend.fivem.net/api/servers/single/{server_id}"
        headers = {"User-Agent": "FiveMServerSearch/1.0", "Accept": "application/json"}
        retries = 3
        backoff_factor = 1.5

        for attempt in range(retries):
            try:
                response = requests.get(api_url, headers=headers, timeout=10)
                response.raise_for_status()
                server_data = response.json()
                print(f"Successfully fetched data from {api_url}: {server_data}")
                break
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    print(f"Server {server_id} not found at {api_url}")
                    return "Unknown Server", "0 / 0", None, "Unknown", []
                print(f"HTTP Error fetching {api_url}: {e}")
                if attempt < retries - 1:
                    delay = backoff_factor * (2 ** attempt)
                    print(f"Retrying after {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("Max retries reached.")
                    return "Unknown Server", "0 / 0", None, "Unknown", []
            except requests.exceptions.RequestException as e:
                print(f"Request Error fetching {api_url}: {e}")
                if attempt < retries - 1:
                    delay = backoff_factor * (2 ** attempt)
                    print(f"Retrying after {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("Max retries reached.")
                    return "Unknown Server", "0 / 0", None, "Unknown", []

        raw_server_name = server_data.get("Data", {}).get("hostname", "Unknown Server")
        raw_server_name = ''.join(char for char in raw_server_name if char.isprintable() and char not in '^0123456789').strip()
        server_name = filter_server_name(raw_server_name)
        players = server_data.get("Data", {}).get("clients", 0)
        max_players = server_data.get("Data", {}).get("sv_maxclients", 0)
        player_count = f"{players} / {max_players}"
        icon_path = fetch_server_icon(server_id)
        server_vars = server_data.get("Data", {}).get("vars", {})
        tags = server_vars.get("tags", "").split(",") if server_vars.get("tags") else []

        location = "Unknown"
        region = server_vars.get("region", "").lower()
        locale = server_vars.get("locale", "").lower()
        region_to_country = {"eu": "Germany", "na": "United States", "sa": "Brazil", "as": "Singapore", "oc": "Australia"}
        locale_to_country = {"en-us": "United States", "fr-fr": "France", "de-de": "Germany", "es-es": "Spain", "pt-br": "Brazil", "zh-cn": "China"}

        if region in region_to_country:
            location = region_to_country[region]
        elif locale in locale_to_country:
            location = locale_to_country[locale]
        else:
            server_name_lower = server_name.lower()
            for country in COUNTRIES:
                if country.lower() in server_name_lower or f"[{country[:2].lower()}]" in server_name_lower:
                    location = country
                    break

        print(f"Filtered server name: {server_name}")
        print(f"Player count: {player_count}")
        print(f"Icon path: {icon_path}")
        print(f"Extracted location: {location}")
        print(f"Tags: {tags}")
        return server_name, player_count, icon_path, location, tags

    except Exception as e:
        print(f"Error fetching server info: {e}")
        return "Unknown Server", "0 / 0", None, "Unknown", []

def load_stylesheet(dark_mode=True):
    if dark_mode:
        background_color = "#121212"
        secondary_background = "#1E1E2F"
        text_color = "#E0E0E0"
        border_color = "#2A2A3C"
        button_color = "#6A1B9A"
        button_hover_color = "#4A148C"
        cancel_button_color = "#D32F2F"
        highlight_color = "#4527A0"
    else:
        background_color = "#F5F5F5"  # Softer white for better readability
        secondary_background = "#E8ECEF"  # Light gray for secondary elements
        text_color = "#212121"  # Darker text for better contrast
        border_color = "#B0BEC5"  # Softer border color
        button_color = "#0288D1"  # A pleasant blue for buttons
        button_hover_color = "#0277BD"  # Slightly darker blue for hover
        cancel_button_color = "#D32F2F"
        highlight_color = "#1976D2"  # A modern blue for highlights

    # Include flag-icons CSS (assumes flag-icons.min.css is in the project directory)
    flag_icon_css = """
        @import url('flag-icons.min.css');
        .fi {
            width: 24px;
            height: 24px;
            background-size: cover;
            display: inline-block;
            vertical-align: middle;
            margin-right: 5px;
        }
    """

    return f"""
        {flag_icon_css}
        QWidget {{
            background-color: {background_color};
            color: {text_color};
            font-size: 14px;
            font-family: 'Segoe UI';
        }}
        QMainWindow, QDialog#addEditWindow {{
            background-color: {background_color};
        }}
        QFrame#sidebar {{
            background-color: {secondary_background};
            border-right: 1px solid {border_color};
        }}
        QListWidget#serverList {{
            background-color: {secondary_background};
            border: 1px solid {border_color};
            border-radius: 5px;
            padding: 8px;
            color: {text_color};
        }}
        QListWidget#serverList::item:selected {{
            background-color: {highlight_color};
            color: {text_color};
        }}
        QScrollArea#resultScroll {{
            background-color: {secondary_background};
            border: 1px solid {border_color};
            border-radius: 5px;
        }}
        QPushButton {{
            background-color: {button_color};
            color: {text_color};
            border: none;
            padding: 8px 12px;
            border-radius: 5px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {button_hover_color};
        }}
        QPushButton#cancelBtn {{
            background-color: {cancel_button_color};
        }}
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {secondary_background};
            color: {text_color};
            border: 1px solid {border_color};
            padding: 6px;
            border-radius: 5px;
        }}
        QGroupBox {{
            border: 1px solid {border_color};
            border-radius: 5px;
            margin-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: {text_color};
        }}
        QLabel {{
            padding: 2px;
        }}
    """

class ServerStatusThread(QThread):
    status_updated = pyqtSignal(str, str, list)

    def __init__(self, server_name, join_url):
        super().__init__()
        self.server_name = server_name
        self.join_url = join_url

    def run(self):
        _, player_count, _, _, tags = fetch_server_info(self.join_url)
        self.status_updated.emit(self.server_name, player_count, tags)

class TriggerBlock(QWidget):
    def __init__(self, trigger_text, description, index):
        super().__init__()
        self.setObjectName("triggerBlockContainer")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        toggle_btn = QPushButton(f"Trigger {index}")
        toggle_btn.setStyleSheet("font-weight: bold;")
        toggle_btn.clicked.connect(self.toggle_content)
        header_layout.addWidget(toggle_btn)

        copy_btn = QPushButton("Copy")
        copy_btn.setObjectName("copyBtn")
        copy_btn.setIcon(qta.icon('mdi.content-copy', color="#E0E0E0"))
        copy_btn.setToolTip("Copy trigger to clipboard")
        copy_btn.clicked.connect(lambda: self.copy_trigger(trigger_text))
        header_layout.addWidget(copy_btn)

        layout.addLayout(header_layout)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.trigger_text = QTextEdit(trigger_text)
        self.trigger_text.setReadOnly(True)
        self.trigger_text.setFixedHeight(60)
        self.content_layout.addWidget(self.trigger_text)

        desc_label = QLabel("Description:")
        self.content_layout.addWidget(desc_label)
        self.desc_text = QTextEdit(description)
        self.desc_text.setReadOnly(True)
        self.desc_text.setFixedHeight(60)
        self.content_layout.addWidget(self.desc_text)

        layout.addWidget(self.content_widget)
        self.content_widget.setVisible(False)

    def toggle_content(self):
        self.content_widget.setVisible(not self.content_widget.isVisible())

    def copy_trigger(self, trigger_text):
        clipboard = QApplication.clipboard()
        clipboard.setText(trigger_text)
        QMessageBox.information(self, "Copied", "Trigger copied to clipboard!")

class AddEditWindow(QDialog):
    def __init__(self, parent=None, server_name=None):
        super().__init__(parent)
        self.setObjectName("addEditWindow")
        self.setWindowTitle("Add/Edit Server")
        self.setFixedSize(500, 600)

        self.server_name = server_name
        self.parent = parent

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setSpacing(10)

        self.location_input = QComboBox()
        available_countries = self.get_available_countries()
        self.location_input.addItems(available_countries)
        form_layout.addRow("Location:", self.location_input)

        self.join_server_input = QLineEdit()
        form_layout.addRow("Join Server:", self.join_server_input)

        self.anticheat_input = QComboBox()
        self.anticheat_input.addItems(["Unknown", "ReaperV4", "FiveGuard", "ElectronAC", "PegasusAC", "FiniAC", "PhoenixAC", "WaveShield"])
        form_layout.addRow("AntiCheat:", self.anticheat_input)

        self.whitelist_input = QCheckBox("Whitelist")
        form_layout.addRow("Whitelist:", self.whitelist_input)

        self.premium_input = QCheckBox("Premium Menu Needed")
        form_layout.addRow("Premium:", self.premium_input)

        self.favorite_input = QCheckBox("Favorite")
        form_layout.addRow("Favorite:", self.favorite_input)

        self.notes_input = QTextEdit()
        self.notes_input.setFixedHeight(80)
        form_layout.addRow("Notes:", self.notes_input)

        layout.addLayout(form_layout)

        triggers_label = QLabel("Triggers:")
        layout.addWidget(triggers_label)

        self.triggers_layout = QVBoxLayout()
        self.triggers_widget = QWidget()
        self.triggers_widget.setLayout(self.triggers_layout)
        self.triggers_scroll = QScrollArea()
        self.triggers_scroll.setWidget(self.triggers_widget)
        self.triggers_scroll.setWidgetResizable(True)
        self.triggers_scroll.setFixedHeight(150)
        layout.addWidget(self.triggers_scroll)

        add_trigger_btn = QPushButton("Add Trigger")
        add_trigger_btn.setObjectName("addTriggerBtn")
        add_trigger_btn.setIcon(qta.icon('mdi.plus', color="#E0E0E0"))
        add_trigger_btn.setToolTip("Add a new trigger")
        add_trigger_btn.clicked.connect(self.add_trigger)
        layout.addWidget(add_trigger_btn)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("saveBtn")
        save_btn.setIcon(qta.icon('mdi.content-save', color="#E0E0E0"))
        save_btn.setToolTip("Save server details")
        save_btn.clicked.connect(self.save_server)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setIcon(qta.icon('mdi.close', color="#E0E0E0"))
        cancel_btn.setToolTip("Cancel and close")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        if server_name and server_name in servers:
            server = servers[server_name]
            self.location_input.setCurrentText(server.get("location", "United States"))
            self.join_server_input.setText(server.get("join_server", ""))
            self.anticheat_input.setCurrentText(server.get("anticheat", "Unknown"))
            self.whitelist_input.setChecked(server.get("whitelist", False))
            self.premium_input.setChecked(server.get("premium", False))
            self.favorite_input.setChecked(server.get("favorite", False))
            self.notes_input.setText(server.get("notes", ""))
            for trigger in server.get("triggers", []):
                self.add_trigger(trigger.get("trigger", ""), trigger.get("description", ""))

    def get_available_countries(self):
        available_countries = set()
        for server in servers.values():
            location = server.get("location", "Unknown")
            if location and location != "Unknown":
                available_countries.add(location)
        return sorted(available_countries) or ["United States"]

    def add_trigger(self, trigger_text="", description=""):
        trigger_text = str(trigger_text)
        description = str(description)

        trigger_widget = QWidget()
        trigger_layout = QVBoxLayout(trigger_widget)

        trigger_input = QTextEdit(trigger_text)
        trigger_input.setFixedHeight(50)
        trigger_layout.addWidget(trigger_input)

        desc_input = QTextEdit(description)
        desc_input.setFixedHeight(50)
        desc_input.setPlaceholderText("Description")
        trigger_layout.addWidget(desc_input)

        remove_btn = QPushButton("Remove")
        remove_btn.setObjectName("removeTriggerBtn")
        remove_btn.setIcon(qta.icon('mdi.delete', color="#E0E0E0"))
        remove_btn.setToolTip("Remove this trigger")
        remove_btn.clicked.connect(lambda: trigger_widget.setParent(None))
        trigger_layout.addWidget(remove_btn)

        self.triggers_layout.addWidget(trigger_widget)

    def save_server(self):
        join_url = self.join_server_input.text().strip()
        if not join_url:
            QMessageBox.warning(self, "Error", "Please enter a join server URL.")
            return

        server_name, player_count, icon_path, location, tags = fetch_server_info(join_url)
        if server_name == "Unknown Server":
            QMessageBox.critical(self, "Error", f"Failed to fetch server info for URL: {join_url}.")
            return

        if self.server_name and self.server_name in servers and self.server_name != server_name:
            del servers[self.server_name]

        triggers = []
        for i in range(self.triggers_layout.count()):
            widget = self.triggers_layout.itemAt(i).widget()
            if widget:
                trigger_input = widget.layout().itemAt(0).widget()
                desc_input = widget.layout().itemAt(1).widget()
                trigger_text = trigger_input.toPlainText().strip()
                description = desc_input.toPlainText().strip()
                if trigger_text:
                    triggers.append({"trigger": trigger_text, "description": description})

        new_server = {
            "location": self.location_input.currentText(),
            "join_server": join_url,
            "icon_path": icon_path,
            "anticheat": self.anticheat_input.currentText(),
            "whitelist": self.whitelist_input.isChecked(),
            "premium": self.premium_input.isChecked(),
            "triggers": triggers,
            "player_count": player_count,
            "notes": self.notes_input.toPlainText().strip(),
            "favorite": self.favorite_input.isChecked(),
            "tags": tags,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        servers[server_name] = new_server
        save_servers()
        self.parent.update_server_list()
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trigger Deamon")
        self.dark_mode = True

        screen = QApplication.primaryScreen().size()
        window_width = int(screen.width() * 0.6)
        window_height = int(screen.height() * 0.5)
        self.setGeometry(100, 100, window_width, window_height)

        global servers
        servers = load_servers()

        self.setStyleSheet(load_stylesheet(self.dark_mode))

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)

        self.server_list_btn = self.create_sidebar_button("Server List", 'mdi.view-dashboard')
        self.server_list_btn.setToolTip("View all servers")
        self.server_list_btn.clicked.connect(self.show_all_servers)
        sidebar_layout.addWidget(self.server_list_btn)

        self.favorites_btn = self.create_sidebar_button("Favorites", 'mdi.star')
        self.favorites_btn.setToolTip("View favorite servers")
        self.favorites_btn.clicked.connect(self.show_favorites)
        sidebar_layout.addWidget(self.favorites_btn)

        self.toggle_theme_btn = self.create_sidebar_button("Toggle Theme", 'mdi.theme-light-dark')
        self.toggle_theme_btn.setToolTip("Switch between light and dark theme")
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.toggle_theme_btn)

        sidebar_layout.addStretch()

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        top_layout = QHBoxLayout()
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Player Count", "Location", "Favorite"])
        self.sort_combo.setToolTip("Sort servers by selected criteria")
        self.sort_combo.currentTextChanged.connect(self.apply_filters)
        top_layout.addWidget(self.sort_combo)

        export_btn = QPushButton("Export Servers")
        export_btn.setToolTip("Export servers to a JSON file")
        export_btn.clicked.connect(self.export_servers)
        top_layout.addWidget(export_btn)

        import_btn = QPushButton("Import Servers")
        import_btn.setToolTip("Import servers from a JSON file")
        import_btn.clicked.connect(self.import_servers)
        top_layout.addWidget(import_btn)

        self.auto_refresh_checkbox = QCheckBox("Auto-Refresh")
        self.auto_refresh_checkbox.setChecked(True)
        self.auto_refresh_checkbox.setToolTip("Enable/disable auto-refresh of server statuses")
        self.auto_refresh_checkbox.stateChanged.connect(self.toggle_auto_refresh)
        top_layout.addWidget(self.auto_refresh_checkbox)

        content_layout.addLayout(top_layout)

        search_filter_layout = QVBoxLayout()
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search server...")
        self.search_bar.setToolTip("Search for a server by name")
        self.search_bar.textChanged.connect(self.apply_filters)
        self.toggle_filter_btn = QPushButton()
        self.toggle_filter_btn.setIcon(qta.icon('mdi.filter', color="#E0E0E0"))
        self.toggle_filter_btn.setFixedSize(40, 40)
        self.toggle_filter_btn.setToolTip("Show/hide filters")
        self.toggle_filter_btn.clicked.connect(self.toggle_filters)
        search_btn = QPushButton()
        search_btn.setIcon(qta.icon('mdi.magnify', color="#E0E0E0"))
        search_btn.setFixedSize(40, 40)
        search_btn.setToolTip("Search (Ctrl+F)")
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.toggle_filter_btn)
        search_layout.addWidget(search_btn)
        search_filter_layout.addLayout(search_layout)

        self.filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(5)
        filter_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        location_label = QLabel("Location:")
        self.location_filter = QComboBox()
        self.location_filter.addItem("All")
        available_countries = self.get_available_countries()
        self.location_filter.addItems(available_countries)
        self.location_filter.currentTextChanged.connect(self.apply_filters)
        self.location_filter.setFixedWidth(150)
        self.location_filter.setToolTip("Filter by server location")
        filter_layout.addWidget(location_label)
        filter_layout.addWidget(self.location_filter)

        anticheat_label = QLabel("AntiCheat:")
        self.anticheat_filter = QComboBox()
        self.anticheat_filter.addItems(["All", "Unknown", "ReaperV4", "FiveGuard", "ElectronAC", "PegasusAC", "FiniAC", "PhoenixAC", "WaveShield"])
        self.anticheat_filter.currentTextChanged.connect(self.apply_filters)
        self.anticheat_filter.setFixedWidth(150)
        self.anticheat_filter.setToolTip("Filter by anti-cheat system")
        filter_layout.addWidget(anticheat_label)
        filter_layout.addWidget(self.anticheat_filter)

        whitelist_label = QLabel("Whitelist:")
        self.whitelist_filter = QComboBox()
        self.whitelist_filter.addItems(["All", "Yes", "No"])
        self.whitelist_filter.currentTextChanged.connect(self.apply_filters)
        self.whitelist_filter.setFixedWidth(150)
        self.whitelist_filter.setToolTip("Filter by whitelist status")
        filter_layout.addWidget(whitelist_label)
        filter_layout.addWidget(self.whitelist_filter)

        tags_label = QLabel("Tags:")
        self.tags_filter = QComboBox()
        self.tags_filter.addItem("All")
        all_tags = set()
        for server in servers.values():
            all_tags.update(server.get("tags", []))
        self.tags_filter.addItems(sorted(all_tags))
        self.tags_filter.currentTextChanged.connect(self.apply_filters)
        self.tags_filter.setFixedWidth(150)
        self.tags_filter.setToolTip("Filter by server tags")
        filter_layout.addWidget(tags_label)
        filter_layout.addWidget(self.tags_filter)

        self.favorite_filter = QCheckBox("Favorites Only")
        self.favorite_filter.stateChanged.connect(self.apply_filters)
        self.favorite_filter.setToolTip("Show only favorite servers")
        filter_layout.addWidget(self.favorite_filter)

        clear_filter_btn = QPushButton("Clear Filters")
        clear_filter_btn.setIcon(qta.icon('mdi.filter-remove', color="#E0E0E0"))
        clear_filter_btn.setToolTip("Reset all filters")
        clear_filter_btn.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_filter_btn)

        self.filter_group.setLayout(filter_layout)
        self.filter_group.setFixedHeight(60)
        search_filter_layout.addWidget(self.filter_group)
        self.filter_group.setVisible(False)

        content_layout.addLayout(search_filter_layout)

        main_content = QWidget()
        main_content_layout = QHBoxLayout(main_content)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        add_server_layout = QHBoxLayout()
        self.server_code_input = QLineEdit()
        self.server_code_input.setPlaceholderText("Enter server code (e.g., r973ap)")
        self.server_code_input.setToolTip("Enter a server code to add a new server")
        add_server_btn = QPushButton("Add Server")
        add_server_btn.setIcon(qta.icon('mdi.plus', color="#E0E0E0"))
        add_server_btn.setToolTip("Add a new server")
        add_server_btn.clicked.connect(self.add_server)
        add_server_layout.addWidget(self.server_code_input)
        add_server_layout.addWidget(add_server_btn)
        left_layout.addLayout(add_server_layout)

        refresh_layout = QHBoxLayout()
        refresh_status_btn = QPushButton("Refresh Status")
        refresh_status_btn.setIcon(qta.icon('mdi.refresh', color="#E0E0E0"))
        refresh_status_btn.setToolTip("Manually refresh server statuses")
        refresh_status_btn.clicked.connect(self.refresh_all_statuses)
        refresh_layout.addWidget(refresh_status_btn)

        refresh_icons_btn = QPushButton("Refresh Icons")
        refresh_icons_btn.setIcon(qta.icon('mdi.sync', color="#E0E0E0"))
        refresh_icons_btn.setToolTip("Refresh server icons")
        refresh_icons_btn.clicked.connect(self.refresh_all_icons)
        refresh_layout.addWidget(refresh_icons_btn)

        left_layout.addLayout(refresh_layout)

        self.server_list = QListWidget()
        self.server_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.server_list.setMinimumWidth(300)
        self.server_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.server_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.server_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.server_list.customContextMenuRequested.connect(self.show_server_context_menu)
        left_layout.addWidget(self.server_list)

        btn_layout = QHBoxLayout()
        self.add_edit_btn = QPushButton("Add/Edit Server")
        self.add_edit_btn.setIcon(qta.icon('mdi.pencil', color="#E0E0E0"))
        self.add_edit_btn.setToolTip("Add or edit a server")
        self.add_edit_btn.clicked.connect(self.open_add_edit_window)
        btn_layout.addWidget(self.add_edit_btn)

        self.delete_btn = QPushButton("Delete Server")
        self.delete_btn.setIcon(qta.icon('mdi.delete', color="#E0E0E0"))
        self.delete_btn.setToolTip("Delete the selected server")
        self.delete_btn.clicked.connect(self.delete_server)
        btn_layout.addWidget(self.delete_btn)

        left_layout.addLayout(btn_layout)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.result_scroll = QScrollArea()
        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout(self.result_widget)
        self.result_layout.setSpacing(10)
        self.result_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.result_scroll.setWidget(self.result_widget)
        self.result_scroll.setWidgetResizable(True)
        self.result_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.result_scroll.setMinimumWidth(300)
        right_layout.addWidget(self.result_scroll)

        main_content_layout.addWidget(left_panel)
        main_content_layout.addWidget(right_panel)

        content_layout.addWidget(main_content)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

        self.setAutoFillBackground(True)
        main_widget.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#121212" if self.dark_mode else "#F5F5F5"))
        self.setPalette(palette)

        self.server_status_labels = {}
        self.status_threads = []
        self.server_icons = {}
        self.placeholder_icon = qta.icon('mdi.server', color="#E0E0E0").pixmap(24, 24)

        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.search_bar.setFocus)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_all_statuses)
        self.timer.start(300000)  # 5 minutes

        self.last_selected_server = None
        self.update_server_list()
        self.refresh_all_statuses()
        self.show_default_message()

    def get_available_countries(self):
        available_countries = set()
        for server in servers.values():
            location = server.get("location", "Unknown")
            if location and location != "Unknown":
                available_countries.add(location)
        return sorted(available_countries) or ["United States"]

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.setStyleSheet(load_stylesheet(self.dark_mode))
        self.toggle_theme_btn.setIcon(qta.icon('mdi.theme-light-dark', color="#E0E0E0" if self.dark_mode else "#212121"))
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#121212" if self.dark_mode else "#F5F5F5"))
        self.setPalette(palette)

    def export_servers(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Servers", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, "w") as f:
                    json.dump(servers, f, indent=4)
                QMessageBox.information(self, "Success", "Servers exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export servers: {e}")

    def import_servers(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Servers", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, "r") as f:
                    imported = json.load(f)
                servers.update(imported)
                save_servers()
                self.update_server_list()
                self.update_location_filter()
                self.update_tags_filter()
                QMessageBox.information(self, "Success", "Servers imported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import servers: {e}")

    def toggle_auto_refresh(self):
        if self.auto_refresh_checkbox.isChecked():
            self.timer.start(300000)
        else:
            self.timer.stop()

    def show_default_message(self):
        self.clear_result_layout()
        default_label = QLabel("Select a server to view details.")
        default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_layout.addWidget(default_label)
        self.result_widget.adjustSize()

    def add_server(self):
        server_code = self.server_code_input.text().strip()
        if not server_code:
            QMessageBox.warning(self, "Error", "Please enter a server code.")
            return

        join_url = f"https://cfx.re/join/{server_code}"
        print(f"Attempting to add server with join URL: {join_url}")
        server_name, player_count, icon_path, location, tags = fetch_server_info(join_url)
        print(f"Fetch result - Server name: {server_name}, Player count: {player_count}")

        if server_name == "Unknown Server":
            QMessageBox.critical(self, "Error", f"Failed to fetch server info for code: {server_code}.")
            return

        new_server = {
            "location": location if location != "Unknown" else "United States",
            "join_server": join_url,
            "icon_path": icon_path,
            "anticheat": "Unknown",
            "whitelist": False,
            "premium": False,
            "triggers": [],
            "player_count": player_count,
            "notes": "",
            "favorite": False,
            "tags": tags,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        servers[server_name] = new_server
        print(f"Added server to dictionary: {servers}")
        save_servers()
        self.update_server_list()
        self.update_location_filter()
        self.update_tags_filter()
        self.server_code_input.clear()

    def show_server_context_menu(self, position):
        selected_items = self.server_list.selectedItems()
        if not selected_items:
            return
        display_name = selected_items[0].text()
        server_name = display_name.split(" ", 1)[1] if " " in display_name else display_name
        server = servers.get(server_name)
        if not server:
            return

        menu = QMenu(self)
        copy_action = QAction("Copy Server Details", self)
        copy_action.triggered.connect(lambda: self.copy_server_details(server))
        menu.addAction(copy_action)

        edit_action = QAction("Edit Server", self)
        edit_action.triggered.connect(self.open_add_edit_window)
        menu.addAction(edit_action)

        delete_action = QAction("Delete Server", self)
        delete_action.triggered.connect(self.delete_server)
        menu.addAction(delete_action)

        toggle_favorite_action = QAction("Toggle Favorite", self)
        toggle_favorite_action.triggered.connect(lambda: self.toggle_favorite(server_name))
        menu.addAction(toggle_favorite_action)

        connect_action = QAction("Connect", self)
        connect_action.triggered.connect(lambda: self.connect_to_server(server))
        menu.addAction(connect_action)

        menu.exec(self.server_list.mapToGlobal(position))

    def toggle_favorite(self, server_name):
        if server_name in servers:
            servers[server_name]["favorite"] = not servers[server_name].get("favorite", False)
            save_servers()
            self.update_server_list()
            if self.last_selected_server == server_name:
                self.show_server_details(server_name)

    def connect_to_server(self, server):
        server_id = self.extract_server_id(server.get("join_server", ""))
        if server_id:
            os.system(f"start fivem://connect/{server_id}")

    def copy_server_details(self, server):
        details = (
            f"Server Name: {server.get('name', server.get('server_name', 'N/A'))}\n"
            f"Location: {server.get('location', 'N/A')}\n"
            f"Join Server: {server.get('join_server', 'N/A')}\n"
            f"AntiCheat: {server.get('anticheat', 'N/A')}\n"
            f"Tags: {', '.join(server.get('tags', []))}\n"
            f"Whitelist: {'Yes' if server.get('whitelist') else 'No'}\n"
            f"Premium: {'Yes' if server.get('premium') else 'No'}\n"
            f"Notes: {server.get('notes', 'None')}\n"
            f"Favorite: {'Yes' if server.get('favorite') else 'No'}\n"
            f"Last Updated: {server.get('last_updated', 'N/A')}"
        )
        clipboard = QApplication.clipboard()
        clipboard.setText(details)
        QMessageBox.information(self, "Copied", "Server details copied to clipboard!")

    def toggle_filters(self):
        self.filter_group.setVisible(not self.filter_group.isVisible())
        icon_name = 'mdi.filter-off' if self.filter_group.isVisible() else 'mdi.filter'
        self.toggle_filter_btn.setIcon(qta.icon(icon_name, color="#E0E0E0" if self.dark_mode else "#212121"))

    def create_sidebar_button(self, text, icon_name):
        btn = QPushButton(text)
        btn.setIcon(qta.icon(icon_name, color="#E0E0E0" if self.dark_mode else "#212121"))
        return btn

    def refresh_all_statuses(self):
        self.status_threads.clear()
        for server_name, server in servers.items():
            join_url = server.get("join_server", "")
            if join_url:
                self.check_server_status(server_name, join_url)

    def refresh_all_icons(self):
        for server_name, server in servers.items():
            join_url = server.get("join_server", "")
            if join_url:
                server_id = self.extract_server_id(join_url)
                if server_id:
                    _, _, icon_path, _, _ = fetch_server_info(join_url)
                    if icon_path:
                        self.server_icons[server_id] = icon_path
                        server["icon_path"] = icon_path
                        save_servers()
        self.apply_filters()

    def extract_server_id(self, join_url):
        if "fivem://connect/" in join_url:
            return join_url.split("fivem://connect/")[-1].split(":")[0]
        elif "cfx.re/join" in join_url:
            return join_url.split("/")[-1]
        return None

    def check_server_status(self, server_name, join_url):
        thread = ServerStatusThread(server_name, join_url)
        thread.status_updated.connect(self.update_server_status)
        thread.finished.connect(lambda: self.status_threads.remove(thread) if thread in self.status_threads else None)
        thread.start()
        self.status_threads.append(thread)

    def update_server_status(self, server_name, status, tags):
        if server_name in servers:
            servers[server_name]["player_count"] = status
            servers[server_name]["tags"] = tags
            servers[server_name]["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
            save_servers()
            self.update_tags_filter()
            self.apply_filters()
        if server_name in self.server_status_labels:
            players, max_players = map(int, status.split(" / "))
            status_text = f"Players: {status} ({'Online' if players > 0 else 'Offline'})"
            self.server_status_labels[server_name].setText(status_text)
        selected_items = self.server_list.selectedItems()
        if selected_items and selected_items[0].text().split(" ", 1)[1] == server_name:
            self.show_server_details(server_name)

    def update_server_list(self):
        self.apply_filters()
        self.server_list.update()
        self.server_list.repaint()

    def update_location_filter(self):
        self.location_filter.clear()
        self.location_filter.addItem("All")
        available_countries = self.get_available_countries()
        self.location_filter.addItems(available_countries)

    def update_tags_filter(self):
        self.tags_filter.clear()
        self.tags_filter.addItem("All")
        all_tags = set()
        for server in servers.values():
            all_tags.update(server.get("tags", []))
        self.tags_filter.addItems(sorted(all_tags))

    def show_all_servers(self):
        self.favorite_filter.setChecked(False)
        self.apply_filters()

    def show_favorites(self):
        self.favorite_filter.setChecked(True)
        self.apply_filters()

    def apply_filters(self):
        search_text = self.search_bar.text().lower()
        selected_anticheat = self.anticheat_filter.currentText()
        selected_whitelist = self.whitelist_filter.currentText()
        selected_location = self.location_filter.currentText()
        selected_tag = self.tags_filter.currentText()
        show_favorites = self.favorite_filter.isChecked()

        self.server_list.clear()
        self.server_status_labels.clear()

        sort_key = self.sort_combo.currentText()
        if sort_key == "Player Count":
            sorted_servers = sorted(servers.keys(), key=lambda x: int(servers[x].get("player_count", "0 / 0").split("/")[0]), reverse=True)
        elif sort_key == "Location":
            sorted_servers = sorted(servers.keys(), key=lambda x: servers[x].get("location", ""))
        elif sort_key == "Favorite":
            sorted_servers = sorted(servers.keys(), key=lambda x: (not servers[x].get("favorite", False), x))
        else:
            sorted_servers = sorted(servers.keys())

        print(f"Sorted servers: {sorted_servers}")

        for server_name in sorted_servers:
            server = servers[server_name]
            matches_search = search_text in server_name.lower()
            matches_anticheat = (selected_anticheat == "All" or server.get('anticheat', 'Unknown') == selected_anticheat)
            matches_whitelist = (
                selected_whitelist == "All" or
                (selected_whitelist == "Yes" and server.get('whitelist', False)) or
                (selected_whitelist == "No" and not server.get('whitelist', False))
            )
            matches_location = (
                selected_location == "All" or
                server.get('location', '') == selected_location
            )
            matches_tag = (
                selected_tag == "All" or
                selected_tag in server.get("tags", [])
            )
            matches_favorite = not show_favorites or server.get("favorite", False)

            print(f"Server: {server_name}, Matches search: {matches_search}, Matches anticheat: {matches_anticheat}, "
                  f"Matches whitelist: {matches_whitelist}, Matches location: {matches_location}, Matches tag: {matches_tag}, Matches favorite: {matches_favorite}")

            if matches_search and matches_anticheat and matches_whitelist and matches_location and matches_tag and matches_favorite:
                item_widget = QWidget()
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(5, 2, 5, 2)

                left_layout = QHBoxLayout()
                server_id = self.extract_server_id(server.get("join_server", ""))
                icon_path = self.server_icons.get(server_id, server.get("icon_path", "")) if server_id else ""
                icon_label = QLabel()
                if icon_path and os.path.exists(icon_path):
                    pixmap = QPixmap(icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio)
                    icon_label.setPixmap(pixmap)
                else:
                    icon_label.setPixmap(self.placeholder_icon)
                left_layout.addWidget(icon_label)

                status_dot = QLabel("●")
                status_dot.setStyleSheet(f"color: {'#00FF00' if server.get('player_count', '0 / 0') != '0 / 0' else '#FF0000'};")
                left_layout.addWidget(status_dot)

                if server.get("favorite", False):
                    favorite_icon = qta.icon('mdi.star', color="#FFD700").pixmap(16, 16)
                    favorite_label = QLabel()
                    favorite_label.setPixmap(favorite_icon)
                    left_layout.addWidget(favorite_label)

                location = server.get("location", "Unknown")
                flag_class = COUNTRY_TO_FLAG_CLASS.get(location, "fi-un")
                flag_label = QLabel()
                flag_label.setProperty("class", f"fi {flag_class}")
                left_layout.addWidget(flag_label)

                display_name = f"{server_name}"
                name_label = QLabel(display_name)
                name_label.setWordWrap(False)
                left_layout.addWidget(name_label)

                item_layout.addLayout(left_layout)
                item_layout.addStretch()

                status_label = QLabel(f"Players: {server.get('player_count', '0 / 0')}")
                players, max_players = map(int, server.get("player_count", "0 / 0").split(" / "))
                fullness = players / max_players if max_players > 0 else 0
                color = "#00FF00" if fullness < 0.5 else "#FFFF00" if fullness < 0.9 else "#FF0000"
                status_text = f"Players: {server.get('player_count', '0 / 0')} ({'Online' if players > 0 else 'Offline'})"
                status_label.setText(status_text)
                status_label.setStyleSheet(f"color: {color}; padding-right: 10px;")
                item_layout.addWidget(status_label)

                item = QListWidgetItem(self.server_list)
                item.setText(display_name)
                item.setSizeHint(item_widget.sizeHint())
                self.server_list.addItem(item)
                self.server_list.setItemWidget(item, item_widget)
                self.server_status_labels[server_name] = status_label
                print(f"Added {server_name} to UI list")

    def clear_filters(self):
        self.search_bar.clear()
        self.location_filter.setCurrentText("All")
        self.anticheat_filter.setCurrentText("All")
        self.whitelist_filter.setCurrentText("All")
        self.tags_filter.setCurrentText("All")
        self.favorite_filter.setChecked(False)
        self.apply_filters()

    def on_selection_changed(self):
        selected_items = self.server_list.selectedItems()
        if selected_items:
            display_name = selected_items[0].text()
            server_name = display_name
            self.last_selected_server = server_name
            self.show_server_details(server_name)
        else:
            self.show_default_message()

    def show_server_details(self, server_name):
        self.clear_result_layout()
        server = servers.get(server_name)
        if not server:
            self.show_default_message()
            return

        details_layout = QVBoxLayout()

        server_info = QGroupBox("Server Information")
        info_layout = QFormLayout()
        info_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        name_label = QLabel(server_name)
        info_layout.addRow("Name:", name_label)

        location_label = QLabel(server.get("location", "Unknown"))
        info_layout.addRow("Location:", location_label)

        join_layout = QHBoxLayout()
        join_label = QLabel(server.get("join_server", "N/A"))
        join_layout.addWidget(join_label)
        copy_join_btn = QPushButton("Copy URL")
        copy_join_btn.setIcon(qta.icon('mdi.content-copy', color="#E0E0E0"))
        copy_join_btn.setToolTip("Copy join URL to clipboard")
        copy_join_btn.clicked.connect(lambda: self.copy_join_url(server.get("join_server", "")))
        join_layout.addWidget(copy_join_btn)
        info_layout.addRow("Join Server:", join_layout)

        anticheat_label = QLabel(server.get("anticheat", "Unknown"))
        info_layout.addRow("AntiCheat:", anticheat_label)

        tags_label = QLabel(", ".join(server.get("tags", [])))
        info_layout.addRow("Tags:", tags_label)

        whitelist_label = QLabel("Yes" if server.get("whitelist", False) else "No")
        info_layout.addRow("Whitelist:", whitelist_label)

        premium_label = QLabel("Yes" if server.get("premium", False) else "No")
        info_layout.addRow("Premium:", premium_label)

        last_updated_label = QLabel(server.get("last_updated", "N/A"))
        info_layout.addRow("Last Updated:", last_updated_label)

        server_info.setLayout(info_layout)
        details_layout.addWidget(server_info)

        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        notes_text = QTextEdit(server.get("notes", ""))
        notes_text.setReadOnly(True)
        notes_text.setFixedHeight(80)
        notes_layout.addWidget(notes_text)
        notes_group.setLayout(notes_layout)
        details_layout.addWidget(notes_group)

        triggers_group = QGroupBox("Triggers")
        triggers_layout = QVBoxLayout()
        triggers = server.get("triggers", [])
        if triggers:
            for idx, trigger in enumerate(triggers, 1):
                trigger_block = TriggerBlock(trigger.get("trigger", ""), trigger.get("description", ""), idx)
                triggers_layout.addWidget(trigger_block)
        else:
            no_triggers_label = QLabel("No triggers available.")
            no_triggers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            triggers_layout.addWidget(no_triggers_label)
        triggers_group.setLayout(triggers_layout)
        details_layout.addWidget(triggers_group)

        self.result_layout.addLayout(details_layout)
        self.result_widget.adjustSize()

    def copy_join_url(self, join_url):
        clipboard = QApplication.clipboard()
        clipboard.setText(join_url)
        QMessageBox.information(self, "Copied", "Join URL copied to clipboard!")

    def clear_result_layout(self):
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def open_add_edit_window(self):
        selected_items = self.server_list.selectedItems()
        server_name = None
        if selected_items:
            display_name = selected_items[0].text()
            server_name = display_name

        dialog = AddEditWindow(self, server_name)
        dialog.exec()

    def delete_server(self):
        selected_items = self.server_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select a server to delete.")
            return

        display_name = selected_items[0].text()
        server_name = display_name

        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete {server_name}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if server_name in servers:
                del servers[server_name]
                save_servers()
                self.update_server_list()
                self.update_location_filter()
                self.update_tags_filter()
                self.show_default_message()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    