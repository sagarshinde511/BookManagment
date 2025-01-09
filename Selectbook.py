import streamlit as st
import cv2
from PIL import Image
import numpy as np
import mysql.connector
from mysql.connector import Error

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

# Main function
def main():
    # Create tabs for the app
    tab1, tab2 = st.tabs(["QR Code Scanner", "Book Information Viewer"])

    with tab1:
        issue_or_return = st.radio(
            "What action would you like to perform?",
            ["Issue", "Return"]
        )

        book_id = read_qr_code_from_camera(issue_or_return.lower())
        if book_id:
            st.session_state["book_id"] = book_id

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

                if int(book_info['AvailableStock']) > 0 and issue_or_return == "Issue":
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
                    # Logic for handling return (you can add return-specific behavior here)
                    st.info("Return functionality is being handled here.")
                else:
                    st.warning("This book is out of stock.")
            else:
                st.error("Book information could not be retrieved. Please check the Book ID.")
        else:
            st.info("Please scan a QR code to view book information.")

if __name__ == "__main__":
    main()
