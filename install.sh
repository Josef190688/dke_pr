# Das Ausführen dieser Shell legt ein Virtual Environment für das Projekt an
# und installiert alle nötigen Flask Abhängigkeiten. 

python3 -m venv venv
chmod +x venv/bin/activate
source venv/bin/activate
pip install --upgrade pip
pip install flask
pip install python-dotenv
brew install mysql-client
echo 'export PATH="/usr/local/opt/mysql-client/bin:$PATH"' >> ~/.bash_profile
export PATH="/usr/local/opt/mysql-client/bin:$PATH"
pip install mysqlclient
pip install flask_mysqldb
pip install pipreqs
pipreqs .
pip install -r requirements.txt
echo "Flask App installiert. Neues Terminal starten und 'flask run' eingeben."