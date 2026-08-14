# Enterprise AI Platform

## Setup

```bash
pip install -r requirements.txt
```

## Running the UI

```bash
streamlit run ui/app.py
```

Use the sidebar to navigate to the **Contact Us** page.

## Running the backend API

```bash
uvicorn backend.main:app --reload
```

`GET /contact` returns the contact information shown on the Contact Us page.
