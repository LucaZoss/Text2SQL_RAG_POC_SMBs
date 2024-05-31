This is the project structure of the RAG system. You can add directories and/or modify them as you want. As of now is just a reference


rag_datalake/
│
├── loaders.py  --Functions to load different data formats
│
├── ui/
│   ├── __init__.py
│   ├── upload_interface.py  --Logic for users to upload files
│   ├── auth.py  --Logic for authenticating users
│   ├── static/
│   │   └── scripts.js  --Registration/Authentication with Apple/Google
│   └── templates/  
│       ├── index.html
│       ├── login.html
│       ├── query.html
│       └── register.html
│
├── rag_system/
│   ├── __init__.py
│   └── llama_index_integration.py -- Logic to add data lo Llama Index
│
├── config/
│   ├── __init__.py
│   └── settings.py --Settings definition file
│
├── main.py
└── requirements.txt  --Libraries required to install prior to executing: "pip install -r requirements"
