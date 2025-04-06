import os
import pandas as pd
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, session, jsonify) # Added session and jsonify
from werkzeug.utils import secure_filename
import json # To pass data safely to JavaScript

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
# IMPORTANT: Change this to a random, secret value in production!
SECRET_KEY = 'dev_secret_key_replace_this'

# --- Flask App Initialization ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit uploads to 16MB

# --- Helper Functions ---
def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def perform_analysis(filepath):
    """Loads data and performs various analyses."""
    try:
        # Load data
        df = pd.read_csv(filepath)

        # --- Data Cleaning & Preparation ---
        # Attempt to convert 'event_date' to datetime objects
        try:
            df['event_date'] = pd.to_datetime(df['event_date'])
            df['event_month'] = df['event_date'].dt.strftime('%Y-%m') # Extract YYYY-MM for grouping
        except KeyError:
            flash("Warning: 'event_date' column not found or invalid format. Temporal analysis skipped.", "warning")
            df['event_month'] = None # Ensure column exists even if empty
        except Exception as e:
            flash(f"Warning: Could not parse 'event_date': {e}. Temporal analysis might be affected.", "warning")
            df['event_month'] = None

        # Check for optional columns existence before analysis
        has_type = 'event_type' in df.columns
        has_location = 'location' in df.columns
        has_attendance = 'attendance' in df.columns and pd.api.types.is_numeric_dtype(df['attendance'])
        has_duration = 'duration_hours' in df.columns and pd.api.types.is_numeric_dtype(df['duration_hours'])

        # --- Analysis ---
        results = {}
        results['total_events'] = len(df)
        results['date_range'] = (df['event_date'].min().strftime('%Y-%m-%d'), df['event_date'].max().strftime('%Y-%m-%d')) if 'event_date' in df.columns and not df['event_date'].isnull().all() else ('N/A', 'N/A')

        # 1. Event Counts by Type (Chart Data)
        if has_type:
            type_counts = df['event_type'].value_counts().to_dict()
            results['type_counts_chart'] = {
                "labels": list(type_counts.keys()),
                "data": list(type_counts.values())
            }
        else:
             results['type_counts_chart'] = {"labels": [], "data": []}

        # 2. Event Counts by Location (Chart Data)
        if has_location:
            location_counts = df['location'].value_counts().to_dict()
            results['location_counts_chart'] = {
                "labels": list(location_counts.keys()),
                "data": list(location_counts.values())
            }
        else:
            results['location_counts_chart'] = {"labels": [], "data": []}

        # 3. Events Over Time (Monthly) (Chart Data)
        if df['event_month'] is not None and not df['event_month'].isnull().all():
            monthly_counts = df['event_month'].value_counts().sort_index().to_dict()
            results['monthly_counts_chart'] = {
                "labels": list(monthly_counts.keys()),
                "data": list(monthly_counts.values())
            }
        else:
            results['monthly_counts_chart'] = {"labels": [], "data": []}

        # 4. Summary Statistics (Table Data)
        summary_stats = {}
        if has_attendance:
            summary_stats['Average Attendance'] = round(df['attendance'].mean(), 2)
            summary_stats['Median Attendance'] = int(df['attendance'].median())
            summary_stats['Total Attendance'] = int(df['attendance'].sum())
        if has_duration:
             summary_stats['Average Duration (hrs)'] = round(df['duration_hours'].mean(), 2)
             summary_stats['Median Duration (hrs)'] = round(df['duration_hours'].median(), 2)
        results['summary_stats'] = summary_stats if summary_stats else {"Info": "No numeric attendance or duration columns found."}

        # 5. Top 5 Events (example - could be by attendance if available)
        if has_type:
            results['top_event_types'] = df['event_type'].value_counts().head(5).to_dict()
        else:
            results['top_event_types'] = {}


        return results

    except FileNotFoundError:
        flash(f"Error: Could not find the file at {filepath}", "danger")
        return None
    except pd.errors.EmptyDataError:
        flash("Error: The uploaded CSV file is empty.", "danger")
        return None
    except Exception as e:
        flash(f"An error occurred during analysis: {e}", "danger")
        print(f"Analysis Error: {e}") # Log error for debugging
        return None


# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'event_file' not in request.files:
            flash('No file part selected.', 'warning')
            return redirect(request.url)
        file = request.files['event_file']

        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) # Sanitize filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(filepath)
                flash('File successfully uploaded!', 'success')
                # Store filename in session to retrieve in the results view
                session['uploaded_filename'] = filename
                return redirect(url_for('results'))
            except Exception as e:
                 flash(f'Error saving file: {e}', 'danger')
                 return redirect(request.url)
        else:
             flash('Invalid file type. Please upload a CSV file.', 'danger')
             return redirect(request.url)

    # GET request: Render the upload form
    from datetime import datetime

    return render_template('index.html', now=datetime.now)

@app.route('/results')
def results():
    # Retrieve filename from session
    filename = session.get('uploaded_filename', None)
    if not filename:
        flash('No file has been uploaded yet.', 'info')
        return redirect(url_for('index'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        flash('Uploaded file not found. Please upload again.', 'danger')
        session.pop('uploaded_filename', None) # Clear invalid session data
        return redirect(url_for('index'))

    # Perform analysis
    analysis_results = perform_analysis(filepath)

    if analysis_results is None:
        # Error occurred during analysis, flash message already set
        return redirect(url_for('index'))

    # Clean up the uploaded file after analysis (optional, keep for debugging?)
    # try:
    #     os.remove(filepath)
    #     session.pop('uploaded_filename', None) # Clear session if file removed
    # except OSError as e:
    #     print(f"Error removing file {filepath}: {e}")

    # Pass results and chart data (JSON-encoded) to the template
    return render_template(
        'results.html',
        filename=filename,
        results=analysis_results,
        # Use json.dumps for safe embedding in JavaScript
        type_counts_json=json.dumps(analysis_results.get('type_counts_chart', {})),
        location_counts_json=json.dumps(analysis_results.get('location_counts_chart', {})),
        monthly_counts_json=json.dumps(analysis_results.get('monthly_counts_chart', {}))
    )

# --- Run the App ---
if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True) # debug=True is helpful for development, disable for production