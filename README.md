# Query Purpose Extractor (QPE)

QPE is an application built with the goal of making Structured Query Language (SQL) more accessible and understandable to non-technical or beginning-to-be-technical users.

<p align="center">
    <img src="./public/qpe-screenshot.png" width="60%" height="45%" />
</p>

<p align="center">
    https://query-pe.dev
</p>

## Installation

1. Clone this repository into a local directory on your machine.
2. Navigate to your new repository root in your terminal. Execute the below commands:  
```
# Create a new virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install python dependencies
pip install -r requirements.txt

# If you encountered an error referencing 'python setup.py egg_info', uncomment 
# and run the below command inside your virtual environment. Then, try to install 
# the python dependencies again.
# pip install --upgrade setuptools

# Deactivate virtual environment
deactivate

# Install npm dependencies
npm install
```

## Running the Application

1. Open two terminal windows. Navigate to the root of your cloned repository in both windows.
2. In the first window, run the command `yarn start-api`. This will begin your backend instance.
3. In the second window, run the command `yarn start`. This will begin your frontend instance.
4. A browser window should appear, but if it does not open one and navigate to `localhost:3000`
5. You should be greeted with the landing page and can now interact with the application.

## API Documentation

Feel free to send a POST request to the API endpoint using your web application, Postman, or similar API handling service. The API endpoint is located at `https://qpe.onrender.com/parse` and the payload you send should be in JSON format following the below convention:

```
{
    "inputQuery": "SELECT 1",
    "path": 1
}
```

Where `inputQuery` is your SQL statement, and `path` is the result you would like to receive (`1` for the JSON abstract syntax tree, `2` for the English paraphrases). The return expected from the above request is:

```
{
    "dict": {
        "Distinct": false,
        "From": {
            "joinvalue": [],
            "relname": []
        },
        "Group": {
            "groups": []
        },
        "Having": {
            "conditions": []
        },
        "Limit": "Unlimited results",
        "Select": {
            "targets": [
                [
                    "VALUE",
                    "1"
                ]
            ]
        },
        "Where": {
            "conditions": []
        }
    },
    "output": "A total of 0 tables were used in this query.\n\nThe following values were included in the result set: 1.\n\nThe number of returned results was unlimited."
}
```

`dict` will be returned in both paths `1` and `2` and contains a simplified dictionary of values representing the relations, projections, and other attributes. `output` will return either the JSON abstract parse tree with new line indicators for formatting purposes (when `path = 1`) or the English paraphrases (when `path = 2`).