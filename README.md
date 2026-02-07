# GUI-score-manager

A Python GUI application for the management of student scores and admin accounts, built with **Tkinter** and **SQLite**, featuring CRUD operations and CSV export.

Version 2.0 - Refactored with modular architecture following SOLID principles.
---

## Features

* **Student Data Management:** Easily add, edit, delete, and view student scores.
* **Secure Access:** Includes a manager account system for protected access.
* **Data Export:** Export all managed data to a CSV file.
* **User-Friendly Interface:** Intuitive graphical interface developed with Tkinter.

---

## Tech Stack

* **Python 3.11.13+**
* **Tkinter** (Graphical User Interface)
* **SQLite** (Local Database)

---

## Getting Started

This project is primarily designed to run as standalone executable files. The Python source code (`.py` files) provided in this repository is intended for building these executables.

### 1. Clone the Repository

First, clone this project from GitHub to your local machine:

```bash
git clone https://github.com/kusogame68/GUI-score-manager.git
cd GUI-score-manager
```

### 2. Prerequisites

Ensure you have `uv` installed, as it's used for dependency management and building.

* **Windows:**
    ```powershell
    irm https://astral.sh/uv/install.ps1 | iex
    ```

### 3. Build Executables

Follow these steps to set up your development environment and build the executable files:

1.  **Navigate to the project directory:**
    ```bash
    cd GUI-score-manager
    ```

2.  **Initialize the `uv` environment and install dependencies:**
    This command will create a virtual environment (`.venv`) and install all required packages (including `pandas` and `pyinstaller`) as defined in `pyproject.toml`.
    ```bash
    uv sync --dev
    ```

3.  **Build the executable files:**
    Use `uv run` to execute `pyinstaller` within the virtual environment, ensuring all dependencies are correctly linked.
    ```bash
    uv run pyinstaller -F -w --icon=./Image/login.ico AccountApp.py
    uv run pyinstaller -F -w --icon=./Image/doc.ico StudentsApp.py
    ```

    * `-F`: Packages the application into a single executable file.
    * `-w`: Suppresses the console window for GUI applications.
    * `--icon=PATH`: Sets a custom icon for the executable (e.g., `./Image/login.ico`).

---

## Running the Application

Once the executables are built (you'll find them in the newly created `dist/` folder):

1.  Launch `./dist/AccountApp.exe` for creating log-in account and managing manager accounts.
2.  Launch `./dist/StudentsApp.exe` for student score management.
3.  Log in as a manager to begin managing student data.
4.  All student scores can be exported to a CSV file from within the application.

---

## Output

* Generates a CSV file containing all student scores upon export from the application.

---

## Version 2.0 Changes

### What's New

* **Modular Architecture**:  
  Code split into three modules. (`base.py`, `studentapp.py`, `accountapp.py`)

* **SOLID Principles**:  
  Improved code structure following best practices.

* **Better Code Reusability**:  
  Shared components extracted to `base.py`.

* **Enhanced Documentation**:  
  Complete type hints and docstrings.

* **Cleaner Separation of Concerns**:  
  UI framework separated from business logic.