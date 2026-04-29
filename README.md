# Food Delivery Application (Frappe/ERPNext v15+)

A comprehensive, Swiggy-like food delivery management system built on top of the Frappe Framework and ERPNext v15.

## 🚀 Features

### 🏪 Restaurant Management
- Track restaurant profiles, locations (Lat/Long), operational hours, and minimum order limits.
- Manage multi-category menus with veg/non-veg tags and pricing.
- Support for dish add-ons and customization variants.

### 🛍️ Order Lifecycle
- Real-time order tracking from **Pending** ➡️ **Confirmed** ➡️ **Preparing** ➡️ **Ready for Pickup** ➡️ **Out for Delivery** ➡️ **Delivered**.
- Automated tax calculation, delivery fee handling, and coupon application.

### 🚴 Delivery Operations
- Agent availability status mapping.
- Geolocation coordinates tracking for live assignment.
- Smart delivery zones mapped via Pincodes/GeoJSON.

### 📊 Analytics & Growth
- **Script Reports**: Daily Order Summaries, Restaurant Top Performers, Delivery Payouts.
- **Live Desk Page**: Core business KPIs rendered via JS visualization.

---

## 📂 Directory Structure

```
food_delivery/
├── setup.py                  # App packaging script
├── requirements.txt          # Dependencies
├── food_delivery/
│   ├── hooks.py              # App hooks & events
│   ├── modules.txt           # Registered Frappe Modules
│   ├── doctype/              # Core schemas
│   │   ├── restaurant/
│   │   ├── food_order/
│   │   └── [10+ other DocTypes]
│   ├── api/                  # Whitelisted endpoints
│   └── report/               # Python query scripts
```

---

## 🛠️ Installation

1. **Download the app** inside your Bench's `apps` folder:
   ```bash
   cd /path/to/your/frappe-bench/apps
   git clone https://github.com/balaji-001-gif/food_delivery.git
   ```

2. **Install the app** onto your site:
   ```bash
   bench get-app food_delivery
   bench --site [your-site-name] install-app food_delivery
   bench migrate
   ```

3. **Start the development server**:
   ```bash
   bench start
   ```

## 📄 License
Distributed under the **MIT License**.
