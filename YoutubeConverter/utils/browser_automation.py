import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class BrowserAutomation:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = None

    def _setup_driver(self):
        """Setup Chrome driver in incognito mode"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--incognito")
            # Remove automation flags
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            # Add user agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
            # Disable blink features that can be used for bot detection
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            # Enable logging
            chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute CDP commands to prevent detection
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            })
            
            return True
        except Exception as e:
            self.logger.error(f"Error setting up Chrome driver: {e}")
            return False

    def _get_cookies_netscape_format(self) -> str:
        """Convert Selenium cookies to Netscape format"""
        cookies = self.driver.get_cookies()
        netscape_cookies = "# Netscape HTTP Cookie File\n"
        netscape_cookies += "# https://curl.haxx.se/rfc/cookie_spec.html\n"
        netscape_cookies += "# This is a generated file!  Do not edit.\n\n"
        
        for cookie in cookies:
            domain = cookie['domain']
            if not domain.startswith('.'):
                domain = '.' + domain
            
            secure = "TRUE" if cookie.get('secure', False) else "FALSE"
            http_only = "TRUE" if cookie.get('httpOnly', False) else "FALSE"
            expires = str(int(cookie.get('expiry', int(time.time() + 3600*24*365))))
            
            netscape_cookies += (
                f"{domain}\t"
                f"{http_only}\t"
                f"{cookie.get('path', '/')}\t"
                f"{secure}\t"
                f"{expires}\t"
                f"{cookie['name']}\t"
                f"{cookie['value']}\n"
            )
        
        return netscape_cookies

    def _get_po_token(self) -> str:
        """Get visitor data from YouTube"""
        try:
            # Go to YouTube homepage
            self.driver.get('https://www.youtube.com')
            time.sleep(3)
            
            # Get visitor data using a simpler JavaScript approach
            visitor_data = self.driver.execute_script("""
                try {
                    // Try to get from ytcfg global object
                    if (typeof ytcfg !== 'undefined' && ytcfg.data_) {
                        return ytcfg.data_.VISITOR_DATA;
                    }
                    
                    // Try to get from meta tag
                    var visitorMeta = document.querySelector('meta[name="visitor-data"]');
                    if (visitorMeta) {
                        return visitorMeta.getAttribute('content');
                    }
                    
                    // Try to get from initial data
                    var ytInitialData = window.ytInitialData;
                    if (ytInitialData && ytInitialData.responseContext) {
                        return ytInitialData.responseContext.visitorData;
                    }
                    
                    return null;
                } catch (e) {
                    return null;
                }
            """)
            
            if not visitor_data:
                # Try one more time with a video page
                self.driver.get('https://www.youtube.com/watch?v=jNQXAC9IVRw')
                time.sleep(3)
                visitor_data = self.driver.execute_script("""
                    try {
                        return ytInitialData?.responseContext?.visitorData || null;
                    } catch (e) {
                        return null;
                    }
                """)
            
            return visitor_data
            
        except Exception as e:
            self.logger.error(f"Error getting visitor data: {e}")
            return None

    def get_youtube_auth(self) -> tuple[str, str]:
        """Get YouTube cookies and visitor data"""
        try:
            if not self._setup_driver():
                raise Exception("Failed to setup Chrome driver")

            # Go to YouTube directly
            self.driver.get('https://www.youtube.com')
            time.sleep(2)
            
            # Click sign in button if present
            try:
                sign_in_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'accounts.google.com/ServiceLogin')]"))
                )
                sign_in_button.click()
            except:
                self.logger.info("No sign in button found, might be already at login page")

            # Wait for successful login (look for avatar button)
            try:
                WebDriverWait(self.driver, 300).until(
                    EC.presence_of_element_located((By.ID, "avatar-btn"))
                )
            except TimeoutException:
                raise Exception("Login timeout - please try again")

            # Visit a few pages to ensure cookies are properly set
            pages = [
                'https://www.youtube.com',
                'https://www.youtube.com/feed/trending',
                'https://www.youtube.com/feed/subscriptions'
            ]
            
            for page in pages:
                self.driver.get(page)
                time.sleep(2)

            # Get cookies after successful login
            cookies = self._get_cookies_netscape_format()

            # Get visitor data
            visitor_data = self._get_po_token()

            if not visitor_data:
                self.logger.warning("Could not get visitor data")

            return cookies, visitor_data

        except Exception as e:
            self.logger.error(f"Error in get_youtube_auth: {e}")
            return None, None
        finally:
            if self.driver:
                self.driver.quit()

# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("Starting YouTube authentication process...")
    print("A Chrome window will open for you to log in.")
    print("Please wait...")
    
    automation = BrowserAutomation()
    cookies, visitor_data = automation.get_youtube_auth()
    
    print("\nResults:")
    print(f"Cookies obtained: {'Yes' if cookies else 'No'}")
    print(f"Visitor Data obtained: {'Yes' if visitor_data else 'No'}")
    
    if cookies:
        print("\nFirst few lines of cookies:")
        print("\n".join(cookies.split("\n")[:5]))
    
    if visitor_data:
        print("\nVisitor Data:")
        print(visitor_data)
    
    input("\nPress Enter to exit...")
