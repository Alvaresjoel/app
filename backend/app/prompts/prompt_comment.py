from datetime import datetime
from langchain.prompts import ChatPromptTemplate

today = datetime.now().date()

query_parser_template = ChatPromptTemplate([
    ("system", 
     "You are a query parser. Convert the user question into a structured JSON object with these keys: \
      - start_date (ISO format, expand relative dates like 'last 6 months') \
      - end_date (ISO format) \
      Today's date is {today}."),
    ("human", "{question}")
])
