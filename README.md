# 🧠 Apache Jira → JSONL Dataset Pipeline

This project scrapes public **Apache Jira issues** (e.g., Kafka, Hadoop, Spark, HBase) and converts them into a structured **JSONL dataset** suitable for **Large Language Model (LLM) training**.

It provides an end-to-end data pipeline — from scraping raw issues to producing preprocessed, clean JSONL and CSV datasets.

---

## 🚀 Features
- Scrapes public Jira issues from Apache projects  
- Cleans and structures issue data (title, description, comments, etc.)  
- Converts data into LLM-friendly JSONL format  
- Includes preprocessing and transformation utilities  
- Ready-to-train datasets for NLP/LLM use cases  

---

## ⚙️ Setup

### 1️⃣ Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🕸️ Step 1: Scrape Apache Jira Issues
Run the scraper for one or more projects:
```bash
python scraper/scraper_api.py --project KAFKA
```
You can replace `KAFKA` with any Apache project (e.g., `HDFS`, `SPARK`, `HBASE`, etc.)

**Output:**
```
scraper/sample_output/<PROJECT>_raw.jsonl
```

---

## 🧩 Step 2: Transform Raw Data into Structured Format
Convert raw JSONL into structured JSONL with summaries and QA pairs:
```bash
python scraper/transform_to_jsonl.py --project KAFKA
```

**Output:**
```
scraper/sample_output/KAFKA_processed.jsonl
```

---

## 🧼 Step 3: Preprocess and Clean Data
Clean and format the transformed data for LLM use:
```bash
python preprocess.py --input scraper/sample_output/KAFKA_processed.jsonl --output data/KAFKA_preprocessed.jsonl
```

**Output:**
```
data/KAFKA_preprocessed.jsonl  
data/KAFKA_preprocessed.csv
```

✅ This step generates the final dataset ready for analysis or LLM fine-tuning.

---

## 🧪 (Optional) Step 4: Run Full Demo Pipeline
You can run the complete demo script which executes scraping and transformation automatically:
```bash
bash run_demo.sh
```

---

## 📁 Project Structure
```
jira-llm-dataset/
├── scraper/
│   ├── scraper_api.py
│   ├── transform_to_jsonl.py
│   └── sample_output/
│       ├── KAFKA_raw.jsonl
│       ├── KAFKA_processed.jsonl
│       └── ...
├── data/
│   ├── KAFKA_preprocessed.jsonl
│   └── KAFKA_preprocessed.csv
├── preprocess.py
├── requirements.txt
├── run_demo.sh
└── README.md
```

---

## 🧾 Example Output (Snippet)
```json
{
  "id": "KAFKA-10006",
  "title": "Streams should not attempt to create internal topics that may exist",
  "status": "Resolved",
  "priority": "Major",
  "reporter": "A. Sophie Blee-Goldman",
  "description": "During assignment, Streams will attempt to validate all internal topics and their number of partitions...",
  "derived_summary": "During assignment, Streams will attempt to validate all internal topics and their number of partitions.",
  "derived_qas": [
    {
      "q": "What is the main issue?",
      "a": "Streams will attempt to create internal topics that already exist"
    }
  ]
}
```

---

## 🧠 Use Case
The resulting dataset can be used for:
- Fine-tuning LLMs for **issue summarization**
- **Bug report classification** or **QA generation**
- Building **developer assistants** for open-source projects

---

## 🛠️ Tools & Technologies Used
- **Python** – Core scripting and automation  
- **Requests / BeautifulSoup** – Data scraping  
- **Pandas** – Data cleaning and processing  
- **JSON / CSV** – Dataset formats  
- **Virtualenv** – Environment isolation  
- **Bash** – Automation script (`run_demo.sh`)  

---

## 🎯 Learning Outcomes
- Learned how to scrape real-world software issue data from APIs  
- Understood data cleaning and preprocessing for NLP tasks  
- Gained hands-on experience in building an automated data pipeline  
- Prepared datasets suitable for machine learning model fine-tuning  

---

## 🐳 Docker Setup for Jira LLM Dataset

### 🧩 Pull the Prebuilt Docker Image
docker pull adityasinghio/jira-llm-dataset

### 🚀 Step 1: Run the Project Inside the Container
docker run -it adityasinghio/jira-llm-dataset

### 💾 (Optional) Step 2: Persist Output Files to Your Local Machine
This mounts your local "outputs" folder to the container’s /app/sample_output directory.
docker run -it -v $(pwd)/outputs:/app/sample_output adityasinghio/jira-llm-dataset

### 📂 Step 3: Check the Saved Outputs Locally
ls outputs/

### 🏗️ (For Developers) Step 4: Build the Docker Image Yourself
docker build -t jira-llm-dataset .

---

## 👤 Author
**Aditya Singh**  
Final Year B.Tech CSE Student | DevOps & Cloud Enthusiast  

🔗 **Docker Hub:** [adityasingh1404/jira-llm-dataset](https://hub.docker.com/r/adityasinghio/jira-llm-datasett)

