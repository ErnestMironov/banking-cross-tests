# Author: Ягунов Денис Алексеевич
# Automated tests for SECOND.md test cases

import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pytest


class BankServiceBoundaryTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.base_url = "http://localhost:8000"
        cls.wait = WebDriverWait(cls.driver, 10)
    
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
    
    def test_06_boundary_balance_values(self):
        try:
            # Тест с нулевым балансом
            self.driver.get(f"{self.base_url}/?balance=0&reserved=0")
            time.sleep(2)
            
            balance_element = self.driver.find_element(By.XPATH, "//span[@id='rub-sum']")
            self.assertEqual(balance_element.text, "0")
            
            # Тест с минимальным балансом
            self.driver.get(f"{self.base_url}/?balance=1&reserved=0")
            time.sleep(2)
            
            balance_element = self.driver.find_element(By.XPATH, "//span[@id='rub-sum']")
            self.assertEqual(balance_element.text, "1")
            
            # Тест с большим балансом
            self.driver.get(f"{self.base_url}/?balance=999999&reserved=0")
            time.sleep(2)
            
            balance_element = self.driver.find_element(By.XPATH, "//span[@id='rub-sum']")
            self.assertEqual(balance_element.text, "999'999")
            
        except Exception as e:
            self.fail(f"Boundary balance values test failed: {str(e)}")
    
    @pytest.mark.xfail(reason="Известный баг: валидация номера карты не фильтрует лишние символы")
    def test_07_card_number_validation_boundary_cases(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=30000&reserved=20001")
            time.sleep(2)
            
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            
            # Тест на превышение лимита символов
            card_input.clear()
            card_input.send_keys("12345678901234567890")
            time.sleep(1)
            
            current_value = card_input.get_attribute("value")
            self.assertTrue(len(current_value.replace(" ", "")) <= 16)
            
            # Тест на буквы в номере карты
            card_input.clear()
            card_input.send_keys("1234abcd56789012")
            time.sleep(1)
            
            # Проверяем что буквы были отфильтрованы
            current_value = card_input.get_attribute("value")
            self.assertNotRegex(current_value, r'[a-zA-Z]')
            
        except Exception as e:
            self.fail(f"Card number boundary validation test failed: {str(e)}")
    
    @pytest.mark.xfail(reason="Известный баг: комиссия округляется неверно")
    def test_08_commission_calculation_rounding_down(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=10000&reserved=0")
            time.sleep(2)
            
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            card_input.clear()
            card_input.send_keys("1234567890123456")
            
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            
            # Тест округления вниз для 55 -> комиссия должна быть 5, а не 5.5
            amount_input.clear()
            amount_input.send_keys("55")
            time.sleep(2)
            
            commission_element = self.driver.find_element(By.XPATH, "//span[@id='comission']")
            self.assertEqual(commission_element.text, "5")
            
            # Тест округления вниз для 199 -> комиссия должна быть 19, а не 19.9
            amount_input.clear()
            amount_input.send_keys("199")
            time.sleep(2)
            
            commission_element = self.driver.find_element(By.XPATH, "//span[@id='comission']")
            self.assertEqual(commission_element.text, "19")
            
        except Exception as e:
            self.fail(f"Commission rounding test failed: {str(e)}")
    
    @pytest.mark.xfail(reason="Известный баг: NaN вместо 0 при невалидных параметрах URL")
    def test_09_bug_003_nan_display_with_invalid_url_params(self):
        try:
            # Тест с некорректными параметрами - должен показывать NaN (это баг)
            self.driver.get(f"{self.base_url}/?balance=abc&reserved=xyz")
            time.sleep(2)
            
            balance_element = self.driver.find_element(By.XPATH, "//span[@id='rub-sum']")
            
            # Ожидаем "0", но приложение показывает "NaN" - это баг
            self.assertEqual(balance_element.text, "0", f"Invalid URL params should show '0', but got: {balance_element.text}")
            
        except Exception as e:
            self.fail(f"URL NaN validation test failed: {str(e)}")
    
    @pytest.mark.xfail(reason="Известный баг: кнопка перевода не блокируется для отрицательных сумм")
    def test_10_bug_004_negative_amounts_acceptance(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=10000&reserved=0")
            time.sleep(2)
            
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            card_input.clear()
            card_input.send_keys("1234567890123456")
            
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            
            # Вводим отрицательную сумму
            amount_input.clear()
            amount_input.send_keys("-100")
            time.sleep(2)
            
            # Проверяем что кнопка НЕ должна быть активна
            transfer_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Перевести')]")
            
            if len(transfer_buttons) > 0:
                button = transfer_buttons[0]
                self.assertFalse(button.is_enabled(), "Transfer button should be disabled for negative amounts")
            else:
                self.fail("Transfer button should exist but be disabled for negative amounts")
            
        except Exception as e:
            self.fail(f"Negative amounts test failed: {str(e)}")


if __name__ == "__main__":
    unittest.main() 