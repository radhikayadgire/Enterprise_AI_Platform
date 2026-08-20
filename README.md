# Enterprise AI Platform

A small multi-agent platform: a FastAPI backend routes HR, search, and email
requests through specialist agents, and a Streamlit UI exposes those
capabilities to end users.

## Running the backend

```
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

## Running the UI

```
streamlit run ui/app.py
```

The UI has three pages: **Home**, **Contact Us**, and **User Details** (a form
where a visitor submits their name, email, phone number, and an optional
message; the submission is posted to `POST /api/user` on the backend).

## Running the tests

```
pytest
```
