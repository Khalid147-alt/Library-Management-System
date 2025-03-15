import streamlit as st
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px
import uuid
import io

# Set page configuration
st.set_page_config(
    page_title="Personal Library Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional UI with hover effects
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #2c3e50;
    }
    
    /* Book card styling with hover effects */
    .book-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-left: 4px solid #3498db;
    }
    
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        background-color: #f5faff;
    }
    
    /* Book title and author */
    .book-title {
        font-weight: 600;
        font-size: 18px;
        color: #2c3e50;
    }
    
    .book-author {
        font-style: italic;
        color: #7f8c8d;
        margin-bottom: 5px;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 3px 6px rgba(0,0,0,0.2);
        background-color: #2980b9;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #ecf0f1;
        padding-top: 20px;
    }
    
    /* Navigation buttons */
    .stButton>button[use_container_width="True"] {
        justify-content: flex-start;
        padding: 10px 15px;
        background-color: transparent;
        color: #2c3e50;
        border: none;
    }
    
    .stButton>button[use_container_width="True"]:hover {
        background-color: #dfe6e9;
        transform: none;
        box-shadow: none;
    }
    
    /* Active navigation item */
    .active-nav {
        background-color: #3498db !important;
        color: white !important;
        border-radius: 5px;
    }
    
    /* Dashboard cards */
    .dashboard-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .dashboard-card:hover {
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# File to store the library
filename = "library.json"

# Function to load the library from file
def load_library():
    """Load the library from a JSON file, handling various data formats and errors."""
    default_structure = {
        'books': [],
        'collections': {},
        'reading_list': []
    }
    
    if not os.path.exists(filename):
        return default_structure
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Handle case where data is neither list nor dict
        if not isinstance(data, (list, dict)):
            st.error(f"Invalid library format: expected list or dict, got {type(data)}. Starting with empty library.")
            return default_structure
        
        # Handle old format (just a list of books)
        if isinstance(data, list):
            valid_books = []
            for book in data:
                if isinstance(book, dict):
                    if 'id' not in book:
                        book['id'] = str(uuid.uuid4())
                    valid_books.append(book)
                else:
                    st.warning(f"Skipping invalid book entry: {book}")
            return {
                'books': valid_books,
                'collections': {},
                'reading_list': []
            }
        
        # Handle proper dictionary format
        elif isinstance(data, dict):
            if 'books' in data and isinstance(data['books'], list):
                valid_books = []
                for book in data['books']:
                    if isinstance(book, dict):
                        if 'id' not in book:
                            book['id'] = str(uuid.uuid4())
                        valid_books.append(book)
                    else:
                        st.warning(f"Skipping invalid book entry: {book}")
                data['books'] = valid_books
            else:
                data['books'] = []
            
            if 'collections' not in data or not isinstance(data['collections'], dict):
                data['collections'] = {}
            if 'reading_list' not in data or not isinstance(data['reading_list'], list):
                data['reading_list'] = []
            
            return data
    
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON format: {str(e)}. Starting with empty library.")
        return default_structure
    except Exception as e:
        st.error(f"Unexpected error loading library: {str(e)}. Starting with empty library.")
        return default_structure

# Function to save the library to file
def save_library(data):
    """Save the library to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        st.error(f"Error saving library: {str(e)}")
        return False

# Function to backup the library
def backup_library():
    """Create a backup of the current library state."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"library_backup_{timestamp}.json"
    try:
        full_data = {
            'books': st.session_state.library,
            'collections': st.session_state.get('collections', {}),
            'reading_list': st.session_state.get('reading_list', [])
        }
        with open(backup_filename, 'w') as f:
            json.dump(full_data, f)
        return backup_filename
    except Exception as e:
        st.error(f"Error creating backup: {str(e)}")
        return None

# Function to restore from backup
def restore_from_backup(backup_file):
    """Restore library from a backup file."""
    try:
        with open(backup_file, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            st.session_state.library = data
            st.session_state.collections = {}
            st.session_state.reading_list = []
        elif isinstance(data, dict):
            st.session_state.library = data.get('books', [])
            st.session_state.collections = data.get('collections', {})
            st.session_state.reading_list = data.get('reading_list', [])
        else:
            raise ValueError("Invalid backup format")
        save_library({
            'books': st.session_state.library,
            'collections': st.session_state.collections,
            'reading_list': st.session_state.reading_list
        })
        return True
    except Exception as e:
        st.error(f"Error restoring from backup: {str(e)}")
        return False

# Initialize session state
if 'library' not in st.session_state:
    data = load_library()
    st.session_state.library = data['books']
    st.session_state.collections = data['collections']
    st.session_state.reading_list = data['reading_list']
if 'nav_option' not in st.session_state:
    st.session_state.nav_option = "Dashboard"

# App header
st.title("📚 Personal Library Manager")
st.write("Organize and manage your book collection with style and ease.")

# Sidebar navigation with emoji icons
with st.sidebar:
    st.image("https://via.placeholder.com/150x150.png?text=Library", width=150)
    st.subheader("Navigation")
    
    nav_options = [
        ("Dashboard", "🏠"),
        ("Add Book", "➕"),
        ("Browse Books", "📚"),
        ("Search", "🔍"),
        ("Collections", "📂"),
        ("Reading List", "📋"),
        ("Statistics", "📊"),
        ("Settings", "⚙️")
    ]
    
    for i, (name, icon) in enumerate(nav_options):
        # Apply active class manually via key and styling
        if st.button(f"{icon} {name}", key=f"nav_{i}", use_container_width=True):
            st.session_state.nav_option = name
            st.rerun()
        # Highlight active navigation item
        if st.session_state.nav_option == name:
            st.markdown(f"""
            <style>
            #nav_{i} button {{
                background-color: #3498db !important;
                color: white !important;
                border-radius: 5px;
            }}
            </style>
            """, unsafe_allow_html=True)

option = st.session_state.nav_option

# Dashboard Section
if option == "Dashboard":
    st.header("🏠 Dashboard")
    
    total_books = len(st.session_state.library)
    num_read = sum(1 for book in st.session_state.library if book.get('read', False))
    genres = set(book.get('genre', '').lower() for book in st.session_state.library if book.get('genre'))
    authors = set(book.get('author', '').lower() for book in st.session_state.library if book.get('author'))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="dashboard-card">
            <h3>Total Books</h3>
            <h2>{total_books}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="dashboard-card">
            <h3>Books Read</h3>
            <h2>{num_read}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="dashboard-card">
            <h3>Genres</h3>
            <h2>{len(genres)}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="dashboard-card">
            <h3>Authors</h3>
            <h2>{len(authors)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("Recent Additions")
    if st.session_state.library:
        recent_books = sorted(st.session_state.library, key=lambda x: x.get('date_added', '0'), reverse=True)[:5]
        for book in recent_books:
            st.markdown(f"""
            <div class="book-card">
                <div class="book-title">{book['title']}</div>
                <div class="book-author">{book['author']}</div>
                <div>Genre: {book.get('genre', 'N/A')} | {'Read' if book.get('read', False) else 'Unread'}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No books added yet.")

    if total_books > 0:
        st.subheader("Reading Progress")
        fig = px.pie(
            values=[num_read, total_books - num_read],
            names=["Read", "Unread"],
            hole=0.5,
            color_discrete_sequence=["#2ecc71", "#e0e0e0"]
        )
        fig.update_layout(
            annotations=[dict(text=f"{(num_read/total_books*100):.1f}%", x=0.5, y=0.5, font_size=20, showarrow=False)],
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True)

# Add Book Section
elif option == "Add Book":
    st.header("➕ Add Book")
    with st.form(key="add_book_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title", placeholder="Enter book title")
            author = st.text_input("Author", placeholder="Enter author name")
            year = st.number_input("Year", min_value=0, max_value=datetime.now().year, step=1)
        with col2:
            genre = st.text_input("Genre", placeholder="e.g., Fiction")
            read = st.checkbox("Read")
            rating = st.slider("Rating", 0, 5, 0)
        notes = st.text_area("Notes", placeholder="Your thoughts...")
        submit = st.form_submit_button("Add Book")
        
        if submit and title and author:
            book = {
                'id': str(uuid.uuid4()),
                'title': title,
                'author': author,
                'year': year,
                'genre': genre,
                'read': read,
                'rating': rating,
                'notes': notes,
                'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.library.append(book)
            save_library({
                'books': st.session_state.library,
                'collections': st.session_state.collections,
                'reading_list': st.session_state.reading_list
            })
            st.success("Book added!")

# Browse Books Section
elif option == "Browse Books":
    st.header("📚 Browse Books")
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("Sort by", ["Title", "Author", "Year", "Genre", "Date Added"])
    with col2:
        filter_read = st.selectbox("Filter", ["All", "Read", "Unread"])
    
    books = st.session_state.library
    if filter_read == "Read":
        books = [b for b in books if b.get('read', False)]
    elif filter_read == "Unread":
        books = [b for b in books if not b.get('read', False)]
    
    sorted_books = sorted(books, key=lambda x: x.get(sort_by.lower(), 'date_added' if sort_by == "Date Added" else ''), reverse=True)
    
    for book in sorted_books:
        st.markdown(f"""
        <div class="book-card">
            <div class="book-title">{book['title']}</div>
            <div class="book-author">{book['author']}</div>
            <div>Genre: {book.get('genre', 'N/A')} | {'⭐' * book.get('rating', 0)}</div>
        </div>
        """, unsafe_allow_html=True)

# Search Section
elif option == "Search":
    st.header("🔍 Search Books")
    query = st.text_input("Search by title, author, or genre")
    if query:
        results = [b for b in st.session_state.library if query.lower() in (b.get('title', '') + b.get('author', '') + b.get('genre', '')).lower()]
        for book in results:
            st.markdown(f"""
            <div class="book-card">
                <div class="book-title">{book['title']}</div>
                <div class="book-author">{book['author']}</div>
                <div>Genre: {book.get('genre', 'N/A')} | {'Read' if book.get('read', False) else 'Unread'}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Enter a search term.")

# Collections Section
elif option == "Collections":
    st.header("📂 Collections")
    if 'new_collection' not in st.session_state:
        st.session_state.new_collection = ""
    
    new_collection = st.text_input("New Collection", value=st.session_state.new_collection)
    if st.button("Create Collection") and new_collection:
        st.session_state.collections[new_collection] = []
        st.session_state.new_collection = ""
        save_library({
            'books': st.session_state.library,
            'collections': st.session_state.collections,
            'reading_list': st.session_state.reading_list
        })
        st.success(f"Collection '{new_collection}' created!")
    
    for name, books in st.session_state.collections.items():
        with st.expander(name):
            st.write(f"{len(books)} books")
            for book_id in books:
                book = next((b for b in st.session_state.library if b['id'] == book_id), None)
                if book:
                    st.write(f"- {book['title']} by {book['author']}")

# Reading List Section
elif option == "Reading List":
    st.header("📋 Reading List")
    for book_id in st.session_state.reading_list:
        book = next((b for b in st.session_state.library if b['id'] == book_id), None)
        if book:
            st.markdown(f"""
            <div class="book-card">
                <div class="book-title">{book['title']}</div>
                <div class="book-author">{book['author']}</div>
            </div>
            """, unsafe_allow_html=True)

# Statistics Section
elif option == "Statistics":
    st.header("📊 Statistics")
    if st.session_state.library:
        df = pd.DataFrame(st.session_state.library)
        st.subheader("Genre Distribution")
        fig = px.bar(df['genre'].value_counts(), title="Books by Genre")
        st.plotly_chart(fig)

# Settings Section
elif option == "Settings":
    st.header("⚙️ Settings")
    if st.button("Backup Library"):
        backup_file = backup_library()
        if backup_file:
            with open(backup_file, 'r') as f:
                st.download_button("Download Backup", f, file_name=backup_file)
    uploaded_file = st.file_uploader("Restore from Backup", type="json")
    if uploaded_file and st.button("Restore"):
        with open("temp_restore.json", "wb") as f:
            f.write(uploaded_file.getvalue())
        if restore_from_backup("temp_restore.json"):
            st.success("Library restored!")
            os.remove("temp_restore.json")
            st.experimental_rerun()
    
    # Theme settings - fixed indentation
    if 'theme' not in st.session_state:
        st.session_state.theme = "Light"

    # Apply theme styles
    if st.session_state.theme == "Dark":
        st.markdown("""
        <style>
        .main {
            background-color: #2c3e50;
            color: #ecf0f1;
        }
        .book-card {
            background-color: #34495e;
            color: #ecf0f1;
        }
        .stButton>button {
            background-color: #3498db;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .main {
            background-color: white;
            color: #2c3e50;
        }
        .book-card {
            background-color: #ffffff;
            color: #2c3e50;
        }
        .stButton>button {
            background-color: #3498db;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)



elif option == "Settings":
    st.header("⚙️ Settings")

    # Theme Selection
    st.subheader("Theme")
    theme = st.selectbox("Select Theme", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1)
    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.experimental_rerun()  # Rerun to apply the new theme immediately

    # Data Export
    st.subheader("Data Export")
    if st.button("Export as JSON"):
        full_data = {
            'books': st.session_state.library,
            'collections': st.session_state.collections,
            'reading_list': st.session_state.reading_list
        }
        st.download_button(
            label="Download JSON",
            data=json.dumps(full_data, indent=4),
            file_name="library.json",
            mime="application/json"
        )

    if st.button("Export as CSV"):
        if st.session_state.library:
            df = pd.DataFrame(st.session_state.library)
            if 'tags' in df.columns:
                df['tags'] = df['tags'].apply(lambda x: ','.join(x) if isinstance(x, list) else '')
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="library.csv",
                mime="text/csv"
            )
        else:
            st.warning("No books to export.")

    # Import Books
    st.subheader("Import Books")
    st.write("CSV should have columns: title, author, year (optional), genre (optional), read (optional), rating (optional), notes (optional), isbn (optional), tags (comma-separated, optional)")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            required_columns = ['title', 'author']
            if not all(col in df.columns for col in required_columns):
                st.error(f"CSV must contain columns: {', '.join(required_columns)}")
            else:
                new_books = []
                for _, row in df.iterrows():
                    book = {
                        'id': str(uuid.uuid4()),
                        'title': row['title'],
                        'author': row['author'],
                        'year': int(row.get('year', 0)) if pd.notna(row.get('year')) else 0,
                        'genre': row.get('genre', ''),
                        'read': bool(row.get('read', False)),
                        'rating': int(row.get('rating', 0)) if pd.notna(row.get('rating')) else 0,
                        'notes': row.get('notes', ''),
                        'isbn': row.get('isbn', ''),
                        'tags': [tag.strip() for tag in str(row.get('tags', '')).split(',') if tag.strip()],
                        'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    new_books.append(book)
                st.session_state.library.extend(new_books)
                save_library({
                    'books': st.session_state.library,
                    'collections': st.session_state.collections,
                    'reading_list': st.session_state.reading_list
                })
                st.success(f"Imported {len(new_books)} books.")
        except Exception as e:
            st.error(f"Error importing CSV: {str(e)}")

    # Reset Library
    st.subheader("Reset Library")
    if st.button("Reset Library"):
        st.warning("Are you sure you want to reset the library? This action cannot be undone.")
        if st.button("Confirm Reset"):
            st.session_state.library = []
            st.session_state.collections = {}
            st.session_state.reading_list = []
            save_library({
                'books': [],
                'collections': {},
                'reading_list': []
            })
            st.success("Library reset successfully.")
            st.experimental_rerun()  # Rerun to refresh the app state