@echo off
echo Clearing old allure results...
if exist reports\allure-results rmdir /s /q reports\allure-results
mkdir reports\allure-results

echo Running envelope API tests...
python -m behave features/get_envelopes.feature --no-capture -f allure_behave.formatter:AllureFormatter -o reports/allure-results

echo.
echo Done. To view report run:
echo   allure serve reports\allure-results
