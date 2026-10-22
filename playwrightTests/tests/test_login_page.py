from playwright.sync_api import expect
import pytest, time

def test_ui(page):
    page.goto("https://frontend-medichain.onrender.com/login/patient")
    expect(page.get_by_text("Secure Login")).to_be_visible()
    expect(page.get_by_placeholder("Enter your username or email")).to_be_visible()
    expect(page.get_by_placeholder("Enter your password")).to_be_visible()
    expect(page.get_by_role("button", name="Sign In")).to_be_enabled()
