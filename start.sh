#!/bin/bash
# HRM System - Start Script
cd "$(dirname "$0")"

echo "================================="
echo "  HRM System - Khoi dong server"
echo "================================="
echo ""
echo "URL:      http://127.0.0.1:8000"
echo "Admin:    username=admin / password=admin123"
echo "HR:       username=hr / password=hr123456"
echo ""
echo "Nhan Ctrl+C de dung server."
echo ""

./venv/bin/python manage.py runserver
