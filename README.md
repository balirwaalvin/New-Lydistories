<p align="center">
  <img src="public/logo.png" alt="Lydistories Logo" width="120" height="120" style="border-radius: 20px;" />
</p>

<h1 align="center">Lydistories</h1>

<p align="center">
  <strong>A premium digital reading platform for books, study guides, articles & documentation.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Frontend-React%20+%20Vite-61DAFB?style=for-the-badge&logo=react&logoColor=white" />
  <img src="https://img.shields.io/badge/Backend-Flask%20+%20SQLite-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/Auth-JWT-orange?style=for-the-badge&logo=jsonwebtokens&logoColor=white" />
  <img src="https://img.shields.io/badge/Payments-Mobile%20Money-34D399?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" />
</p>

---

## 📖 About

**Lydistories** is a full-stack web application that lets users browse, preview, purchase, and read digital content — all from the browser. Admins manage the library through a dedicated portal, uploading PDFs and setting per-item pricing. Payments are handled through a simulated **Mobile Money** gateway with OTP verification.

### Why Lydistories?

- 🌍 Built for the **African digital reading market**
- 💳 **Mobile Money** payment flow familiar to local users
- 📄 Upload a PDF and text is **extracted automatically**
- 💰 Admins control **per-item pricing** — no subscriptions required
- 🎨 Premium **dark-mode UI** with a striking red/black/white design

---

## ✨ Features

### For Readers

| Feature                      | Description                                                                        |
| ---------------------------- | ---------------------------------------------------------------------------------- |
| 📚 **Browse & Search**       | Filter by category (Books, Guides, Articles, Documents), search by title or author |
| 👁️ **Free Previews**         | Read preview text before purchasing — no login required                            |
| 💳 **Mobile Money Payments** | Pay via phone number → receive OTP → confirm → instant access                      |
| 📖 **Full Reader**           | Adjustable font size, clean reading experience                                     |
| 🔖 **Bookmarks**             | Save content for later from any page                                               |
| 📊 **Reading Progress**      | Track how far you've read across your library                                      |
| 📱 **Responsive Design**     | Works seamlessly on mobile, tablet, and desktop                                    |

### For Admins

| Feature                   | Description                                       |
| ------------------------- | ------------------------------------------------- |
| 📈 **Dashboard**          | Real-time stats — users, revenue, transactions    |
| 📝 **Content Management** | Create, edit, delete content with live preview    |
| 📄 **PDF Upload**         | Upload PDFs — text is auto-extracted via PyPDF2   |
| 💰 **Custom Pricing**     | Set individual prices (UGX) for each content item |
| ⭐ **Featured Content**   | Toggle items to appear on the homepage            |
| 👥 **User Management**    | View users, toggle admin roles, remove accounts   |

---

## 🛠️ Tech Stack

```
┌─────────────────────────────────────────────────────┐
│  FRONTEND              │  BACKEND                   │
│  ─────────             │  ────────                  │
│  React 19              │  Python Flask              │
│  Vite                  │  SQLite                    │
│  React Router v7       │  PyJWT (Authentication)    │
│  React Icons           │  bcrypt (Password Hashing) │
│  Vanilla CSS           │  PyPDF2 (PDF Extraction)   │
│  Google Fonts          │  Flask-CORS                │
│  (Outfit + Inter)      │                            │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+

### 1. Clone the repository

```bash
git clone https://github.com/balirwaalvin/New-Lydistories.git
cd New-Lydistories
```

### 2. Install dependencies

```bash
# Frontend
npm install

# Backend
pip install flask flask-cors pyjwt bcrypt pypdf2
```

### 3. Start the servers

```bash
# Terminal 1 — Backend API (port 5000)
python server/app.py

