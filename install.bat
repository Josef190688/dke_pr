@echo off
rem Das Ausführen dieses Batch-Files legt ein Virtual Environment für das Projekt an
rem und installiert alle nötigen Flask Abhängigkeiten. 

@echo on
python -m venv venv
icacls venv\Scripts\python.exe /grant %USERNAME%:(F)
call venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install flask
python -m pip install python-dotenv
python -m pip install mysqlclient
python -m pip install flask_mysqldb
python -m pip install pipreqs
python -m pipreqs .
python -m pip install -r requirements.txt
echo "Flask App installiert. Neues Terminal starten und 'flask run' eingeben."