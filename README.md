# 🛡️ WebSentinal

**WebSentinal** is a web vulnerability scanner focused on crawling web applications and extracting potential attack surfaces such as links, endpoints, and input vectors.

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
## 🧪 Planned Features

### ⚠️ Vulnerability Detection
Basic vulnerability checks will be added:

- **SQL Injection (SQLi)**
- **Cross-Site Scripting (XSS)**
- **Insecure Direct Object References (IDOR)**

### 🔐 Sensitive Data Exposure Detection

Detection of exposed:

- API keys  
- Tokens  
- Secrets  

---

## ⚠️ Limitations

- Some websites return **403 Forbidden**, which prevents effective crawling  
- No support for **parallel crawling**  
- Limited handling of advanced anti-bot protections  

---

## 🛠️ Installation

```bash
git clone https://github.com/Mr-Sudheer/Websentinal.git
```
```bash
Websentinal.py
```
