#!/data/data/com.termux/files/usr/bin/bash
echo "Instalando clang si es necesario..."
pkg install -y clang python
echo "Compilando libitsuki.so..."
clang -O3 -fPIC -shared -o libitsuki.so engine.c
echo "Ejecutando Itsuki..."
python itsuki.py
