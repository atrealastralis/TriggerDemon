# Trigger Deamon

**Trigger Deamon** is a Python application built with PyQt6 to manage and monitor FiveM servers. It provides a user-friendly interface to track server statuses, manage triggers, and filter servers based on various criteria such as location, anti-cheat systems, and tags. The application supports both dark and light themes for a better user experience.

## Features
- **Server Management**: Add, edit, and delete FiveM servers with ease.
- **Server Status Monitoring**: View real-time player counts and server status (online/offline).
- **Trigger Management**: Add and manage triggers for each server with descriptions.
- **Advanced Filtering**: Filter servers by location, anti-cheat system, whitelist status, tags, and favorites.
- **Theme Support**: Switch between dark and light themes for better visibility.
- **Auto-Refresh**: Automatically refresh server statuses at configurable intervals.
- **Favorites**: Mark servers as favorites for quick access.
- **Export/Import**: Export and import server configurations as JSON files.
- **Context Menu**: Right-click servers for quick actions like connecting, copying details, or editing.

## Screenshots
*(Optional: Add screenshots of your application here to showcase its interface. You can take screenshots, upload them to the repository, and link them here.)*

Example:
![Main Window](screenshots/main_window.png)
![Add Server](screenshots/add_server.png)

## Requirements
- Python 3.8 or higher
- PyQt6
- qtawesome
- requests
- beautifulsoup4
- flag-icons (CSS library for country flags, included in the project)

## Installation
Follow these steps to set up and run **Trigger Deamon** on your system:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/atrealastra/TriggerDeamon.git
   cd TriggerDeamon
