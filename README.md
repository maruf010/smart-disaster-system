# Smart Disaster & Emergency Resource Management System (SDERMS)

A Python & SQLite desktop application for university disaster management featuring automated multi-criteria risk scoring, population-proportional relief distribution, optimal shelter recommendation, rescue squad tracking, civilian volunteer coordination, and Dijkstra shortest path routing.

---

## 🚀 Features

- **Executive Dashboard**: Real-time KPI statistics (active disasters, affected casualties, critical queue, shelter capacity, and rescue readiness).
- **Disaster Management**: Register incidents, track severity ratings, and toggle resolution status.
- **Emergency Priority Queue**: Real-time automated risk score calculation (0–100) and live prioritization.
- **Shelter Operations**: Visual occupancy progress bars with optimal **Best-Fit Shelter Recommendation** algorithm.
- **Supply & Resource Allocation**: Inventory tracking, critical stock alerts, and **Population-Proportional Distribution** calculation.
- **Rescue Squads & Volunteers**: Real-time squad status dispatching and civilian volunteer skill registry.
- **Road Network & Dijkstra Navigation**: Visual Dijkstra shortest route pathfinder with live road obstruction / blockade simulation.
- **Reports & Export**: One-click CSV audit report export.
- **Modern UI**: Full Dark / Light mode toggle powered by CustomTkinter.

---

## 🔐 Default Credentials
- **Username:** `admin`
- **Password:** `admin123`

---

## 💻 How to Run

### Option 1: Desktop GUI Application (Recommended)
```bash
python gui_main.py
```

### Option 2: Console (CLI) Application
```bash
python main.py
```

---

## 📦 Requirements
Install required desktop GUI packages:
```bash
pip install -r requirements.txt
```
*(Uses standard libraries + `customtkinter`)*
