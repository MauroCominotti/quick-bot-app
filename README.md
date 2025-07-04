# 🚀 Quickbot

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![Code Style: Google](https://img.shields.io/badge/code%20style-google-blueviolet.svg)](https://github.com/google/gts)

Quickbot is an innovative, out-of-the-box solution enabling users to deploy sophisticated AI Agents as full-stack cloud applications on their own Google Cloud Platform (GCP) accounts, entirely without requiring any coding expertise. It empowers you to seamlessly integrate and customize Google's latest AI models and protocols through intuitive templates.

## Our Mission
To democratize Agentic AI application deployment. We provide a seamless, one-click style solution that installs fully functional and visually engaging Agentic AI applications (encompassing both backend and frontend infrastructure, leveraging diverse templates) into your own GCP account. This process is designed to be completed quickly.

Quickbot addresses the challenge users face in independently building and deploying custom AI Agents as full-stack cloud applications within their own GCP environments simply and directly. We believe users want to **own the code** in their GCP accounts and **customize it as needed**.

## Features

* **Preset Templates:** Quickly create custom agents with ready-to-use options.
* **Fast Deployment:** Get sophisticated AI applications running in your GCP account in under 10 minutes.
* **Customizable Codebase:** Full access to the open-source code (Angular frontend, Python FastAPI backend) for direct interaction and modification.
* **Cloud Run Deployment:** Each template can be deployed as an independent application on Google Cloud Run.
* **Standardized Architecture:** Every agent template includes an Angular frontend and a FastAPI Python backend, ensuring a consistent development experience.
* **Google Cloud Authentication:** Uses your default Google Cloud credentials for seamless integration.
* **Scalable Resources:** Deploys necessary Google Cloud resources based on each template's complexity.
* **Latest AI Integration:** Easily leverage Google's cutting-edge AI models and protocols (e.g., Gemini, Imagen, Agent Builder).
* **Diverse Template Ecosystem:** Utilizes a variety of Agentic Templates, including our own and inspirations from others like Agent Garden, A2A, etc.

## Architecture

Quickbot templates follow a standard and straightforward architecture:

* `frontend/`: Contains the Angular application that provides the user interface.
* `backend/`: Contains the FastAPI (Python) application that powers the agent's logic and interacts with Google Cloud services.

This separation allows for clear development workflows and independent scaling of frontend and backend services.

## Available Templates

Quickbot provides a growing set of pre-built templates:

* **ADK Travel Concierge Template (Coming Soon):** Leveraging the [ADK](https://google.github.io/adk-docs/) + [Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) capabilities, this MultiAgent orchestrates personalized travel experiences and provides support throughout the user’s journey, from initial planning to real-time itinerary alerts.
* **Image Generation Template:** A custom AI Agent that integrates with Imagen for text-to-image generation.
* **LinkedIn Profile Image Generation Template:** A specialized AI Agent leveraging Imagen's latest features for image editing and recognition to help you create customized professional corporate profile photos.
* **Background Changer Image Generation Template:** An AI Agent using Imagen's image editing capabilities to customize your product, graphic, car, or pet images, generating professional catalog-style photos with new backgrounds.
* **Document Search Template:** An AI Agent that provides answers based on documents and information you provide beforehand. Integrated with Agent Builder, Cloud Storage, and Cloud Run.
* **Website Search Template:** An advanced AI Agent that learns from your website. Provide a URL, and it crawls your domain, extracts information, converts it to vectors stored in Vertex AI, and then generates answers based on a custom prompt, the vector database, and user questions.
* **Single Playbook Template:** Generates an AI Agent that detects specific intents (keywords) in user questions and responds with a corresponding specialized Chatbot, providing a tailored experience.
* **Multi Playbook Template:** An evolution of the Single Playbook, this agent detects intents and routes to one of several specialized Chatbots, offering a more nuanced and personalized experience for diverse user inquiries.

## Getting Started

Follow these general steps to get a Quickbot template running in your local environment.

### Prerequisites

1.  **Google Cloud Project:** You'll need a GCP project with billing enabled.
2.  **Google Cloud SDK (`gcloud`):** [Install and initialize the gcloud CLI](https://cloud.google.com/sdk/docs/install).
3.  **Node.js and npm:** We recommend using [nvm (Node Version Manager)](https://github.com/nvm-sh/nvm) to manage Node.js versions.
    * Install nvm, then install a compatible Node.js version (e.g., v18.x or later).
    * Install Angular CLI: `npm install -g @angular/cli@18` (or the version specified by the template).
4.  **Python:** Python 3.8+ and `pip` are required.
    * `sudo apt install python3 python3-pip` (Linux example)
5.  **Git:** For cloning the repository.
6.  **(Optional) Docker and docker-compose:** Useful for containerized development and deployment.

### Installation & Running a Template
Every template has their own README.md with their considerations and particularities, but basically they all bootstrap in the same way:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/GoogleCloudPlatform/quickbot.git
    cd quickbot
    ```

2.  **Navigate to a Template Folder:**
    Each template resides in its own directory within the `quickbot/` folder. For example:
    ```bash
    cd quickbot/text-to-image-generation-template
    ```

3.  **Set Up the Backend:**
    * Navigate to the backend directory:
        ```bash
        cd backend
        ```
    * Create and activate a Python virtual environment:
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```
        *(For Windows: `.\.venv\Scripts\activate`)*
    * Install dependencies:
        ```bash
        pip3 install -r requirements.txt
        ```
    * **Authenticate with Google Cloud:**
        ```bash
        gcloud auth login
        gcloud config set project YOUR_PROJECT_ID
        # Grant application default credentials access to your project for quota and billing
        gcloud auth application-default set-quota-project YOUR_PROJECT_ID
        ```
        Replace `YOUR_PROJECT_ID` with your actual Google Cloud Project ID.
    * **Environment Variables:**
        Many templates require environment variables (e.g., API keys, project settings). These are typically managed in a `.local.env` file in the `backend/` directory. Create this file if it doesn't exist, based on any provided `.env.example` or documentation.
        To load them (on Mac/Linux with bash/zsh):
        ```bash
        . ./local.env
        ```
        Or, for Linux, you might add them to your `activate` script within the virtual environment.
    * **Run Setup Script (if applicable):**
        Some templates may have a `setup.py` script to provision necessary cloud resources.
        ```bash
        python3 setup.py
        ```
    * **Run the Backend Application:**
        ```bash
        uvicorn main:app --reload --port 8080
        ```
        The backend API documentation (Swagger UI) will typically be available at `http://localhost:8080/docs`.

4.  **Set Up the Frontend:**
    * Navigate to the frontend directory (from the template's root):
        ```bash
        cd ../frontend
        ```
    * Install dependencies:
        ```bash
        npm install
        ```
    * **Configure Environment (if needed):**
        Frontend configurations, like backend URLs or Firebase settings, are usually in `src/environments/environment.ts` and `src/environments/environment.prod.ts`.
    * **Run the Frontend Application:**
        ```bash
        npm start
        ```
        The frontend application will typically be available at `http://localhost:4200`.

## Authentication

Quickbot templates can be integrated with **Firebase Authentication** for user sign-up, sign-in, and management. Configuration details for Firebase are typically found in the frontend's `src/environments/environment.ts` file. You can use existing Firebase projects or set up new ones to connect with your deployed agents.

## Code Styling & Commit Guidelines

To maintain code quality and consistency:

* **TypeScript (Frontend):** We follow [Angular Coding Style Guide](https://angular.dev/style-guide) by leveraging the use of [Google's TypeScript Style Guide](https://github.com/google/gts) using `gts`. This includes a formatter, linter, and automatic code fixer.
* **Python (Backend):** We adhere to the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), using tools like `pylint` and `black` for linting and formatting.
* **Commit Messages:** We suggest following [Angular's Commit Message Guidelines](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md) to create clear and descriptive commit messages.

#### Frontend (TypeScript with `gts`)

1.  **Initialize `gts` (if not already done in the project):**
    Navigate to the `frontend/` directory and run:
    ```bash
    npx gts init
    ```
    This will set up `gts` and create necessary configuration files (like `tsconfig.json`). Ensure your `tsconfig.json` (or a related gts config file like `.gtsrc`) includes an extension for `gts` defaults, typically:
    ```json
    {
      "extends": "./node_modules/gts/tsconfig-google.json",
      // ... other configurations
    }
    ```
2.  **Check for linting issues:**
    ```bash
    npm run lint
    ```
    (This assumes a `lint` script is defined in `package.json`, e.g., `"lint": "gts lint"`)
3.  **Fix linting issues automatically (where possible):**
    ```bash
    npm run fix
    ```
    (This assumes a `fix` script is defined in `package.json`, e.g., `"fix": "gts fix"`)

#### Backend (Python with `pylint` and `black`)

1.  **Ensure Dependencies are Installed:**
    Add `pylint` and `black` to your `backend/requirements.txt` file:
    ```
    pylint
    black
    ```
    Then install them within your virtual environment:
    ```bash
    pip install pylint black
    # or pip install -r requirements.txt
    ```
2.  **Configure `pylint`:**
    It's recommended to have a `.pylintrc` file in your `backend/` directory to configure `pylint` rules. You might need to copy a standard one or generate one (`pylint --generate-rcfile > .pylintrc`).
3.  **Check for linting issues with `pylint`:**
    Navigate to the `backend/` directory and run:
    ```bash
    pylint .
    ```
    (Or specify modules/packages: `pylint your_module_name`)
4.  **Format code with `black`:**
    To automatically format all Python files in the current directory and subdirectories:
    ```bash
    python -m black . --line-length=80
    ```

## Contributing

We welcome contributions to Quickbot! Whether it's new templates, features, bug fixes, or documentation improvements, your help is valued.

### Prerequisites for Contributing

* A **GitHub Account**.
* **2-Factor Authentication (2FA)** enabled on your GitHub account.
* Familiarity with the "Getting Started" section to set up your development environment.

### Branching Model

We follow the [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) branching model. Please create feature branches from `dev` and submit pull requests back to `dev`.

For more detailed contribution guidelines, please refer to the `CONTRIBUTING.md` file.

## Feedback

* **Found an issue or have a suggestion?** Please [raise an issue](https://github.com/GoogleCloudPlatform/quickbot/issues) on our GitHub repository.
* **Share your experience!** We'd love to hear about how you're using Quickbot or any success stories. Feel free to reach out to us at quick-bot-team@google.com or discuss in the GitHub discussions.

## Contributors

[Robby Singh](mailto:robbysingh@google.com): Project Lead

[Mauro Cominotti](mailto:maurocominotti@google.com): Project Manager | Tech Lead

[Manuel Correa Freisztav](mailto:manucf@google.com): AI Engineer

[Tomasz Świtoń](mailto:switon@google.com): AI Engineer

[San Srinivasan](mailto:sansrinivasan@google.com): Infra Engineer

[Agnieszka Kołkiewicz](mailto:akolkiewicz@google.com): Product Manager

# Relevant Terms of Service

[Google Cloud Platform TOS](https://cloud.google.com/terms)

[Google Cloud Privacy Notice](https://cloud.google.com/terms/cloud-privacy-notice)

# Responsible Use

Building and deploying generative AI agents requires a commitment to responsible development practices. Quickbot provides to you the tools to build agents, but you must also provide the commitment to ethical and fair use of these agents. We encourage you to:

*   **Start with a Risk Assessment:** Before deploying your agent, identify potential risks related to bias, privacy, safety, and accuracy.
*   **Implement Monitoring and Evaluation:** Continuously monitor your agent's performance and gather user feedback.
*   **Iterate and Improve:**  Use monitoring data and user feedback to identify areas for improvement and update your agent's prompts and configuration.
*   **Stay Informed:**  The field of AI ethics is constantly evolving. Stay up-to-date on best practices and emerging guidelines.
*   **Document Your Process:**  Maintain detailed records of your development process, including data sources, models, configurations, and mitigation strategies.

# Disclaimer

**This is not an officially supported Google product.**

Copyright 2025 Google LLC. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.