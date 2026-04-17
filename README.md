# 🛡️ WebSentinal

**WebSentinal** is a web crawler focused on crawling web applications and extracting potential attack surfaces such as links, endpoints, and input vectors.

It is built to assist in the **reconnaissance phase** of security testing by mapping out the structure of a target application.

---

## 🚀 Features

### 🔍 Crawling Engine
WebSentinal performs deep crawling to extract:

- **Links**  
- **Resources**  
- **Images**
- **Scripts**
- **Input fields**
- **Parameters**
- **Forms**

### 🎯 Endpoint Discovery

Identifies different types of endpoints:

- **Static Endpoints**
- **Dynamic Endpoints**
- **Hidden Endpoints**
- **Contextual Endpoints**   

---

## 🛠️ Installation

<b>1. Clone repo</b>
```bash
git clone https://github.com/Mr-Sudheer/Websentinal.git
```
```bash
cd Websentinal
```
<b>2. Install dependencies</b>
```bash
pip install -r requirements.txt
```
```bash
playwright install
```

<b>3. Run the tool</b>
```bash
python Websentinal.py
```

---

## ⚠️ Limitations

- Some websites return **403 Forbidden**, which prevents effective crawling  
- No support for **parallel crawling**  
- Limited handling of advanced anti-bot protections