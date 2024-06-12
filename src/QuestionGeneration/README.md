# Question Generation

This project contains Python scripts designed to generate various types of questions based on event data. The scripts read event attributes from a database, construct questions, and store them back in the database.

## Requirements

- Python 3.x
- `psycopg2` for PostgreSQL database interaction
- `requests` for HTTP requests
- `configparser` for reading database configuration
- `SPARQLWrapper` for executing SPARQL queries

## Setup

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
2. Install the required Python packages:
   ```bash
   pip install psycopg2 requests SPARQLWrapper configparser pandas
3. Configure the database connection:
   - Create a `database.ini` file with the following format:
     ```ini
     [postgresql]
     host=your_host
     database=your_database
     user=your_user
     password=your_password
     ```
## Running the Scripts

1. Ensure your database is set up and populated with the required data.
2. Run the question generation files for the desired type of question
