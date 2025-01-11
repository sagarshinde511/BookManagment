import streamlit as st
import cv2
from PIL import Image
import numpy as np
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# MySQL database connection details
host = "82.180.143.66"
user = "u263681140_students"
passwd = "testStudents@123"
db_name = "u263681140_students"

HOST = "82.180.143.66"
USER = "u263681140_students"
PASSWORD = "testStudents@123"
DATABASE = "u263681140_students"

def update_stock(book_id, new_stock):
    """
    Updates the available stock for a book in the database.

    Args:
        book_id (str): The ID of the book to update.
        new_stock (int): The new stock value to set.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    connection = None
    try:
        # Establish a connection to the database
        connection = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Update the available stock for the book
            update_query = "UPDATE BookInfo SET AvailableStock = %s WHERE id = %s"
            cursor.execute(update_query, (new_stock, book_id))

            # Commit the transaction
            connection.commit()

            # Check if rows were affected
            if cursor.rowcount > 0:
                print("Stock updated successfully.")
                return True
            else:
                print("Book ID not found. No update made.")
                return False

    except Error as e:
        print(f"Error while connecting to the database: {e}")
        return False

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def fetch_data(book_id):
    try:
        # Establish connection to MySQL database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Query to fetch book information
            query = "SELECT BookName, Author, InStock, AvailableStock FROM BookInfo WHERE id = %s"
            cursor.execute(query, (book_id,))
            result = cursor.fetchone()
            return result
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Function to fetch RFidNo from the BookHistory table
def read_qr_code_from_camera(issue_or_return):
    st.title(f"QR Code Scanner - {issue_or_return.capitalize()} Book")

    # Use Streamlit's camera input
    camera_image = st.camera_input(f"Take a picture to scan for QR codes to {issue_or_return}.")

    if camera_image:
        # Convert the captured image to OpenCV format
        image = Image.open(camera_image)
        frame = np.array(image)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Decode QR codes in the frame using OpenCV's QRCodeDetector
        qr_detector = cv2.QRCodeDetector()
        value, points, _ = qr_detector.detectAndDecode(frame)

        if value:
            st.success(f"Book ID is: {value}")
            return value
        else:
            st.warning("No QR Code detected.")
            return None

# Function to fetch RFidNo from the BookHistory table
def fetch_rfid(book_id):
    try:
        # Establish connection to MySQL database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Query to fetch RFidNo from BookHistory where id matches the book_id
            query = "SELECT RFidNo FROM ReadRFID WHERE id = %s"
            cursor.execute(query, (book_id,))
            result = cursor.fetchone()
            return result['RFidNo'] if result else None
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_history(rfid, book_id):
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(
            host="82.180.143.66",
            user="u263681140_students",
            passwd="testStudents@123",
            database="u263681140_students"
        )
        cursor = conn.cursor()

        # Insert data into the BookHistory table
        query = "INSERT INTO BookHistory (RFidNo, BookId) VALUES (%s, %s)"
        cursor.execute(query, (rfid, book_id))
        
        # Commit the transaction
        conn.commit()
        
        # Close the connection
        cursor.close()
        conn.close()
        
        return True  # Success
    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")
        return False  # Failure
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return False


def update_return_status_and_stock(book_id):
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        cursor = conn.cursor()

        # Get the current date
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Update ReturnStatus to 1 and set the ReturnDate where BookId matches and ReturnStatus is NULL
        query = """
            UPDATE BookHistory 
            SET ReturnStatus = 1, ReturnDate = %s 
            WHERE BookId = %s AND ReturnStatus IS NULL
        """
        cursor.execute(query, (current_date, book_id))
        
        # Increase the available stock by 1 for the book
        stock_query = "UPDATE BookInfo SET AvailableStock = AvailableStock + 1 WHERE id = %s"
        cursor.execute(stock_query, (book_id,))

        # Commit the transaction
        conn.commit()

        # Check if rows were affected
        if cursor.rowcount > 0:
            st.success(f"Return status updated, return date set to {current_date}, and available stock increased for Book ID {book_id}.")
        else:
            st.warning("No matching entry found for return or the book is already returned.")

        # Close the connection
        cursor.close()
        conn.close()
        
        return True  # Success
    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")
        return False  # Failure
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return False
def fetch_issued_books():
    """
    Fetches the list of issued books along with student details.
    Joins BookHistory, BookInfo, and BookStudents tables.
    """
    try:
        # Establish connection to MySQL database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Corrected query to join tables and fetch issued book details
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
                    bh.ReturnStatus = 0; -- Only show currently issued books
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
def fetch_rfid_data():
    """
    Fetch the latest RFidNo from the ReadRFID table.
    """
    try:
        # Establish connection to MySQL database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Query to fetch the most recent RFidNo from the ReadRFID table
            query = "SELECT RFidNo FROM ReadRFID ORDER BY id DESC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            return result['RFidNo'] if result else None
    except Error as e:
        st.error(f"Error connecting to the database: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def fetch_book_history(rfid_no):
    """
    Fetch all rows from BookHistory where RFidNo matches the given value.
    """
    try:
        # Establish connection to MySQL database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=passwd,
            database=db_name
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Query to fetch book history for the given RFidNo
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
            return result
    except Error as e:
        st.error(f"Error connecting to the database: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def main():
    # Create tabs for the app
    tab1, tab2, tab3 = st.tabs(["QR Code Scanner", "Book Information Viewer", "Issued Book List"])
    
    tab1, tab2, tab3 = st.tabs(["QR Code Scanner", "Book Information Viewer", "Issued Book List"])
    
    with tab1:
        issue_or_return = st.radio(
            "What action would you like to perform?",
            ["Issue Book", "Return Book", "CheckBooks"]
        )

        # Only call `read_qr_code_from_camera` if "Issue Book" or "Return Book" is selected
        if issue_or_return in ["Issue Book", "Return Book"]:
            book_id = read_qr_code_from_camera(issue_or_return.lower())
            if book_id:
                st.session_state["book_id"] = book_id

        elif issue_or_return == "CheckBooks":
            if st.button("Read RFID"):
                rfid_no = fetch_rfid_data()
                if rfid_no:
                    st.success(f"RFID Number: {rfid_no}")
                    book_history = fetch_book_history(rfid_no)
                    if book_history:
                        st.subheader("Book History")
                        st.table(book_history)
                    else:
                        st.warning("No book history found for the given RFID.")
                else:
                    st.error("No RFID data available in the ReadRFID table.")
    with tab2:
        if "book_id" in st.session_state:
            book_id = st.session_state["book_id"]
            book_info = fetch_data(book_id)
            if book_info:
                st.subheader("Book Information")
                st.write(f"**Book Name:** {book_info['BookName']}")
                st.write(f"**Author:** {book_info['Author']}")
                st.write(f"**In Stock:** {book_info['InStock']}")
                st.write(f"**Available Stock:** {book_info['AvailableStock']}")

                if issue_or_return == "Issue" and int(book_info['AvailableStock']) > 0:
                    # Add a button to assign the book
                    if st.button("Assign Book"):
                        rfid = fetch_rfid(book_id)  # Fetch RFID for the book
                        if rfid and int(rfid) != 0:
                            st.success(f"RFID Number: {rfid}")
                            create_history(rfid, book_id)

                            # Update available stock in the database
                            new_stock = int(book_info['AvailableStock']) - 1
                            update_stock(book_id, new_stock)
                            st.info(f"Book assigned successfully. Updated available stock: {new_stock}")
                        else:
                            st.error("RFID Number is either not assigned or invalid.")
                elif issue_or_return == "Return":
                    # Handle return by updating the return status and increasing stock
                    if st.button("Return Book"):
                        update_return_status_and_stock(book_id)
                else:
                    st.warning("This book is out of stock.")
            else:
                st.error("Book information could not be retrieved. Please check the Book ID.")
        else:
            st.info("Please scan a QR code to view book information.")
    with tab3:
            st.subheader("List of Issued Books")
            issued_books = fetch_issued_books()
            if issued_books:
                # Convert the data into a pandas DataFrame for better display
                import pandas as pd
                df = pd.DataFrame(issued_books)
                st.dataframe(df)
            else:
                st.info("No books are currently issued.")



if __name__ == "__main__":
    main()
