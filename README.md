### 📌 **Requirements to Use ModzForwarder Bot**  

#### ✅ **1. Install Python (Version 3.7 or Higher)**  
Download and install Python from [python.org](https://www.python.org/downloads/).  
Verify installation by running:  
```bash
python --version
```

#### ✅ **2. Install Required Libraries**  
Open **Command Prompt (CMD) or Terminal** and run:  
```bash
pip install pyrogram tgcrypto
```

#### ✅ **3. Get Your Telegram API Credentials**  
You need:  
1. **API ID & API Hash** – Get from [my.telegram.org](https://my.telegram.org/apps).  
2. **Bot Token** – Create a bot via [@BotFather](https://t.me/BotFather) on Telegram.  
3. **Admin ID** – Get your Telegram user ID from [@userinfobot](https://t.me/userinfobot).  

#### ✅ **4. Update the Code with Your Credentials**  
Replace the placeholders in the script with your:  
- `API_ID = YOUR_API_ID`  
- `API_HASH = "YOUR_API_HASH"`  
- `BOT_TOKEN = "YOUR_BOT_TOKEN"`  
- `ADMIN_ID = YOUR_TELEGRAM_ID`  

---

### 🚀 **How to Use the Bot**  

#### **1️⃣ Run the Bot**  
After setting up everything, **run the script**:  
```bash
python bot.py
```
It should display:  
```
Bot is running...
```

#### **2️⃣ Start the Bot**  
Go to Telegram and **start your bot** by sending `/start`. You’ll get a welcome message.

#### **3️⃣ Handle User Messages**  
- Any **message sent by an unknown user** gets forwarded to the **admin**.  
- The **admin replies**, and the message is **sent back to the user** automatically.  
- Users can **send files**, and they get forwarded to the admin.  

#### **4️⃣ Use Inline Commands**  
- `/help` → Shows available options.  
- `📥 Send File` → Allows users to send files.  
- `🛠 Contact Admin` → Provides admin contact options.  

---

### 🎯 **Final Steps**  
- **Run the script** whenever you need to restart the bot.  

