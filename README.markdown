# 💽 Drive Formatter Pro

A professional, modern, multi-language disk formatting utility built with **Python** and **PyQt6**, featuring a Windows 11 styled interface with multiple themes and full RTL/LTR language support.

---

# 🇬🇧 English

## Overview

**Drive Formatter Pro** is a professional desktop application for formatting, inspecting, and managing disk drives. It offers a clean, modern Windows 11 styled interface, multiple visual themes, and full support for English, Persian, and Chinese languages with correct right-to-left and left-to-right layout handling.

## Features

- 🖥️ Modern Windows 11 styled interface built with PyQt6
- 🎨 Five built-in themes: Windows 11 Light, Windows 11 Dark, Windows 11 Default, Red, and Blue
- 🌐 Three languages: English, Persian (فارسی), and Chinese (中文) — with automatic RTL/LTR layout switching
- 💾 Automatic detection and listing of all connected drives with detailed information
- 📊 Real-time drive usage statistics (total, used, and free space)
- ⚙️ Full format configuration: file system (NTFS, FAT32, exFAT, ReFS), volume label, allocation unit size, quick or full format
- 🛡️ Multi-step safety confirmation before any destructive operation, with automatic protection against formatting the system drive
- 🧰 Additional tools: Disk Information viewer, Check Disk (error scanning), Secure Erase (multi-pass wipe), and Safe Eject
- 📝 Built-in operation log with save-to-file support
- 🔧 Persistent user settings (language, theme, confirmation preferences, startup behavior)
- 🖱️ Fully responsive, resizable, and accessible layout

## Requirements

- Python 3.10 or higher
- Windows 10/11 (recommended for full formatting functionality)
- Administrator privileges (required for formatting operations)

## Installation

### 1. Install the required libraries

Run the following command in your terminal to install all dependencies at once:

```bash
pip install -r requirements.txt
```

Or install each library individually:

```bash
pip install PyQt6
pip install psutil
```

### 2. Run the application

Launch the application with:

```bash
python main.py
```

> **Note:** On Windows, right-click your terminal (Command Prompt / PowerShell) and select **"Run as Administrator"** before launching the app, since formatting drives requires elevated privileges.

## Usage

1. Launch the application; connected drives will be listed automatically.
2. Select a drive from the list to view its detailed information.
3. Choose your desired file system, volume label, allocation unit, and format type.
4. Click **Format Drive** and type the drive letter to confirm the operation.
5. Monitor progress through the progress bar and operation log.

## License

This project is provided for educational and professional use. Use responsibly — formatting a drive permanently erases all data on it.

---

# 🇮🇷 فارسی

## معرفی

**فرمت‌کننده حرفه‌ای درایو** یک برنامه دسکتاپ حرفه‌ای برای فرمت کردن، بررسی و مدیریت درایوهای دیسک است. این برنامه دارای رابط کاربری مدرن به سبک ویندوز ۱۱، چندین پوسته بصری، و پشتیبانی کامل از زبان‌های انگلیسی، فارسی و چینی همراه با مدیریت صحیح جهت متن راست‌چین و چپ‌چین می‌باشد.

## ویژگی‌ها

- 🖥️ رابط کاربری مدرن به سبک ویندوز ۱۱ ساخته شده با PyQt6
- 🎨 پنج پوسته آماده: ویندوز ۱۱ روشن، ویندوز ۱۱ تاریک، ویندوز ۱۱ پیش‌فرض، پوسته قرمز و پوسته آبی
- 🌐 سه زبان: انگلیسی، فارسی و چینی — با تغییر خودکار جهت متن به راست‌چین یا چپ‌چین
- 💾 شناسایی و نمایش خودکار تمام درایوهای متصل همراه با اطلاعات کامل
- 📊 نمایش آمار لحظه‌ای فضای درایو (حجم کل، استفاده شده و آزاد)
- ⚙️ تنظیمات کامل فرمت: سیستم فایل (NTFS، FAT32، exFAT، ReFS)، برچسب حجم، اندازه واحد تخصیص، فرمت سریع یا کامل
- 🛡️ تأیید چند مرحله‌ای امنیتی پیش از هر عملیات مخرب، همراه با محافظت خودکار در برابر فرمت درایو سیستم
- 🧰 ابزارهای اضافی: نمایشگر اطلاعات دیسک، بررسی خطای دیسک، پاک‌سازی امن (چند مرحله‌ای) و خارج کردن ایمن درایو
- 📝 گزارش عملیات داخلی همراه با قابلیت ذخیره در فایل
- 🔧 ذخیره دائمی تنظیمات کاربر (زبان، پوسته، تنظیمات تأیید و رفتار هنگام شروع)
- 🖱️ چیدمان کاملاً واکنش‌گرا، قابل تغییر اندازه و در دسترس

