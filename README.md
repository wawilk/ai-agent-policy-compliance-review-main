# AI Agent Policy Compliance Review

Placeholder

## Overview

Placeholder

## Prerequisites

- Python 3.10 or later
- Visual Studio Code
- An Azure AI Services resource with an Azure OpenAI o3-mini deployment

## Setup

1. **Clone the Repository**

   ```sh
   git clone https://github.com/Kthwaits/ai-agent-policy-compliance-review
   cd ai-agent-policy-compliance-review

2. **Populate environment variables**

    Rename  ```sample.env``` to  ```.env ``` update the placeholder values.

3. **Install requirements**

    ```sh
    pip install -r requirements.txt
    
4. **Copy your policy documents to the /data directory**

    In future versions of this project, documents will be able to be fetched from a remote source. For demo/testing purposes, this project expects policy documents (both the underlier and master) to be present in the project's ```/data``` folder.
    
 5. **Run the agent**
 
    ```
    python main.py 'underlier.pdf' 'master.pdf'
    ```
   
    Substitute the placeholder names with the name of policy documents located in your /data folder. Note that the single quotes (' ') around each file name are required and the underlier and master policy are expected to be passed in that order. 