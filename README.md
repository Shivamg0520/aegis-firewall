# Aegis Firewall

Aegis Firewall is a simple desktop application built with tkinter and ttkbootstrap. It allows you to view active applications and manage their network access using Windows Firewall rules.

## Features

- **View Active Applications:** Lists currently running user applications (system processes are filtered out).
- **Block Applications:** Block selected applications from accessing the network by creating outbound firewall rules.
- **Unblock Applications:** Remove firewall rules to allow previously blocked applications.
- **Search Functionality:** Easily search for applications in the list.
- **Real-time Status:** Displays the current status of each application (Blocked/Not Blocked).
- **Modern Interface:** Built with ttkbootstrap for a clean and modern look.

## Requirements

- Python 3.x
- tkinter (usually included with Python)
- psutil
- ttkbootstrap

## Installation

1. Clone the repository or download `main_firewall_app.py`:

    ```sh
    git clone https://github.com/Shivamg0520/aegis-firewall.git
    cd aegis-firewall
    ```

2. Install the required Python packages:

    ```sh
    pip install psutil ttkbootstrap
    ```

## Usage

1. Run the application:

    ```sh
    python main_firewall_app.py
    ```

2. Browse the list of active applications, use the search bar, and use the Block/Unblock buttons as needed.
3. Click "Refresh List" to update the list of applications and their firewall status.

## How it Works

- Uses the `netsh advfirewall firewall` command-line utility to manage Windows Firewall rules.
- Uses `psutil` to fetch information about running processes.
- Uses `subprocess` to execute firewall commands.
- The GUI is built with tkinter and ttkbootstrap.

## Important Notes

- **Administrator Rights:** The application requires administrator privileges to add, delete, or modify Windows Firewall rules.
- **Rule Naming:** All firewall rules created by this app are prefixed with `ProjectAegis_` for easy identification.
- **System Processes:** Common Windows system processes are filtered out from the list.

## License

