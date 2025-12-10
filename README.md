verview

The Safe Code Executor is a simple and secure Python code execution system built using Flask and Docker.
In this project, the user sends Python code to an API, and the code is executed inside a Docker container with restricted resources.

This setup prevents harmful or unexpected scripts from crashing the host system.
The main purpose of the project is to learn how to handle untrusted code safely using Docker isolation techniques.

Setup Instructions
1. Create Project Folder

I created a new folder manually named:

safe-code-executor


All my project files such as app.py, Dockerfile, and test scripts were placed inside this folder.

2. Install Required Software

Before starting the project, I installed:

Python 3.10 or above

Docker Desktop

Visual Studio Code

WSL2 (for Windows users)

These tools are required for running Docker containers and building the Flask API.

3. Install Python Dependencies

Inside the project folder, I installed Flask using:

pip install flask

4. Run the Flask API

Once everything was ready, I started the API:

python app.py


This enables the /run endpoint that executes Python code safely.

5. Test the API Using Postman

URL:

http://localhost:5000/run


Body (JSON):

{ "code": "print('Hello World')" }

<img width="1355" height="767" alt="image" src="https://github.com/user-attachments/assets/56d23b3a-6c5f-4740-a530-8a3f19404ee2" />

Expected Output:

Hello World





This confirmed that the API and Docker execution were working correctly.

Security Features Implemented

To protect the system, I implemented several Docker security measures.

1. Timeout Limit (10 seconds)

Prevents infinite loops such as:

while True:
    pass


The container automatically stops after the timeout.

<img width="902" height="685" alt="image" src="https://github.com/user-attachments/assets/74f8d19f-eacf-4922-92c0-9a15f7839ed8" />


2. Memory Restriction (128 MB)

Blocks programs that consume excessive memory, for example:

x = "a" * 1000000000

<img width="795" height="523" alt="image" src="https://github.com/user-attachments/assets/095597e7-b2bb-49e7-9b0e-33325a2be263" />

<img width="1126" height="225" alt="image" src="https://github.com/user-attachments/assets/c0155813-e727-41db-9cbd-ebebde1fd2b5" />

When I tested memory-heavy code, Docker automatically killed the container and returned exit code 137, which means the process was terminated because it exceeded the allowed memory limit.
This helped me understand how Docker protects the system by force-stopping programs before they crash or overload the server.


The container stops before the system crashes.

3. Network Disabled

Prevents scripts from making network requests:

import requests
requests.get("http://example.com")

<img width="1920" height="1008" alt="Screenshot 2025-12-09 145237" src="https://github.com/user-attachments/assets/70542933-b562-41e1-9f17-a671e82e30c3" />

<img width="1116" height="734" alt="image" src="https://github.com/user-attachments/assets/42f0c131-114a-4b2a-98bb-aecefb0047ae" />

<img width="1031" height="466" alt="image" src="https://github.com/user-attachments/assets/0e9deb50-7026-4ce4-86ac-53d08f6395a1" />





This keeps the environment isolated from the internet.

4. Read-Only Filesystem

When enabled, this prevents the script from writing files inside the container.


5. Automatic Cleanup

Every container runs with --rm, which removes it after execution.
This keeps the system clean and avoids unnecessary storage usage.

easy -level
<img width="727" height="520" alt="image" src="https://github.com/user-attachments/assets/1091bc22-a389-4e95-9761-35616e9d78a7" />
<img width="727" height="520" alt="image" src="https://github.com/user-attachments/assets/c5eb00c7-cd0a-446a-9483-1d91cbf0cc5a" />

mid-level: i tested with the zip file the user will give the zip file by using the postman.
<img width="1039" height="526" alt="image" src="https://github.com/user-attachments/assets/8ad687d9-ca01-4fa4-9bde-71d7428994ea" />





What I Learned

While building this project, I learned several practical DevOps concepts and real security behaviors.

1. How Docker isolates processes

I understood that Docker provides a controlled environment where untrusted code can run safely without affecting the host system.

2. How to control resources

I implemented memory limits, timeouts, and CPU restrictions.
These helped me see how attacks like infinite loops and memory overflows can be stopped safely.

3. How to block network access

By disabling network access, I saw how dangerous scripts trying to access external URLs were immediately blocked.

4. Difference between container filesystem and host filesystem

I noticed that even though a script can read from /etc/passwd, it is reading the container’s file, not the host’s.
This helped me understand what Docker can and cannot protect.

5. How to integrate Docker with Flask

I learned how to make Flask run external Docker commands, capture output, and return that output to the user in a clean JSON response.

6. How to test and debug using Postman

I noticed how each scenario—normal code, infinite loop, memory attack, file write—behaves differently and how the API responds in each case.

7. Importance of secure code execution

This project helped me understand why running user code directly on the host machine is dangerous and how Docker solves that problem using isolation.
