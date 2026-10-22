from playwright.sync_api import expect
import pytest, time

@pytest.fixture
def home_page(page):
    page.goto("https://frontend-medichain.onrender.com/")
    return page

def test_ui(home_page):
    expect(home_page.get_by_text("Patient Login")).to_be_visible()
    expect(home_page.get_by_text("Doctor Login")).to_be_visible()
    expect(home_page.get_by_text("Lab Staff Login")).to_be_visible()
    expect(home_page.get_by_role("button", name="Login as Patient")).to_be_enabled()
    expect(home_page.get_by_role("button", name="Login as Doctor")).to_be_enabled()
    expect(home_page.get_by_role("button", name="Login as Lab")).to_be_enabled()
    expect(home_page.locator("#chatbot-toggler")).to_be_enabled()


def test_chatbot_window(home_page):
    #Verify open chatbot window when clicking the toggle button
    home_page.goto("https://frontend-medichain.onrender.com/")
    home_page.locator("#chatbot-toggler").click()
    expect(home_page.locator(".chatbot-popup")).to_be_visible()
    expect(home_page.locator(".logo-text")).to_have_text("Chatbot")
    expect(home_page.locator(".chat-body .message.bot-message .message-text")).to_have_text(
        "Hey there, How can I help you today?")
    home_page.get_by_placeholder("Message...").fill("Hello")
    home_page.keyboard.press("Enter")
    expect(home_page.locator(".chat-body .message.user-message .message-text")).to_have_text("Hello")
    expect(home_page.locator(".chat-body .message.bot-message:last-child")).to_have_text("Thinking...")
    time.sleep(2)
    expect(home_page.locator(".chat-body .message.bot-message:last-child")).not_to_have_text("Thinking...")

    #Verify close chatbot window when clicking the toggle button
    home_page.locator("#chatbot-toggler").click()
    expect(home_page.locator(".chatbot-popup")).not_to_be_visible()
    time.sleep(2)

def test_navigation(home_page):
    #Verify navigation to patient login page
    home_page.get_by_role("button", name="Login as Patient").click()
    expect(home_page).to_have_url("https://frontend-medichain.onrender.com/login/patient")
    time.sleep(2)
    home_page.go_back()

    #Verify navigation to doctor login page
    home_page.get_by_role("button", name="Login as Doctor").click()
    expect(home_page).to_have_url("https://frontend-medichain.onrender.com/login/doctor")
    time.sleep(2)
    home_page.go_back()

    #Verify navigation to lab staff login page
    home_page.get_by_role("button", name="Login as Lab").click()
    expect(home_page).to_have_url("https://frontend-medichain.onrender.com/login/lab")
    time.sleep(2)
    home_page.go_back()




