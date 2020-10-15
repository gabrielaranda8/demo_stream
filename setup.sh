mkdir -p ~/.streamlit/

echo "\
    [general]\n\
    email = \"gabrielaranda8@gmail.com\"\n\
    " > ~/.streamlit/credentials.toml

echo "\
    [server]\n\
    headless = true\n\
    enableCORS = false
    port = $PORT\n\
    " > ~/.streamlit/config.toml