## پیش‌نیازها

- پایتون نسخه ۳.۱۰ یا بالاتر
- ویندوز ۱۰ یا ۱۱ (برای عملکرد کامل فرمت توصیه می‌شود)
- دسترسی مدیر سیستم (برای انجام عملیات فرمت الزامی است)

## نصب

### ۱. نصب کتابخانه‌های مورد نیاز

دستور زیر را در ترمینال اجرا کنید تا تمام وابستگی‌ها یکجا نصب شوند:

```bash
pip install -r requirements.txt
```

یا هر کتابخانه را به‌صورت جداگانه نصب کنید:

```bash
pip install PyQt6
pip install psutil
```

### ۲. اجرای برنامه

برنامه را با دستور زیر اجرا کنید:

```bash
python main.py
```

> **نکته:** در ویندوز، پیش از اجرای برنامه، روی ترمینال (Command Prompt یا PowerShell) کلیک راست کرده و گزینه **"Run as Administrator"** را انتخاب کنید، زیرا فرمت درایو نیازمند دسترسی مدیر سیستم است.

## نحوه استفاده

۱. برنامه را اجرا کنید؛ درایوهای متصل به‌صورت خودکار نمایش داده می‌شوند.
۲. یک درایو را از لیست انتخاب کنید تا اطلاعات کامل آن نمایش داده شود.
۳. سیستم فایل، برچسب حجم، اندازه واحد تخصیص و نوع فرمت مورد نظر را انتخاب کنید.
۴. روی دکمه **فرمت درایو** کلیک کرده و حرف درایو را برای تأیید عملیات تایپ کنید.
۵. روند عملیات را از طریق نوار پیشرفت و گزارش عملیات دنبال کنید.

## مجوز استفاده

این پروژه برای استفاده آموزشی و حرفه‌ای ارائه شده است. لطفاً با مسئولیت‌پذیری استفاده کنید — فرمت کردن یک درایو تمام اطلاعات آن را برای همیشه پاک می‌کند.

---

# 🇨🇳 中文

## 概述

**专业驱动器格式化工具** 是一款用于格式化、检查和管理磁盘驱动器的专业桌面应用程序。它拥有简洁现代的 Windows 11 风格界面、多种视觉主题，并完全支持英语、波斯语和中文，同时正确处理从右到左与从左到右的排版方向。

## 功能特点

- 🖥️ 使用 PyQt6 构建的现代 Windows 11 风格界面
- 🎨 内置五种主题：Windows 11 浅色、Windows 11 深色、Windows 11 默认、红色主题和蓝色主题
- 🌐 支持三种语言：英语、波斯语（فارسی）和中文（中文）——自动切换从右到左或从左到右的排版方向
- 💾 自动检测并列出所有已连接的驱动器及其详细信息
- 📊 实时显示驱动器使用统计信息（总容量、已用空间和可用空间）
- ⚙️ 完整的格式化配置选项：文件系统（NTFS、FAT32、exFAT、ReFS）、卷标、分配单元大小、快速或完全格式化
- 🛡️ 在任何破坏性操作前进行多步骤安全确认，并自动防止格式化系统驱动器
- 🧰 附加工具：磁盘信息查看器、磁盘检查（错误扫描）、安全擦除（多次覆写）和安全弹出
- 📝 内置操作日志，支持保存为文件
- 🔧 持久化用户设置（语言、主题、确认偏好和启动行为）
- 🖱️ 完全响应式、可调整大小且易于访问的布局

## 系统要求

- Python 3.10 或更高版本
- Windows 10/11（推荐使用，以获得完整的格式化功能）
- 管理员权限（执行格式化操作时必需）

## 安装步骤

### 1. 安装所需的库

在终端中运行以下命令，一次性安装所有依赖项：

```bash
pip install -r requirements.txt
```

或单独安装每个库：

```bash
pip install PyQt6
pip install psutil
```

### 2. 运行应用程序

使用以下命令启动应用程序：

```bash
python main.py
```

> **提示：** 在 Windows 系统中，启动应用程序前，请右键点击终端（命令提示符或 PowerShell），选择 **"以管理员身份运行"**，因为格式化驱动器需要提升的权限。

## 使用方法

1. 启动应用程序后，已连接的驱动器将自动列出。
2. 从列表中选择一个驱动器以查看其详细信息。
3. 选择所需的文件系统、卷标、分配单元大小和格式化类型。
4. 点击 **格式化驱动器** 按钮，并输入驱动器盘符以确认操作。
5. 通过进度条和操作日志监控操作进度。

## 许可

本项目仅供教育和专业用途使用。请负责任地使用——格式化驱动器将永久删除其上的所有数据。
