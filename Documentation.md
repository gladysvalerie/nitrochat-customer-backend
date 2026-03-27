## Running the Project

### User-Frontend

- Navigate to the project directory
- Open terminal and run the code snippet below. 
- The code snippet below will run the react project
- You can paste the default address given for the Vite server on your web browser to see the project

```
npm install
npm run dev
```

### User-Backend

- Firstly, make sure you have [[uv]] install. 

	```
	pip install uv
	```

- Alternatively, if the above line of code does not work, you can try this line of code below

```
	powershell -ExecutionPolicy Bypass -c "pip install uv"
```

- After installing [[uv]], we need to create the virtual environment properly based on the `pyproject.toml` file.  As such, run this line of command below, which will create the virtual environment properly. 

```
uv sync
```

- Next we want to set up the project so that it has access to the API keys necessary. To do this, we need a `.env` file. In the same project directory, please create a file with the name `.env`
- Afterwards, open the `.env` file and please paste the following code in, alongside your API keys

```
ADMIN_BASE_URL= "http://localhost:8001/api/admin"
ADMIN_INTERNAL_KEY= "nitrochat-rag-admin"
```

- `ADMIN_BASE_URL` is used to make POST request to the server, uploading a question and creating a new thread
- `ADMIN_INTERNAL_KEY` is passed along through the headers, adding extra information and acting as a security handshake, verifying the internal request is authorized
- If you run `uv run uvicorn main:app --reload` and pasted in `http://127.0.0.1:8000/docs#/` to your web browser, the below image should show up, showing that the backend server for the user is running

![[Pasted image 20260327094643.png|697]]


### Admin-Frontend

- Navigate to the project directory
- Open terminal and run the code snippet below. 
- The code snippet below will run the react project
- You can paste the default address given for the Vite server on your web browser to see the project

```
npm install
npm run dev
```

### Admin-Backend

- Since we have already installed [[uv]], we do no need to install anything else, just run the following code snippet below, which create the correct environment in the form of a `.venv` file within the project

```
uv sync
```

- Create the `.env` file within the same directory to put your keys.
- Paste the code below to your `.env` file

```
MONGO_URI=mongodb://localhost:27017
DB_NAME=nitrochat_admin
DB_TEMPLATE_COLLECTION=templates
DB_KBS_COLLECTION=kbs
DB_DOCS_COLLECTION=docs
CHROMA_PATH=./db/vector_database/storage
CHROMA_FAQ_COLLECTION=faq
# GEMINI_API_KEY=AIzaSyC2o4iwjXR2NMSDAf6kuC7lSPAKNq1elEM
# GEMINI_API_KEY=AIzaSyB86ZNes-uUNJf7lK6bqm1OMpxNuz22Qec rawstone's
GEMINI_API_KEY=AIzaSyDDl8MRXDXrL94Mvjb-XGpp7N522zciMw8
OPENAI_API_KEY=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
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
GEMINI_CHAT_MODEL=gemini-2.5-flash
OPENAI_CHAT_MODEL=gpt-4.1-2025-04-14
LANGSMITH_TRACING="true"
LANGSMITH_API_KEY=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
INTERNAL_KEY="nitrochat-rag-admin"
```

- Since we are using MongoDB as a database, we need to start install and start it up.
- To install, we run powershell as an admin and run the code below

```
winget install MongoDB.Server
```

- Afterwards, we can run it with the code below

```
net start MongoDB
```

- Afterwards, you can run `uv run uvicorn main:app --reload --port 8001` to start the fastAPI server on a different one compared to the backend server for the User side
- You should have something similar to the image below

![[Pasted image 20260327105041.png]]

### Verifying it Works

- To verify it works, upload a CSV file according to the template given
- To do so, go the fastAPI docs `http://127.0.0.1:8001/docs#/` and try it out using the Upload FaQ function.
- Press on it, press 'Try it Out', upload a CSV, and then press execute
-
![[Pasted image 20260327105241.png]]

- Having a code 200 verifies that your implementation is working properly
- You can then move to the user-frontend part, and prompt a question from a user based on the CSV file you uploaded.


![[Pasted image 20260327105341.png]]

- If you have something like above, congratulations! You have set up the NitroChat project properly