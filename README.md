# GUI-gradebook-manager

A Tkinter and SQLite desktop application for managing student gradebooks and user accounts, featuring CRUD operations and CSV export.

Version 3.0 - Refactored into a layered architecture (interfaces / implementations / domain modules) following SOLID principles.

---

## Features

* **Score Data Management:** Easily add, edit, delete, and view scores.
* **Secure Access:** Includes a manager account system for protected access.
* **Data Export:** Export all managed data to a CSV file.
* **User-Friendly Interface:** Intuitive graphical interface developed with Tkinter.

---

## Tech Stack

* **Python 3.11.13+**
* **Tkinter**
* **SQLite**

---

## Getting Started

This project is primarily designed to run as standalone executable files. The Python source code provided in this repository is intended for building these executables.

### 1. Clone the Repository

First, clone this project from GitHub to your local machine:

```bash
git clone https://github.com/kusogame68/GUI-gradebook-manager.git
cd GUI-gradebook-manager
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
    ```cmd
    cd GUI-gradebook-manager
    ```

2.  **Initialize the `uv` environment and install dependencies:**
    This command will create a virtual environment (`.venv`) and install all required packages (including `pandas` and `pyinstaller`) as defined in `pyproject.toml`.
    ```cmd
    uv sync
    ```

3.  **Build the executable files:**
    Use `uv run python -m PyInstaller` (rather than the `pyinstaller` command directly) within the virtual environment.
    ```cmd
    uv run python -m PyInstaller -F -w --paths . --name ManagerApp --icon=./Image/manager.ico ./member/main.py && move .\dist\ManagerApp.exe .\ && rmdir /s /q build dist && del /q *.spec

    uv run python -m PyInstaller -F -w --paths . --name GradebookApp --icon=./Image/doc.ico ./gradebook/main.py && move .\dist\GradebookApp.exe .\ && rmdir /s /q build dist && del /q *.spec
    ```

    * `-F`: Packages the application into a single executable file.
    * `-w`: Suppresses the console window for GUI applications.
    * `--icon=PATH`: Sets a custom icon for the executable (e.g., `./Image/login.ico`).
    * `--paths .`: Lets PyInstaller resolve imports across the project's top-level packages (`interfaces`, `implementations`, `tools`, `login`, `member`, `gradebook`).

---

## Running the Application

Once the executables are built, place them alongside the `GUI-gradebook-manager/` folder:

1.  Launch `ManagerApp.exe` to create and manage login accounts.
2.  Launch `GradebookApp.exe`  — it opens with a login screen first; enter a valid account and password to proceed to the student score management screen.
3.  Manage scores from there (add, query, update, delete).
4.  Closing either window exports its current data to a CSV file automatically.

---

## Output

* Closing `ManagerApp.exe` exports the account list to a CSV file.
* Closing `GradebookApp.exe` exports all scores to a CSV file.

---

## Version 3.0 Changes

### Project Structure

<table>
<tr>
<th align="center">Current (After)</th>
<th align="center"></th>
<th align="center">Previous (Before)</th>
</tr>
<tr>
<td valign="top">

```
GUI-gradebook-manager/
├── Image/
│   ├── doc.ico
│   ├── manager.ico
│   └── person.ico
│
├── interfaces/
│   ├── repository.py
│   └── view.py
│
├── implementations/
│   ├── sqlite_repository.py
│   └── tk_management_view.py
│
├── tools/
│   └── csv_exporter.py
│
├── login/
│   ├── view.py
│   └── controller.py
│
├── member/
│   ├── service.py
│   ├── view.py
│   ├── controller.py
│   └── main.py
│
├── gradebook/
│   ├── service.py
│   ├── view.py
│   ├── controller.py
│   └── main.py
│
├── pyproject.toml
└── uv.lock
```

</td>
<td align="center" valign="middle">◀----- after</td>
<td valign="top">

```
GUI-gradebook-manager/
├── Image/
│   ├── doc.ico
│   ├── login.ico
│   └── person.ico
│
├── accountApp.py
├── gradebookApp.py
├── base.py
│
├── pyproject.toml
└── uv.lock
```

</td>
</tr>
</table>

### What's New

* **Layered Architecture (Ports & Adapters):**
  `interfaces/` holds abstract contracts (`Repository`, `View`); `implementations/` holds the concrete SQLite and Tkinter adapters that fulfill them. Domain modules only depend on the abstractions, never the concrete classes.

* **Domain Modules:**
  `member/`, `gradebook/`, and `login/` each contain their own `service.py` (business rules), `view.py` (screen-specific config), and `controller.py` (wires repository + service + view together). `login/` has no dependency on `gradebook/`; it reports success through an injected callback.

* **SOLID Principles:**
  * *SRP* — validation, average/grade computation, data access, and UI construction are each in their own file.
  * *DIP* — `Controller` classes depend on the `Repository`/`View` interfaces, not on `SqliteRepository`/`TkManagementView` directly.
  * *DRY* — CSV export logic is centralized in `tools/csv_exporter.py`, shared by both `member` and `gradebook`.

* **Composition Roots:**
  `member/main.py` and `gradebook/main.py` are the only files that import concrete implementations directly and wire everything together — `gradebook/main.py` additionally assembles the login flow before launching the gradebook screen.

* **Type Hints:**
  Maintained throughout all modules for clarity and easier maintenance.