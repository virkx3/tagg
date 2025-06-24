import time, json, requests, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ===== CONFIG =====
USERNAME = "kiransharma0580"
PASSWORD = "Virksaab"
TARGET_PROFILE = "iamvirk05"

SMMWIZ_API_KEY = "ccdc7bc9cda18e72b22ed9ba9d13c872"
SERVICE_ID = "13826"
SMMWIZ_URL = "https://smmwiz.com/api/v2"

CHECK_INTERVAL = 60  # seconds

# ===== LOADERS =====
def load_processed():
    try:
        with open("processed.json") as f:
            return set(json.load(f))
    except:
        return set()

def save_processed(processed):
    with open("processed.json", "w") as f:
        json.dump(list(processed), f)

def log_event(text):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {text}\n")

def log_order(shortcode, url, order_id):
    try:
        with open("orders.json") as f:
            orders = json.load(f)
    except:
        orders = []

    orders.append({
        "shortcode": shortcode,
        "url": url,
        "order_id": order_id,
        "timestamp": datetime.datetime.now().isoformat()
    })

    with open("orders.json", "w") as f:
        json.dump(orders, f, indent=2)

# ===== SETUP SELENIUM DRIVER =====
def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver

# ===== LOGIN TO INSTAGRAM =====
def login(driver):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[text()='Only allow essential cookies']")
        cookie_btn.click()
        time.sleep(2)
    except:
        pass

    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)
    password_input.submit()
    time.sleep(7)

    try:
        not_now_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
        not_now_btn.click()
        time.sleep(2)
    except:
        pass

    try:
        not_now_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
        not_now_btn.click()
        time.sleep(2)
    except:
        pass

# ===== GET LAST TAGGED POST URL =====
def get_last_tagged_post(driver):
    driver.get(f"https://www.instagram.com/{TARGET_PROFILE}/tagged/")
    time.sleep(5)
    links = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")]')
    if links:
        return links[0].get_attribute("href")
    return None

# ===== SEND SMMWIZ ORDER =====
def send_order(insta_url):
    payload = {
        "key": SMMWIZ_API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": insta_url,
        "quantity": 20
    }
    try:
        res = requests.post(SMMWIZ_URL, data=payload).json()
        return res.get("order")
    except Exception as e:
        log_event(f"❌ SMMWiz API error: {e}")
        return None

# ===== MAIN LOOP WITH AUTO RESTART =====
def main():
    processed = load_processed()

    while True:
        driver = None
        try:
            driver = get_driver()
            login(driver)

            print("🔍 Checking latest tagged post...")
            link = get_last_tagged_post(driver)

            if link:
                shortcode = link.rstrip('/').split('/')[-1]
                if shortcode not in processed:
                    log_event(f"🆕 New tagged post: {link}")
                    order_id = send_order(link)
                    if order_id:
                        print(f"✅ Ordered likes! Order ID: {order_id}")
                        log_event(f"✅ Order placed: {order_id} for {link}")
                        log_order(shortcode, link, order_id)
                        processed.add(shortcode)
                        save_processed(processed)
                    else:
                        print("⚠ Order failed")
                        log_event(f"⚠ Order failed for: {link}")
                else:
                    print("✔ Already processed.")
                    log_event(f"Skipped: {link} (already ordered)")
            else:
                print("❌ No tagged post found.")
                log_event("No tagged post found.")

        except Exception as e:
            print("❌ ERROR:", e)
            log_event(f"❌ Exception: {e}")

        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
