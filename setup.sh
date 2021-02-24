mkdir -p ~/.streamlit/
echo "[general]
email = "abhishek.dobliyal1512@gmail.com"
" > ~/.streamlit/credentials.toml
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
