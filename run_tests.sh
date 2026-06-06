#!/usr/bin/env bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt --break-system-packages -q

echo "Running BDD tests with Allure formatter..."
behave

echo ""
echo "Allure results saved to: reports/allure-results/"
echo "To view the report, run:"
echo "  allure serve reports/allure-results"
