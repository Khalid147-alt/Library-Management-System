import streamlit as st
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px
import uuid

# Set page configuration
st.set_page_config(
    page_title="Personal Library Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    .st-emotion-cache-1kyxreq {
        margin-top: -60px;
    }
    .st-emotion-cache-16idsys p {
        font-size: 18px;
    }
    .book-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 10px;
    }
    .book-title {
        font-weight: bold;
        font-size: 18px;
    }
    .book-author {
        font-style: italic;
    }
    .book-info {
        margin-top: 10px;
    }
    .st-emotion-cache-1jp5osc {
        margin-top: 25px;
    }
</style>
""", unsafe_allow_html=True)

# File to store the library
filename = "library.json"

# Function to load the library from file
def load_library():
    """Load the library from a JSON file, or return an empty list if the file doesn't exist or is corrupted."""
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                library = json.load(f)
                # Add UUID if not present for backward compatibility
                for book in library:
                    if 'id' not in book:
                        book['id'] = str(uuid.uuid4())
                return library
        except json.JSONDecodeError:
            st.error("Error loading library file. Starting with an empty library.")
            return []
    return []

# Function to save the library to file
def save_library(library):
    """Save the library to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(library, f)

# Function to backup the library
def backup_library():
    """Create a backup of the current library state."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"library_backup_{timestamp}.json"
    with open(backup_filename, 'w') as f:
        json.dump(st.session_state.library, f)
    return backup_filename

# Function to restore from backup
def restore_from_backup(backup_file):
    """Restore library from a backup file."""
    try:
        with open(backup_file, 'r') as f:
            st.session_state.library = json.load(f)
        save_library(st.session_state.library)
        return True
    except Exception as e:
        st.error(f"Error restoring from backup: {e}")
        return False

# Initialize the library in session state
if 'library' not in st.session_state:
    try:
        st.session_state.library = load_library()
    except Exception as e:
        st.error("Error loading library: 'str' object does not support item assignment. Starting with empty library.")
        st.session_state.library = []

# App header with logo
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("# 📚")
with col2:
    st.title("Personal Library Manager")
    st.write("Manage your personal book collection with ease.")

# Sidebar navigation with improved styling
with st.sidebar:
    st.image("https://via.placeholder.com/150x150.png?text=Library", width=150)
    st.title("Navigation")
    options = ["Dashboard", "Add Book", "Browse Books", "Search", "Collections", "Reading List", "Statistics", "Settings"]
    icons = ["house", "plus-circle", "book", "search", "collection", "list-check", "bar-chart", "gear"]
    
    option = st.radio("", options, format_func=lambda x: f":{icons[options.index(x)]}: {x}")