# Terminal 2 — Frontend Dev Server (port 5173)
npm run dev
```

### 4. Open in browser

```
http://localhost:5173
```

### Default Admin Account

| Field    | Value                   |
| -------- | ----------------------- |
| Email    | `admin@lydistories.com` |
| Password | `Lydistories2026!`      |

> ⚠️ **Change these credentials before deploying to production.**

---

## 📁 Project Structure

```
New-Lydistories/
├── index.html                      # Entry point with SEO meta tags
├── public/
│   └── logo.png                    # App logo / favicon
├── src/
│   ├── main.jsx                    # React mount
│   ├── App.jsx                     # Router & route definitions
│   ├── index.css                   # Global design system
│   ├── context/
│   │   └── AuthContext.jsx         # JWT auth state management
│   ├── hooks/
│   │   └── useApi.js               # Authenticated fetch wrapper
│   ├── components/
│   │   ├── Navbar.jsx              # Navigation + search + profile
│   │   ├── Footer.jsx              # Site footer
│   │   ├── ContentCard.jsx         # Browse grid cards
│   │   ├── PaymentModal.jsx        # Mobile Money OTP payment flow
│   │   └── ProtectedRoute.jsx      # Auth & admin route guards
│   └── pages/
│       ├── HomePage.jsx            # Landing page with hero & CTA
│       ├── BrowsePage.jsx          # Search + filter catalog
│       ├── ContentPage.jsx         # Reader + paywall
│       ├── LoginPage.jsx           # Login form
│       ├── RegisterPage.jsx        # Registration form
│       ├── Dashboard.jsx           # User library & stats
│       └── admin/
│           ├── AdminDashboard.jsx  # Admin stats & overview
│           ├── AdminContent.jsx    # Content list management
│           ├── AdminContentEditor.jsx # Create/edit content + PDF upload
│           └── AdminUsers.jsx      # User management
└── server/
    ├── app.py                      # Flask entry point
    ├── database.py                 # SQLite schema, migrations & seed data
    └── routes/
        ├── auth.py                 # Register, login, JWT middleware
        ├── content.py              # Content CRUD + PDF extraction
        ├── payments.py             # Mobile Money simulation
        └── users.py                # User mgmt, bookmarks, progress
```

---

## 🔌 API Reference

### Authentication

| Method | Endpoint             | Description              |
| ------ | -------------------- | ------------------------ |
| `POST` | `/api/auth/register` | Create a new account     |
| `POST` | `/api/auth/login`    | Login & receive JWT      |
| `GET`  | `/api/auth/me`       | Get current user profile |

### Content

| Method   | Endpoint           | Description                                           |
| -------- | ------------------ | ----------------------------------------------------- |
| `GET`    | `/api/content`     | List all content (supports `?category=` & `?search=`) |
| `GET`    | `/api/content/:id` | Get content detail (full text if user has access)     |
| `POST`   | `/api/content`     | Create content (admin, supports PDF upload)           |
| `PUT`    | `/api/content/:id` | Update content (admin)                                |
| `DELETE` | `/api/content/:id` | Delete content (admin)                                |

### Payments

| Method | Endpoint                 | Description                                |
| ------ | ------------------------ | ------------------------------------------ |
| `POST` | `/api/payments/initiate` | Start payment (returns OTP for simulation) |
| `POST` | `/api/payments/confirm`  | Confirm payment with OTP                   |
| `GET`  | `/api/payments/history`  | User's payment history                     |

### Users & Features

| Method     | Endpoint                | Description                    |
| ---------- | ----------------------- | ------------------------------ |
| `GET`      | `/api/users`            | List all users (admin)         |
| `GET`      | `/api/users/stats`      | Platform statistics (admin)    |
| `GET/POST` | `/api/bookmarks`        | Get or add bookmarks           |
| `DELETE`   | `/api/bookmarks/:id`    | Remove a bookmark              |
| `GET/PUT`  | `/api/reading-progress` | Get or update reading progress |
| `GET`      | `/api/users/dashboard`  | User dashboard data            |

---

## 💳 Payment Flow

The app simulates a **Mobile Money** payment (MTN, Airtel, etc.):

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Enter Phone │ ──▶ │  Receive OTP │ ──▶ │   Confirm &  │
│   Number     │     │  (simulated) │     │ Get Access   │
└──────────────┘     └──────────────┘     └──────────────┘
```

> **Note:** In production, replace the OTP simulation with a real Mobile Money API (e.g., Flutterwave, MTN MoMo API, or Airtel Money API).

---

## 🎨 Design System

| Token           | Value                                                      |
| --------------- | ---------------------------------------------------------- |
| Primary Red     | `#C41E24`                                                  |
| Dark Background | `#0D0D0D`                                                  |
| Light Text      | `#FFFFFF`                                                  |
| Display Font    | [Outfit](https://fonts.google.com/specimen/Outfit)         |
| Body Font       | [Inter](https://fonts.google.com/specimen/Inter)           |
| Card Style      | Glassmorphism with subtle borders                          |
| Animations      | Smooth page transitions, hover effects, micro-interactions |

---

## 🗄️ Database Schema

```
users ──────────────── payments
  │                      │
  ├── user_content_access ┘
  │
  ├── bookmarks
  │
  └── reading_progress

content ─── payments
   │
   ├── user_content_access
   │
   └── bookmarks
```

**6 tables:** `users`, `content`, `payments`, `user_content_access`, `bookmarks`, `reading_progress`

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Alvin Balirwa**

- GitHub: [@balirwaalvin](https://github.com/balirwaalvin)
- Email: sanyukalvin@gmail.com

---

<p align="center">
  Built with ❤️ for readers everywhere
</p>
