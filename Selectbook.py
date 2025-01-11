import streamlit as st
import cv2
from PIL import Image
import numpy as np
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import pandas as pd

# MySQL database connection details
host = "82.180.143.66"
user = "u263681140_students"
passwd = "testStudents@123"
db_name = "u263681140_students"

# Functions
def fetch_rfid_data():
    """
    Fetch the latest RFidNo from the ReadRFID table.
    """
    try:
        connection = mysql.connector.connect(
            host=host, user=user, password=passwd, database=db_name
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT RFidNo FROM ReadRFID ORDER BY id DESC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            return result['RFidNo'] if result else None
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def fetch_book_history_grouped(rfid_no):
    """
    Fetch and group book history by ReturnStatus for a given RFidNo.
    """
    try:
        connection = mysql.connector.connect(
            host=host, user=user, password=passwd, database=db_name
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT 
                    bh.BookId, 
                    bi.BookName, 
                    bi.Author, 
                    bh.date AS IssueDate, 
                    bh.ReturnStatus, 
                    bh.ReturnDate 
                FROM 
                    BookHistory bh
                INNER JOIN 
                    BookInfo bi ON bh.BookId = bi.id
                WHERE 
                    bh.RFidNo = %s
            """
            cursor.execute(query, (rfid_no,))
            result = cursor.fetchall()

            # Separate results into two groups based on ReturnStatus
            current_issued_books = [row for row in result if row['ReturnStatus'] == 0]
            past_issued_books = [row for row in result if row['ReturnStatus'] == 1]

            return {
                "current_issued_books": current_issued_books,
                "past_issued_books": past_issued_books,
            }
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def fetch_issued_books():
    """
    Fetches the list of issued books along with student details.
    Joins BookHistory, BookInfo, and BookStudents tables.
    """
    try:
        connection = mysql.connector.connect(
            host=host, user=user, password=passwd, database=db_name
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT 
                    bs.Name AS StudentName,
                    bs.RFidNo,
                    bs.Branch,
                    bs.Year,
                    bi.BookName,
                    bi.Author,
                    bh.date
                FROM 
                    BookHistory bh
                INNER JOIN 
                    BookInfo bi ON bh.BookId = bi.id
                INNER JOIN 
                    BookStudents bs ON bh.RFidNo = bs.RFidNo
                WHERE 
                    bh.ReturnStatus = 0;
            """
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Error as e:
        st.error(f"Error connecting to the database: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Streamlit App
def main():
    # Create tabs for the app
    tab1, tab2 = st.tabs(["CheckBooks", "Issued Book List"])

    with tab1:
        if st.button("Read RFID"):
            rfid_no = fetch_rfid_data()
            if rfid_no:
                st.success(f"RFID Number: {rfid_no}")
                grouped_history = fetch_book_history_grouped(rfid_no)

                if grouped_history:
                    # Display Currently Issued Books
                    st.subheader("Currently Issued Books")
                    if grouped_history["current_issued_books"]:
                        st.table(grouped_history["current_issued_books"])
                    else:
                        st.info("No books are currently issued.")

                    # Display Past Issued Books
                    st.subheader("Past Issued Books")
                    if grouped_history["past_issued_books"]:
                        st.table(grouped_history["past_issued_books"])
                    else:
                        st.info("No past issued books found.")
                else:
                    st.warning("No book history found for the given RFID.")
            else:
                st.error("No RFID data available in the ReadRFID table.")

    with tab2:
        st.subheader("List of Issued Books")
        issued_books = fetch_issued_books()
        if issued_books:
            df = pd.DataFrame(issued_books)
            st.dataframe(df)
        else:
            st.info("No books are currently issued.")

if __name__ == "__main__":
    main()