# Dashboard
if option == "Dashboard":
    st.header("📊 Dashboard")
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    total_books = len(st.session_state.library)
    num_read = sum(1 for book in st.session_state.library if book.get('read', False))
    genres = set(book.get('genre', '').lower() for book in st.session_state.library if book.get('genre', ''))
    authors = set(book.get('author', '').lower() for book in st.session_state.library if book.get('author', ''))
    
    with col1:
        st.metric("Total Books", total_books)
    with col2:
        st.metric("Books Read", num_read)
    with col3:
        st.metric("Unique Genres", len(genres))
    with col4:
        st.metric("Unique Authors", len(authors))
    
    # Recent additions
    st.subheader("Recently Added Books")
    if st.session_state.library:
        recent_books = sorted(st.session_state.library, key=lambda x: x.get('date_added', '0'), reverse=True)[:5]
        for book in recent_books:
            with st.container():
                st.markdown(f"""
                <div class="book-card">
                    <div class="book-title">{book['title']}</div>
                    <div class="book-author">by {book['author']}</div>
                    <div class="book-info">
                        Genre: {book.get('genre', 'N/A')} | Year: {book.get('year', 'N/A')} | 
                        Status: {"Read" if book.get('read', False) else "Unread"}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No books in your library yet. Add some books to get started!")

    # Reading progress
    if num_read > 0:
        st.subheader("Reading Progress")
        fig = px.pie(values=[num_read, total_books - num_read], 
                     names=["Read", "Unread"], 
                     hole=0.4,
                     color_discrete_sequence=["#4CAF50", "#E0E0E0"])
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig)

# Add Book Section
elif option == "Add Book":
    st.header("Add a New Book")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Title")
        author = st.text_input("Author")
        year = st.number_input("Publication Year", min_value=0, step=1, format="%d")
        isbn = st.text_input("ISBN (optional)")
    
    with col2:
        genre = st.text_input("Genre")
        read = st.checkbox("Have you read this book?")
        rating = st.slider("Rating", 0, 5, 0)
        notes = st.text_area("Notes (optional)")
    
    # Add tags
    tags = st.text_input("Tags (comma separated)")
    
    if st.button("Add Book"):
        if title and author:
            book = {
                'id': str(uuid.uuid4()),
                'title': title,
                'author': author,
                'year': int(year),
                'genre': genre,
                'read': read,
                'rating': rating,
                'notes': notes,
                'isbn': isbn,
                'tags': [tag.strip() for tag in tags.split(',')] if tags else [],
                'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.library.append(book)
            save_library(st.session_state.library)
            st.success("Book added successfully!")
        else:
            st.error("Please fill in at least the title and author.")

# Browse Books Section
elif option == "Browse Books":
    st.header("Browse Your Library")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        sort_by = st.selectbox("Sort by", ["Title", "Author", "Year", "Genre", "Date Added"])
    with col2:
        sort_order = st.radio("Order", ["Ascending", "Descending"], horizontal=True)
    with col3:
        filter_read = st.radio("Filter by", ["All", "Read", "Unread"], horizontal=True)
    
    # Apply filters
    filtered_books = st.session_state.library
    
    if filter_read == "Read":
        filtered_books = [book for book in filtered_books if book.get('read', False)]
    elif filter_read == "Unread":
        filtered_books = [book for book in filtered_books if not book.get('read', False)]
    
    # Apply sorting
    sort_key = sort_by.lower()
    if sort_key == "date added":
        sort_key = "date_added"
    
    reverse_order = sort_order == "Descending"
    
    sorted_books = sorted(filtered_books, 
                          key=lambda x: str(x.get(sort_key, "")).lower(),
                          reverse=reverse_order)
    
    # Display books in a grid
    if sorted_books:
        cols = st.columns(3)
        for i, book in enumerate(sorted_books):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"""
                    <div class="book-card">
                        <div class="book-title">{book['title']}</div>
                        <div class="book-author">by {book['author']}</div>
                        <div class="book-info">
                            Genre: {book.get('genre', 'N/A')} | Year: {book.get('year', 'N/A')} | 
                            Status: {"Read" if book.get('read', False) else "Unread"}
                        </div>
                        <div class="book-info">
                            Rating: {"⭐" * book.get('rating', 0)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("View Details", key=f"view_{book['id']}"):
                        st.session_state.selected_book = book['id']
                    if st.button("Edit", key=f"edit_{book['id']}"):
                        st.session_state.edit_book = book['id']
                    if st.button("Delete", key=f"delete_{book['id']}"):
                        st.session_state.library.remove(book)
                        save_library(st.session_state.library)
                        st.experimental_rerun()
    else:
        st.info("No books found matching your criteria.")
    
    # Book details modal
    if hasattr(st.session_state, 'selected_book'):
        book = next((b for b in st.session_state.library if b['id'] == st.session_state.selected_book), None)
        if book:
            with st.expander("Book Details", expanded=True):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image("https://via.placeholder.com/150x200.png?text=Cover", width=150)
                with col2:
                    st.markdown(f"# {book['title']}")
                    st.markdown(f"## by {book['author']}")
                    st.markdown(f"**Genre:** {book.get('genre', 'N/A')}")
                    st.markdown(f"**Year:** {book.get('year', 'N/A')}")
                    st.markdown(f"**ISBN:** {book.get('isbn', 'N/A')}")
                    st.markdown(f"**Status:** {'Read' if book.get('read', False) else 'Unread'}")
                    st.markdown(f"**Rating:** {'⭐' * book.get('rating', 0)}")
                    if book.get('tags', []):
                        st.markdown("**Tags:**")
                        for tag in book.get('tags', []):
                            st.markdown(f"- {tag}")
                    if book.get('notes', ''):
                        st.markdown("**Notes:**")
                        st.markdown(book.get('notes', ''))

# Search Section
elif option == "Search":
    st.header("Search for Books")
    
    search_by = st.selectbox("Search by", ["Title", "Author", "Genre", "Tags", "All Fields"])
    search_term = st.text_input(f"Enter search term")
    
    col1, col2 = st.columns(2)
    with col1:
        match_type = st.radio("Match type", ["Contains", "Exact Match"], horizontal=True)
    with col2:
        case_sensitive = st.checkbox("Case sensitive")
    
    if st.button("Search"):
        if search_term:
            matching_books = []
            for book in st.session_state.library:
                if search_by == "All Fields":
                    search_fields = [
                        book.get('title', ''),
                        book.get('author', ''),
                        book.get('genre', ''),
                        book.get('notes', ''),
                        ' '.join(book.get('tags', []))
                    ]
                    search_text = ' '.join(search_fields)
                elif search_by == "Tags":
                    search_text = ' '.join(book.get('tags', []))
                else:
                    search_text = book.get(search_by.lower(), '')
                
                if not case_sensitive:
                    search_text = search_text.lower()
                    search_term_mod = search_term.lower()
                else:
                    search_term_mod = search_term
                
                if match_type == "Contains" and search_term_mod in search_text:
                    matching_books.append(book)
                elif match_type == "Exact Match" and search_term_mod == search_text:
                    matching_books.append(book)
            
            if matching_books:
                st.write(f"Found {len(matching_books)} matching books:")
                for book in matching_books:
                    with st.container():
                        st.markdown(f"""
                        <div class="book-card">
                            <div class="book-title">{book['title']}</div>
                            <div class="book-author">by {book['author']}</div>
                            <div class="book-info">
                                Genre: {book.get('genre', 'N/A')} | Year: {book.get('year', 'N/A')} | 
                                Status: {"Read" if book.get('read', False) else "Unread"}
                            </div>
                            <div class="book-info">
                                Rating: {"⭐" * book.get('rating', 0)}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No matching books found.")
        else:
            st.error("Please enter a search term.")

# Collections Section (Continued)
elif option == "Collections":
    st.header("Book Collections")
    
    # Manage collections
    with st.expander("Manage Collections", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            # Initialize collections in session state if not present
            if 'collections' not in st.session_state:
                st.session_state.collections = load_library().get('collections', {})
            
            # Add new collection
            new_collection = st.text_input("Create New Collection")
            if st.button("Create Collection"):
                if new_collection:
                    if new_collection not in st.session_state.collections:
                        st.session_state.collections[new_collection] = []
                        # Update the library with collections
                        library_data = {
                            'books': st.session_state.library,
                            'collections': st.session_state.collections
                        }
                        save_library(library_data)
                        st.success(f"Collection '{new_collection}' created successfully!")
                    else:
                        st.error("Collection already exists!")
        
        with col2:
            # Delete collection
            if st.session_state.collections:
                collection_to_delete = st.selectbox("Select Collection to Delete", list(st.session_state.collections.keys()))
                if st.button("Delete Collection"):
                    if collection_to_delete:
                        del st.session_state.collections[collection_to_delete]
                        # Update the library with collections
                        library_data = {
                            'books': st.session_state.library,
                            'collections': st.session_state.collections
                        }
                        save_library(library_data)
                        st.success(f"Collection '{collection_to_delete}' deleted successfully!")
            else:
                st.info("No collections created yet.")
    
    # View collections
    st.subheader("Your Collections")
    if st.session_state.collections:
        collection_tabs = st.tabs(list(st.session_state.collections.keys()))
        
        for i, collection_name in enumerate(st.session_state.collections.keys()):
            with collection_tabs[i]:
                # Get books in this collection
                collection_books = [book for book in st.session_state.library if book['id'] in st.session_state.collections[collection_name]]
                
                # Display collection stats
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Books in Collection", len(collection_books))
                with col2:
                    read_count = sum(1 for book in collection_books if book.get('read', False))
                    if collection_books:
                        st.metric("Read Percentage", f"{(read_count / len(collection_books) * 100):.1f}%")
                    else:
                        st.metric("Read Percentage", "0%")
                
                # Add books to collection
                st.subheader("Add Books to Collection")
                available_books = [book for book in st.session_state.library if book['id'] not in st.session_state.collections[collection_name]]
                if available_books:
                    books_to_add = st.multiselect(
                        "Select books to add",
                        options=[(book['id'], f"{book['title']} by {book['author']}") for book in available_books],
                        format_func=lambda x: x[1]
                    )
                    
                    if st.button("Add to Collection", key=f"add_to_{collection_name}"):
                        for book_id, _ in books_to_add:
                            st.session_state.collections[collection_name].append(book_id)
                        # Update the library with collections
                        library_data = {
                            'books': st.session_state.library,
                            'collections': st.session_state.collections
                        }
                        save_library(library_data)
                        st.success("Books added to collection successfully!")
                        st.experimental_rerun()
                else:
                    st.info("All books already in this collection.")
                
                # Display books in collection
                st.subheader("Books in Collection")
                if collection_books:
                    for book in collection_books:
                        with st.container():
                            st.markdown(f"""
                            <div class="book-card">
                                <div class="book-title">{book['title']}</div>
                                <div class="book-author">by {book['author']}</div>
                                <div class="book-info">
                                    Genre: {book.get('genre', 'N/A')} | Year: {book.get('year', 'N/A')} | 
                                    Status: {"Read" if book.get('read', False) else "Unread"}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button("Remove from Collection", key=f"remove_{book['id']}_{collection_name}"):
                                st.session_state.collections[collection_name].remove(book['id'])
                                # Update the library with collections
                                library_data = {
                                    'books': st.session_state.library,
                                    'collections': st.session_state.collections
                                }
                                save_library(library_data)
                                st.success(f"Book removed from collection successfully!")
                                st.experimental_rerun()
                else:
                    st.info("No books in this collection yet.")
    else:
        st.info("No collections created yet. Create a collection to organize your books!")

# Reading List Section
elif option == "Reading List":
    st.header("Reading List")
    
    # Add to reading list
    with st.expander("Add to Reading List", expanded=True):
        # Get unread books not in reading list
        if 'reading_list' not in st.session_state:
            st.session_state.reading_list = []
        
        available_books = [book for book in st.session_state.library 
                          if not book.get('read', False) and book['id'] not in st.session_state.reading_list]
        
        if available_books:
            books_to_add = st.multiselect(
                "Select books to add to reading list",
                options=[(book['id'], f"{book['title']} by {book['author']}") for book in available_books],
                format_func=lambda x: x[1]
            )
            
            if st.button("Add to Reading List"):
                for book_id, _ in books_to_add:
                    st.session_state.reading_list.append(book_id)
                # Update the library with reading list
                library_data = {
                    'books': st.session_state.library,
                    'reading_list': st.session_state.reading_list
                }
                save_library(library_data)
                st.success("Books added to reading list successfully!")
                st.experimental_rerun()
        else:
            st.info("No unread books available to add to reading list.")
    
    # Display reading list
    st.subheader("Your Reading List")
    reading_list_books = [book for book in st.session_state.library if book['id'] in st.session_state.reading_list]
    
    if reading_list_books:
        # Reorder reading list
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Drag to reorder")
        with col2:
            if st.button("Mark as Read"):
                for book in reading_list_books:
                    book['read'] = True
                st.session_state.reading_list = []
                save_library(st.session_state.library)
                st.success("All books marked as read!")
                st.experimental_rerun()
        
        for i, book in enumerate(reading_list_books):
            with st.container():
                cols = st.columns([1, 10, 2])
                with cols[0]:
                    st.write(f"#{i+1}")
                with cols[1]:
                    st.markdown(f"""
                    <div class="book-card">
                        <div class="book-title">{book['title']}</div>
                        <div class="book-author">by {book['author']}</div>
                        <div class="book-info">
                            Genre: {book.get('genre', 'N/A')} | Year: {book.get('year', 'N/A')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with cols[2]:
                    if st.button("Remove", key=f"remove_reading_{book['id']}"):
                        st.session_state.reading_list.remove(book['id'])
                        save_library(st.session_state.library)
                        st.success("Book removed from reading list!")
                        st.experimental_rerun()
                    if st.button("Mark Read", key=f"mark_read_{book['id']}"):
                        book['read'] = True
                        st.session_state.reading_list.remove(book['id'])
                        save_library(st.session_state.library)
                        st.success("Book marked as read!")
                        st.experimental_rerun()
    else:
        st.info("Your reading list is empty. Add some books to get started!")

# Statistics Section
elif option == "Statistics":
    st.header("Library Statistics")
    
    # Basic stats
    total_books = len(st.session_state.library)
    
    if total_books > 0:
        num_read = sum(1 for book in st.session_state.library if book.get('read', False))
        percentage_read = (num_read / total_books) * 100
        
        # Create a DataFrame for analysis
        df = pd.DataFrame(st.session_state.library)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", total_books)
        with col2:
            st.metric("Books Read", num_read)
        with col3:
            st.metric("Completion Rate", f"{percentage_read:.1f}%")
        
        # Tabs for different charts
        tab1, tab2, tab3, tab4 = st.tabs(["Genres", "Authors", "Reading Progress", "Timeline"])
        
        with tab1:
            # Genre distribution
            st.subheader("Genre Distribution")
            genre_counts = df['genre'].value_counts().reset_index()
            genre_counts.columns = ['Genre', 'Count']
            
            if len(genre_counts) > 0:
                fig = px.pie(genre_counts, values='Count', names='Genre', hole=0.4)
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No genre data available.")
        
        with tab2:
            # Top authors
            st.subheader("Top Authors")
            author_counts = df['author'].value_counts().reset_index()
            author_counts.columns = ['Author', 'Count']
            
            if len(author_counts) > 0:
                fig = px.bar(author_counts.head(10), x='Author', y='Count')
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No author data available.")
        
        with tab3:
            # Reading progress over time
            st.subheader("Reading Progress Over Time")
            if 'date_added' in df.columns:
                # Convert date_added to datetime
                df['date_added'] = pd.to_datetime(df['date_added'])
                df['year_month'] = df['date_added'].dt.strftime('%Y-%m')
                
                # Group by year-month
                monthly_counts = df.groupby('year_month').size().reset_index(name='new_books')
                monthly_read = df[df['read'] == True].groupby('year_month').size().reset_index(name='read_books')
                
                # Merge the two dataframes
                monthly_stats = pd.merge(monthly_counts, monthly_read, on='year_month', how='left')
                monthly_stats['read_books'] = monthly_stats['read_books'].fillna(0)
                
                # Calculate cumulative counts
                monthly_stats['cumulative_books'] = monthly_stats['new_books'].cumsum()
                monthly_stats['cumulative_read'] = monthly_stats['read_books'].cumsum()
                
                # Plot
                fig = px.line(monthly_stats, x='year_month', y=['cumulative_books', 'cumulative_read'],
                             labels={'year_month': 'Month', 'value': 'Books', 'variable': 'Type'},
                             title='Cumulative Books Added vs Read')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No date information available.")
        
        with tab4:
            # Timeline of books by year
            st.subheader("Books by Publication Year")
            if 'year' in df.columns:
                year_counts = df.groupby('year').size().reset_index(name='count')
                year_counts = year_counts[year_counts['year'] > 0]  # Filter out invalid years
                
                fig = px.bar(year_counts, x='year', y='count',
                            labels={'year': 'Publication Year', 'count': 'Number of Books'},
                            title='Books by Publication Year')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No publication year data available.")
        
        # Reading habits
        st.subheader("Reading Habits")
        col1, col2 = st.columns(2)
        
        with col1:
            # Average rating
            if 'rating' in df.columns:
                avg_rating = df[df['rating'] > 0]['rating'].mean()
                if not pd.isna(avg_rating):
                    st.metric("Average Rating", f"{avg_rating:.1f}/5")
                else:
                    st.metric("Average Rating", "N/A")
            
            # Books by read status
            read_status = df['read'].value_counts().reset_index()
            read_status.columns = ['Status', 'Count']
            read_status['Status'] = read_status['Status'].map({True: 'Read', False: 'Unread'})
            
            fig = px.pie(read_status, values='Count', names='Status', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Genre completion rates
            if 'genre' in df.columns:
                genre_completion = df.groupby('genre').agg({'read': 'mean'}).reset_index()
                genre_completion['completion_rate'] = genre_completion['read'] * 100
                genre_completion = genre_completion.sort_values('completion_rate', ascending=False)
                
                fig = px.bar(genre_completion.head(10), 
                             x='genre', y='completion_rate',
                             labels={'genre': 'Genre', 'completion_rate': 'Completion Rate (%)'},
                             title='Genre Completion Rates')
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add some books to see statistics!")

# Settings Section
elif option == "Settings":
    st.header("Settings")
    
    # Backup and restore
    st.subheader("Backup and Restore")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("Create a backup of your library")
        if st.button("Create Backup"):
            backup_file = backup_library()
            st.success(f"Backup created successfully: {backup_file}")
            st.download_button(
                label="Download Backup",
                data=open(backup_file, 'rb').read(),
                file_name=backup_file,
                mime="application/json"
            )
    
    with col2:
        st.write("Restore from backup")
        uploaded_file = st.file_uploader("Upload backup file", type=["json"])
        if uploaded_file is not None:
            # Save the uploaded file temporarily
            with open("temp_backup.json", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.button("Restore Backup"):
                if restore_from_backup("temp_backup.json"):
                    st.success("Library restored successfully!")
                    st.experimental_rerun()
    
    # Export options
    st.subheader("Export Library")
    export_format = st.radio("Export format", ["CSV", "Excel", "JSON"], horizontal=True)
    
    if st.button("Export Library"):
        if st.session_state.library:
            df = pd.DataFrame(st.session_state.library)
            if export_format == "CSV":
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="library_export.csv",
                    mime="text/csv"
                )
            elif export_format == "Excel":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Library', index=False)
                excel_data = output.getvalue()
                st.download_button(
                    label="Download Excel",
                    data=excel_data,
                    file_name="library_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:  # JSON
                json_str = json.dumps(st.session_state.library, indent=4)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name="library_export.json",
                    mime="application/json"
                )
        else:
            st.error("No books in library to export!")
    
    # Import data
    st.subheader("Import Data")
    import_format = st.radio("Import format", ["CSV", "JSON"], horizontal=True)
    
    uploaded_import = st.file_uploader(f"Upload {import_format} file", type=[import_format.lower()])
    if uploaded_import is not None:
        if import_format == "CSV":
            try:
                import_df = pd.read_csv(uploaded_import)
                if st.button("Import from CSV"):
                    # Convert DataFrame to list of dictionaries
                    imported_books = import_df.to_dict('records')
                    # Add unique IDs if missing
                    for book in imported_books:
                        if 'id' not in book:
                            book['id'] = str(uuid.uuid4())
                    # Add to library
                    st.session_state.library.extend(imported_books)
                    save_library(st.session_state.library)
                    st.success(f"Successfully imported {len(imported_books)} books!")
            except Exception as e:
                st.error(f"Error importing CSV: {e}")
        else:  # JSON
            try:
                imported_data = json.load(uploaded_import)
                if st.button("Import from JSON"):
                    # Check if it's a list (books directly) or dict (may contain collections etc.)
                    if isinstance(imported_data, list):
                        imported_books = imported_data
                    elif isinstance(imported_data, dict) and 'books' in imported_data:
                        imported_books = imported_data['books']
                        # If collections exist, import them too
                        if 'collections' in imported_data:
                            st.session_state.collections = imported_data['collections']
                    else:
                        st.error("Invalid JSON format. Expected a list of books or a dictionary with a 'books' key.")
                        imported_books = []
                    
                    # Add unique IDs if missing
                    for book in imported_books:
                        if 'id' not in book:
                            book['id'] = str(uuid.uuid4())
                    
                    # Add to library
                    st.session_state.library.extend(imported_books)
                    save_library(st.session_state.library)
                    st.success(f"Successfully imported {len(imported_books)} books!")
            except Exception as e:
                st.error(f"Error importing JSON: {e}")
    
    # Clear data
    st.subheader("Clear Data")
    with st.expander("⚠️ Danger Zone", expanded=False):
        st.warning("The following actions cannot be undone. Please make sure you have a backup before proceeding.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Reading List"):
                if 'reading_list' in st.session_state:
                    st.session_state.reading_list = []
                    save_library(st.session_state.library)
                    st.success("Reading list cleared successfully!")
        
        with col2:
            if st.button("Clear All Collections"):
                if 'collections' in st.session_state:
                    st.session_state.collections = {}
                    save_library(st.session_state.library)
                    st.success("All collections cleared successfully!")
        
        if st.button("⚠️ RESET ENTIRE LIBRARY"):
            confirm = st.text_input("Type 'DELETE' to confirm reset of entire library")
            if confirm == "DELETE":
                st.session_state.library = []
                if 'collections' in st.session_state:
                    st.session_state.collections = {}
                if 'reading_list' in st.session_state:
                    st.session_state.reading_list = []
                save_library([])  # Save empty library
                st.success("Library reset successfully!")
                st.experimental_rerun()
    
    # Appearance settings
    st.subheader("Appearance Settings")
    theme = st.selectbox("Theme", ["Light", "Dark", "System Default"])
    st.info("Theme settings will be available in a future update.")
    
    # Fix missing imports from earlier
    import io
    import plotly.express as px
    
# Add the necessary import at the top of the file
# import io

# Update the load_library and save_library functions to handle the new data structure
def load_library():
    """Load the library from a JSON file, or return an empty structure if the file doesn't exist or is corrupted."""
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
                # Check if the data is the old format (just a list of books)
                if isinstance(data, list):
                    library = data
                    # Add UUID if not present for backward compatibility
                    for book in library:
                        if 'id' not in book:
                            book['id'] = str(uuid.uuid4())
                    return {
                        'books': library,
                        'collections': {},
                        'reading_list': []
                    }
                else:
                    # New format with collections and reading list
                    if 'books' not in data:
                        data['books'] = []
                    if 'collections' not in data:
                        data['collections'] = {}
                    if 'reading_list' not in data:
                        data['reading_list'] = []
                    
                    # Add UUID if not present for backward compatibility
                    for book in data['books']:
                        if 'id' not in book:
                            book['id'] = str(uuid.uuid4())
                    
                    return data
        except json.JSONDecodeError:
            st.error("Error loading library file. Starting with an empty library.")
            return {'books': [], 'collections': {}, 'reading_list': []}
    return {'books': [], 'collections': {}, 'reading_list': []}

def save_library(data):
    """Save the library to a JSON file."""
    # Check if data is just the books list (old format)
    if isinstance(data, list):
        data = {
            'books': data,
            'collections': st.session_state.get('collections', {}),
            'reading_list': st.session_state.get('reading_list', [])
        }
    
    with open(filename, 'w') as f:
        json.dump(data, f)

# Initialize application state properly
if 'library' not in st.session_state:
    data = load_library()
    st.session_state.library = data['books']
    st.session_state.collections = data['collections']
    st.session_state.reading_list = data['reading_list']